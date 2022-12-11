from django.urls import path
from .views import GraphApiView

urlpatterns = [
    path('a', GraphApiView.as_view())
]