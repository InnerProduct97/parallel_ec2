import time

import boto3
from fabric import Connection

ec2_client = boto3.client('ec2', region_name="us-east-1")


def check_instance_state(instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    state = response['Reservations'][0]['Instances'][0]['State']['Name']
    return state


def create_worker_instance(instance_name, pem_key_path, bash_script_path, python_script_path):
    # Create EC2 instance

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
    response = ec2_client.run_instances(
        ImageId="ami-0dba2cb6798deb6d8",  # Replace with the appropriate AMI ID
        InstanceType='t2.micro',  # Replace with the desired instance type
        MinCount=1,
        MaxCount=1,
        KeyName='WorkerInstanceKeyPairs',  # Replace with the name of your PEM key
        SecurityGroupIds=[security_group_id],
        UserData=f'''#!/bin/bash
        sudo apt-get update
        sudo apt-get install -y python3
        ''',
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f"Created EC2 instance with ID: {instance_id}")
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

        while True:
            state = check_instance_state(instance_id)
            if state == "running":
                break
            time.sleep(1)

        # Get the public IP address of the instance
        ec2_resource = boto3.resource('ec2')
        instance = ec2_resource.Instance(instance_id)
        instance_public_ip = instance.public_ip_address
        print("SSH into EC2 Instance Begin")

        while True:
            try:
                conn = Connection(host=instance_public_ip, user='ubuntu', connect_kwargs={'key_filename': pem_key_path})

                # Copy Bash script and Python script to the instance
                conn.put(bash_script_path, '/home/ubuntu/bash_script.sh')
                conn.put(python_script_path, '/home/ubuntu/main.py')

                # Run the Bash script on the instance
                result = conn.run('bash /home/ubuntu/bash_script.sh', hide=True)
                print(result.stdout)

                # Close the SSH connection
                conn.close()
                break
            except Exception as err:
                print("Exception Occurred, Trying Again")
                time.sleep(1)
                continue

    except Exception as err:
        print(err)
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        raise Exception("Something Went Wrong")

    return instance_id


create_worker_instance("WorkerInstance", "./static/WorkerInstanceKeyPairs.pem", "./static/set_cron_job.sh", "./worker_function.py")