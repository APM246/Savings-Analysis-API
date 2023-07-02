from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, FileResponse
from .lib.analysis import analyse
from time import sleep

class GraphApiView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            files = request.data.getlist("files")
            bank_types = request.data.getlist("bankTypes")
            hidden: bool = request.data['hideAxis'] == 'true'

            graph_file = analyse(files, bank_types, hidden)
            return HttpResponse(graph_file, content_type='image/png')

        except Exception as error:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MonitorApiView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK) 