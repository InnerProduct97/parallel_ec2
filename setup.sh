#!/bin/bash

# This scripts creates IAM role, security group and creates EC2 with these resources.
# Set your desired region and role details
region="us-east-1"
role_name="EC2FullAccess"
policy_name="EC2FullAccess-policy"
iam_description="Web Server IAM role Created with AWS CLI"

# Set your desired region, instance details, IAM role, and security group
instance_type="t2.micro"
ami_id="ami-0dba2cb6798deb6d8" # Ubuntu 20.04 LTS
key_name="WebServer_Security_PemKEY"
worker_key_name="WorkerInstanceKeyPairUpdated"
instance_name="WebServer"
instance2_name="WebServer2"
deploy_script="deploy.sh"

# Set your desired region and security group details
security_group_name="web_server_sg"
description="Allows SSH, HTTP and HTTPS"


# Create the IAM role
echo "Creating IAM role..."
role_arn=$(aws iam create-role \
  --region $region \
  --role-name $role_name \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --description "$iam_description" \
  --output text \
  --query 'Role.Arn')

echo "IAM role created with ARN: $role_arn"

# Create the IAM policy
echo "Creating IAM policy..."
policy_arn=$(aws iam create-policy \
  --region $region \
  --policy-name $policy_name \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"ec2:*","Resource":"*"}]}' \
  --output text \
  --query 'Policy.Arn')

echo "IAM policy created with ARN: $policy_arn"

# Attach the policy to the role
echo "Attaching policy to IAM role..."
aws iam attach-role-policy \
  --region $region \
  --role-name $role_name \
  --policy-arn $policy_arn

echo "Policy attached to IAM role"

# Create the instance profile
echo "Creating instance profile..."
instance_profile_arn=$(aws iam create-instance-profile \
  --region $region \
  --instance-profile-name $role_name \
  --output text \
  --query 'InstanceProfile.Arn')

echo "Instance profile created with ARN: $instance_profile_arn"

# Add the IAM role to the instance profile
echo "Adding IAM role to instance profile..."
aws iam add-role-to-instance-profile \
  --region $region \
  --instance-profile-name $role_name \
  --role-name $role_name

echo "IAM role added to instance profile"

# Create the security group
echo "Creating security group..."
security_group_id=$(aws ec2 create-security-group \
  --region $region \
  --group-name $security_group_name \
  --description "$description" \
  --output text \
  --query 'GroupId')

echo "Security group created with ID: $security_group_id"

# Allow SSH access to the security group
echo "Allowing SSH access to security group..."
aws ec2 authorize-security-group-ingress \
  --region $region \
  --group-id $security_group_id \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTPS access to the security group
echo "Allowing HTTPS access to security group..."
aws ec2 authorize-security-group-ingress \
  --region $region \
  --group-id $security_group_id \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow HTTP access to the security group
echo "Allowing HTTP access to security group..."
aws ec2 authorize-security-group-ingress \
  --region $region \
  --group-id $security_group_id \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

echo "Security group created with ID: $security_group_id"

# EC2 instance
# Download the PEM key
echo "Downloading PEM key..."
aws ec2 create-key-pair \
  --region $region \
  --key-name $key_name \
  --query 'KeyMaterial' \
  --output text > $key_name.pem

echo "PEM key downloaded to $key_name.pem"
chmod 400 $key_name.pem


echo "Downloading PEM key For Worker Instance..."
aws ec2 create-key-pair \
  --region $region \
  --key-name $worker_key_name \
  --query 'KeyMaterial' \
  --output text > $worker_key_name.pem

echo "PEM key downloaded to $worker_key_name.pem"
chmod 400 $worker_key_name.pem
sleep 5

# Create the EC2 instance
echo "Creating EC2 instance..."
instance_id=$(aws ec2 run-instances \
  --region $region \
  --image-id $ami_id \
  --instance-type $instance_type \
  --key-name $key_name \
  --security-group-ids $security_group_id \
  --iam-instance-profile Name=$role_name \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value='$instance_name'}]' \
  --output text \
  --query 'Instances[0].InstanceId')

echo "EC2 instance created with ID: $instance_id"

# Create the EC2 instance
echo "Creating Second EC2 instance..."
instance_id2=$(aws ec2 run-instances \
  --region $region \
  --image-id $ami_id \
  --instance-type $instance_type \
  --key-name $key_name \
  --security-group-ids $security_group_id \
  --iam-instance-profile Name=$role_name \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value='$instance2_name'}]' \
  --output text \
  --query 'Instances[0].InstanceId')

echo "EC2 instance created with ID: $instance_id2"

# Wait for the instance to start up
echo "Waiting for instances to start up..."
aws ec2 wait instance-status-ok --instance-ids $instance_id --region $region
aws ec2 wait instance-status-ok --instance-ids $instance_id2 --region $region


# Allocate an Elastic IP
echo "Allocating Elastic IP..."
allocation_id=$(aws ec2 allocate-address \
  --region $region \
  --domain vpc \
  --output text \
  --query 'AllocationId')

echo "Elastic IP allocated with ID: $allocation_id"

# Associate the Elastic IP with the instance
echo "Associating Elastic IP with instance..."
aws ec2 associate-address \
  --region $region \
  --instance-id $instance_id \
  --allocation-id $allocation_id

echo "Elastic IP address created and associated with instance"


# Allocate an Elastic IP for Second Instance
echo "Allocating Elastic IP..."
allocation_id2=$(aws ec2 allocate-address \
  --region $region \
  --domain vpc \
  --output text \
  --query 'AllocationId')

echo "Elastic IP allocated with ID: $allocation_id2"

# Associate the Elastic IP with the instance
echo "Associating Elastic IP with instance..."
aws ec2 associate-address \
  --region $region \
  --instance-id $instance_id2 \
  --allocation-id $allocation_id2

echo "Elastic IP address created and associated with instance"


# Get the public IP address of the instance
public_ip=$(aws ec2 describe-instances \
  --region $region \
  --instance-ids $instance_id \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Instance IP address: $public_ip"


# Get the public IP address of the instance
public_ip2=$(aws ec2 describe-instances \
  --region $region \
  --instance-ids $instance_id2 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Instance IP address: $public_ip2"

# Copy the deploy script to the instance
echo "Copying deploy script to instance..."
scp -i $key_name.pem -o StrictHostKeyChecking=no $deploy_script ubuntu@$public_ip:~/
scp -i $key_name.pem -o StrictHostKeyChecking=no $worker_key_name.pem ubuntu@$public_ip:~/

# Run the deploy script on the instance
echo "Running deploy script on instance..."
ssh -i $key_name.pem -o StrictHostKeyChecking=no -o ServerAliveInterval=60 ubuntu@$public_ip "./$deploy_script"

# Copy the deploy script to the instance
echo "Copying deploy script to instance..."
scp -i $key_name.pem -o StrictHostKeyChecking=no $deploy_script ubuntu@$public_ip2:~/
scp -i $key_name.pem -o StrictHostKeyChecking=no $worker_key_name.pem ubuntu@$public_ip2:~/

# Run the deploy script on the instance
echo "Running deploy script on instance..."
ssh -i $key_name.pem -o StrictHostKeyChecking=no -o ServerAliveInterval=60 ubuntu@$public_ip2 "./$deploy_script"
