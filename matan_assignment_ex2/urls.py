from django.urls import path, include
from base.views import *

urlpatterns = [
    path("enqueue", enqueue),
    path("pullCompleted", pull_completed),
    path("admin/", include("base.urls")),
]
