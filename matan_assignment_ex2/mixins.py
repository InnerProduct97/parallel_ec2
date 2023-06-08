import boto3
import requests


def get_current_instance_public_url():
    # Retrieve the public IP address of the current instance
    response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
    public_ip = response.text

    # Construct the public URL using the public IP address
    public_url = f"http://{public_ip}"

    return public_url


def get_webserver_instance_url():
    # Retrieve the current instance ID
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    current_instance_id = response.text

    # Create an EC2 client
    ec2_client = boto3.client('ec2', region_name="us-east-1")

    # Retrieve the list of instances
    response = ec2_client.describe_instances(Filters=[
        {'Name': 'instance-state-name', 'Values': ['running', 'pending']},
        {'Name': 'tag:Name', 'Values': ['WebServer*']}
    ])

    # Extract the instance details
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            public_ip = instance.get('PublicIpAddress', 'N/A')
            if instance_id != current_instance_id:  # Exclude the current instance
                instances.append({'InstanceID': instance_id, 'PublicIP': public_ip})
    for instance in instances:
        base_url = f"http://{instance['PublicIP']}"

    return base_url
