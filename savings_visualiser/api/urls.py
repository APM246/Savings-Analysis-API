from django.urls import path
from .views import GraphApiView

urlpatterns = [
    path('graph', GraphApiView.as_view())
]