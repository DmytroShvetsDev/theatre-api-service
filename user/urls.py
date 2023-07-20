from django.db import router
from django.urls import path, include

urlpatterns = [path("", include(router.urls))]

app_name = "user"
