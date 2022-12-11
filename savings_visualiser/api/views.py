from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse, FileResponse
from .lib.analysis import analyse

class GraphApiView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        csv_file: InMemoryUploadedFile = request.data['file']

        try:
            graph_file = analyse(csv_file)
            return HttpResponse(graph_file, content_type='image/png')
            
            #return Response(graph_file, content_type='image/png', status=status.HTTP_200_OK)
        except: 
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)