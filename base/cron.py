from .models import Item, Instance
from .create_worker_instance import create_worker_instance, is_there_pending_instances
from random import randint
from datetime import timedelta
from django.utils import timezone
from .mixins import *
import boto3
import logging
import fcntl
import os


logging.basicConfig(
    level=logging.INFO,
    filename='/home/ubuntu/cron_logs.log',
    format='%(asctime)s [%(levelname)s] %(message)s'
)

lockfile_path = '/home/ubuntu/lockfile.lock'
lockfile2_path = '/home/ubuntu/lockfile2.lock'


def assign_instance_items():
    if os.path.isfile(lockfile_path):
        print("Another instance of the cron job is already running. Exiting.")
        return
    # Create the lock file
    lockfile = open(lockfile_path, 'w')
    try:
        # Try acquiring an exclusive lock on the file
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        items = Item.objects.filter(instance=None)
        if items.exists():
            for item in items:
                print(f"Item is {item}")
                instances = Instance.objects.all()
                # Check Which Instance have minimum assigned tasks
                instance = Instance.get_instance_with_minimum_assigned_items()
                if instance and instance.assigned_items_count < 5:
                    print(f"Assigning to existed Instance {instance.instance_id}")
                    item.instance = instance

                else:
                    if instances.count() < 5:
                        print("Creating New Instance")
                        # Create an Instance
                        instance_name = f"WorkerInstance{randint(1, 19999)}"
                        pem_key_path = "/home/ubuntu/WorkerInstanceKeyPairUpdated.pem"
                        bash_script = "/var/www/parallel_ec2//static/set_cron_job.sh"
                        python_script = "/var/www/parallel_ec2/worker_function.py"

                        logging.info('Creating Worker Instance')
                        if is_there_pending_instances():
                            logging.info('Some Worker Instance Is being Ready.')
                            logging.info('Quiting...')
                            return False

                        instance_id = create_worker_instance(instance_name, pem_key_path, bash_script, python_script)

                        logging.info('Worker Instance Created Successfully')

                        # Save Data to DB
                        instance = Instance.objects.create(instance_id=instance_id)
                        instance.save()
                        create_instance(instance_id=instance_id)
                        item.instance = instance
                update_item(item_id=item.id, instance=item.instance)
                item.save()
        for item in Item.objects.all():
            logging.info(f"Item {item.id} is associated with Instance {item.instance.instance_id}")
        # Release the lock
        fcntl.flock(lockfile, fcntl.LOCK_UN)
    finally:
        # Close and remove the lock file
        lockfile.close()
        os.remove(lockfile_path)


def remove_idle_instances():
    if os.path.isfile(lockfile2_path):
        print("Another instance of the cron job is already running. Exiting.")
        return
    # Create the lock file
    lockfile = open(lockfile2_path, 'w')
    try:
        # Try acquiring an exclusive lock on the file
        fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        threshold_time = timezone.now() - timedelta(minutes=5)

        # Retrieve instances that have not been assigned any items for 5 minutes
        instances_to_delete = Instance.objects.filter(assigned_items__isnull=True, updated_at__lt=threshold_time)

        if instances_to_delete.exists():
            for instance in instances_to_delete:
                # Create an EC2 client
                ec2_client = boto3.client('ec2', region_name="us-east-1")

                # Terminate the EC2 instance
                response = ec2_client.terminate_instances(InstanceIds=[instance.instance_id])

                # Check if termination was successful
                if response['TerminatingInstances'][0]['CurrentState']['Name'] == 'shutting-down':
                    logging.info(f"EC2 instance {instance.instance_id} is being terminated.")
                else:
                    logging.info(f"Failed to terminate EC2 instance {instance.instance_id}.")

                # Delete the instance Object
                delete_instance(instance_id=instance.instance_id)
                instance.delete()
        # Release the lock
        fcntl.flock(lockfile, fcntl.LOCK_UN)
    finally:
        # Close and remove the lock file
        lockfile.close()
        os.remove(lockfile2_path)


