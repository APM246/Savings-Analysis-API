from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from .lib.analysis import analyse

class GraphApiView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file: InMemoryUploadedFile = request.data['file']
        analyse(file)
        return Response(status=status.HTTP_200_OK)