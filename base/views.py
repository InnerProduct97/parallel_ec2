from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from random import shuffle
from .models import Item, Instance, Completed
from rest_framework.viewsets import ModelViewSet
from .serializer import ItemSerializer, InstanceSerializer, CompletedSerializer
from .cron import *
from django.forms.models import model_to_dict


# Views Goes Here
@csrf_exempt
def enqueue(request):
    if request.method == "PUT":
        buffer = request.GET.get("buffer", "")
        iterations = request.GET.get("iterations", 0)
        item = Item.objects.create(buffer=buffer, iterations=iterations)
        item.save()
        item_data = {"id": item.id, "buffer": item.buffer, "iterations": item.iterations}
        create_item(**item_data)
        return JsonResponse({"id": item.id})

    return JsonResponse({"details": "Method Not Allowed"}, status=400)


@csrf_exempt
def pull_completed(request):
    if request.method == "POST":
        top = int(request.GET.get("top", 0))
        items = Completed.objects.all()
        if items.exists():
            data = [model_to_dict(item) for item in items]
            shuffle(data)
            data = data[:top]
            for item in data:
                items.filter(pk=item.get("id")).delete()
            return JsonResponse({"data": data})
        return JsonResponse({"details": 0})
    return JsonResponse(status=400, data={"details": "Method Not Allowed"})


class ItemManagement(ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = []
    authentication_classes = []
    queryset = Item.objects.all()


class InstanceManagement(ModelViewSet):
    serializer_class = InstanceSerializer
    permission_classes = []
    authentication_classes = []
    queryset = Instance.objects.all()


class CompletedManagements(ModelViewSet):
    serializer_class = CompletedSerializer
    permission_classes = []
    authentication_classes = []
    queryset = Completed.objects.all()


def test(request):
    remove_idle_instances()
    return JsonResponse({"details": "Successfull"})