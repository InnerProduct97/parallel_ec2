from .models import Item, Instance, Completed
from rest_framework import serializers


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        fields = "__all__"


class CompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Completed
        fields = "__all__"
