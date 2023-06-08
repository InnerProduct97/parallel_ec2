from django.db import models


class Instance(models.Model):
    instance_id = models.CharField(max_length=200, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def assigned_items_count(self):
        return self.assigned_items.count()

    @classmethod
    def get_instance_with_minimum_assigned_items(cls):
        # Retrieve the instance with the minimum number of assigned items
        return cls.objects.annotate(assigned_items_count=models.Count('assigned_items')).order_by(
            'assigned_items_count').first()

    def __str__(self):
        return self.instance_id


class Item(models.Model):
    buffer = models.CharField(max_length=999, null=True, blank=True)
    iterations = models.IntegerField(default=0)
    instance = models.ForeignKey(
        Instance,
        on_delete=models.DO_NOTHING,
        related_name="assigned_items",
        null=True,
        blank=True
    )


class Completed(models.Model):
    output = models.CharField(max_length=1999, null=False)
