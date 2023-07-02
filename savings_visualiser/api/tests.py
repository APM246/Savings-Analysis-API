from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from savings_visualiser.api.views import MonitorApiView

class EndpointsTestCase(APITestCase):
    def test_monitor_endpoint(self):
        response = self.client.get('/api/monitor')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
    def test_graph_endpoint_500_when_no_file_provided(self):
        response = self.client.post('/api/graph')
        self.assertEqual(response.status_code, 400)