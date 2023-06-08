import requests
from django.conf import settings


# Set the base URL for your Django API
base_url = settings.BASE_URL + "/admin/"


# Perform CRUD operations on the Instance model
def create_instance(**kwargs):
    url = base_url + 'instances'
    data = {**kwargs}
    response = requests.post(url, data=data)
    return response.json()


def retrieve_instance(instance_id):
    url = base_url + f'instances/{instance_id}'
    response = requests.get(url)
    return response.json()


def update_instance(instance_id, new_instance_id):
    url = base_url + f'instances/{instance_id}'
    data = {'instance_id': new_instance_id}
    response = requests.put(url, data=data)
    return response.json()


def delete_instance(instance_id):
    url = base_url + f'instances/{instance_id}'
    response = requests.delete(url)
    return response.status_code


def list_instance():
    url = base_url + 'instances'
    response = requests.get(url)
    return response.json()


# Perform CRUD operations on the Item model
def create_item(**kwargs):
    url = base_url + 'items'
    data = {**kwargs}
    response = requests.post(url, data=data)
    return response.json()


def list_item():
    url = base_url + 'items'
    response = requests.get(url)
    return response.json()


def retrieve_item(item_id):
    url = base_url + f'items/{item_id}'
    response = requests.get(url)
    return response.json()


def update_item(item_id, **kwargs):
    url = base_url + f'items/{item_id}'
    data = {**kwargs}
    response = requests.put(url, data=data)
    return response.json()


def delete_item(item_id):
    url = base_url + f'items/{item_id}'
    response = requests.delete(url)
    return response.status_code
