from django.urls import path
from .views import GraphApiView, MonitorApiView

urlpatterns = [
    path('monitor', MonitorApiView.as_view()),
    path('graph', GraphApiView.as_view())
]