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
        bankwest_csv_file: InMemoryUploadedFile = request.data['bankwest']
        commbank_csv_file = None
        if 'commbank' in request.data:
            commbank_csv_file: InMemoryUploadedFile = request.data['commbank']
        
        hidden: bool = request.data['hideAxis'] == 'true'

        try:
            graph_file = analyse(bankwest_csv_file, commbank_csv_file, hidden)
            return HttpResponse(graph_file, content_type='image/png')

        except: 
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)