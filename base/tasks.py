# tasks.py

from celery import shared_task
from .models import Item


@shared_task
def check_item_task():
    # Retrieve items without an instance attached
    items_without_instance = Item.objects.filter(instance=None)

    if items_without_instance.exists():
        # Run the task for items without instance attached
        for item in items_without_instance:
            print(item)
    # Perform your task logic here
    # ...
    # For example, process the item or perform other functions

    # Attach an instance to the item
    # item.instance = instance
    # item.save()
    else:
        # Perform other functions when all items have an instance attached
        # ...
        pass
