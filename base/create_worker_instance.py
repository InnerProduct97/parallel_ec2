import boto3
from django.conf import settings
from fabric import Connection
from time import sleep
import logging


logging.basicConfig(
    level=logging.INFO,
    filename='/home/ubuntu/cron_logs.log',
    format='%(asctime)s [%(levelname)s] %(message)s'
)


python_file_code = f"""

import requests
import logging


logging.basicConfig(
    level=logging.INFO,
    filename='/home/ubuntu/cron_logs.log',
    format='%(asctime)s [%(levelname)s] %(message)s'
)

base_url = "{settings.BASE_URL}/admin/"
base_url2 = "{settings.THIS_INSTANCE_URL}/admin/"


""" + """

def list_item():
    url = base_url + 'items'
    response = requests.get(url)
    return response.json()


def delete_item(item_id, **kwargs):
    url = base_url + 'items/' + str(item_id)
    response = requests.delete(url)
    logging.info(f'Sending Delete Request to {url} and got the response {response}')
    url = base_url2 + 'items/' + str(item_id)
    logging.info(f'Sending Delete Request to {url} and got the response {response}')
    response = requests.delete(url)


def work(buffer, iterations):
    import hashlib
    output = hashlib.sha512(buffer.encode()).digest()
    for i in range(iterations-1):
        output = hashlib.sha512(output).digest()
    return output

def update_instance(instance_id):
    url = base_url + 'instances/' + instance_id
    requests.put(url, data={"instance_id": instance_id})
    url = base_url2 + 'instances/' + instance_id
    requests.put(url, data={"instance_id": instance_id})


def add_completed(**kwargs):
    url = base_url + 'completed'
    data = {**kwargs}
    response = requests.post(url, data=data)
    url = base_url2 + 'completed'
    response = requests.post(url, data=data)
    return True


def main():
    items = list_item()
    logging.info(f'Items are {items}')
    for item in items:
        # Retrieve the current instance ID
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
        current_instance_id = response.text
        # get the items for current instance
        if item.get("instance") == current_instance_id:
            # complete the given work
            logging.info(f'working on item {item}')
            output = work(buffer=item.get("buffer"), iterations=item.get("iterations"))
            # Make it complete on Other instances.
            delete_item(item_id=item.get("id"))
            logging.info(f'Work Completed, Adding to Complete Table')
            add_completed(output=output)
            update_instance(current_instance_id)
main()
"""

with open("/var/www/parallel_ec2/worker_function.py", 'w') as python_file:
    python_file.write(python_file_code)


def create_worker_instance(instance_name, pem_key_path, bash_script_path, python_script_path):
    # Create EC2 instance
    ec2_client = boto3.client('ec2', region_name="us-east-1")

    # Check if security group already exists
    response = ec2_client.describe_security_groups(
        Filters=[
            {'Name': 'group-name', 'Values': ['SSHAccess']}
        ]
    )

    if len(response['SecurityGroups']) > 0:
        # Security group already exists, get its ID
        security_group_id = response['SecurityGroups'][0]['GroupId']
    else:
        # Security group doesn't exist, create it
        security_group = ec2_client.create_security_group(
            Description='SSH Access',
            GroupName='SSHAccess',
        )

        security_group_id = security_group['GroupId']
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                },
            ],
        )

    # Launch EC2 instance
    if is_there_pending_instances():
        logging.info('Some Worker Instance Is being Ready.')
        logging.info('Quiting...')
        return False
    response = ec2_client.run_instances(
        ImageId="ami-0dba2cb6798deb6d8",  # Replace with the appropriate AMI ID
        InstanceType='t2.micro',  # Replace with the desired instance type
        MinCount=1,
        MaxCount=1,
        KeyName='WorkerInstanceKeyPairUpdated',  # Replace with the name of your PEM key
        SecurityGroupIds=[security_group_id],
        UserData=f'''#!/bin/bash
        sudo apt-get update
        sudo apt-get install -y python3
        ''',
    )
    instance_id = response['Instances'][0]['InstanceId']
    logging.info(f"Created EC2 instance with ID: {instance_id}")
    try:
        ec2_client.create_tags(
            Resources=[instance_id],
            Tags=[
                {'Key': 'Name', 'Value': instance_name},
            ],
        )
        # Wait for the instance to be in the 'running' state
        ec2_waiter = ec2_client.get_waiter('instance_running')
        ec2_waiter.wait(InstanceIds=[instance_id])

        # Get the public IP address of the instance
        ec2_resource = boto3.resource('ec2', region_name="us-east-1")
        instance = ec2_resource.Instance(instance_id)
        instance_public_ip = instance.public_ip_address
        logging.info("SSH into EC2 Instance Begin")

        # Establish SSH connection to the instance
        while True:
            try:
                conn = Connection(host=instance_public_ip, user='ubuntu', connect_kwargs={'key_filename': pem_key_path})

                # Copy Bash script and Python script to the instance
                conn.put(bash_script_path, '/home/ubuntu/bash_script.sh')
                conn.put(python_script_path, '/home/ubuntu/main.py')

                # Run the Bash script on the instance
                result = conn.run('bash /home/ubuntu/bash_script.sh', hide=True)
                logging.info(result.stdout)

                # Close the SSH connection
                conn.close()
                break
            except Exception as err:
                logging.info("Exception Occurred, Trying Again")
                sleep(1)
                continue

    except Exception as err:
        logging.info(err)
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        raise Exception("Something Went Wrong")

    return instance_id


def is_there_pending_instances():
    ec2_client = boto3.client('ec2', region_name='us-east-1')  # Replace with your region
    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['WorkerInstance*']},
            {'Name': 'instance-state-name', 'Values': ['pending']}
        ]
    )
    instances = response['Reservations']

    if instances:
        return True
    else:
        return False

