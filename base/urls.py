from django.urls import path, include
from rest_framework_nested.routers import SimpleRouter
from .views import ItemManagement, InstanceManagement, CompletedManagements, test


router = SimpleRouter(trailing_slash=False)
router.register('items', ItemManagement, basename='')
router.register('instances', InstanceManagement, basename='')
router.register('completed', CompletedManagements, basename='')

urlpatterns = [
    path('', include(router.urls)),
    path('test', test),
]