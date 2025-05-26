from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .models import Document
from .serializers import DocumentSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import docx
import os
import requests
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)

class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            title=self.request.data.get('title', self.request.FILES['file'].name)
        )

    def get_serializer_context(self):
        return {'request': self.request}

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        return {'request': self.request}

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            response.data.update({
                'user': UserSerializer(user).data
            })
        return response

# Add to views.py
class DocumentContentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk, user=request.user)
        
        try:
            if document.file.name.endswith('.pdf'):
                from PyPDF2 import PdfReader
                document.file.open('rb')
                reader = PdfReader(document.file)
                text = "\n".join([page.extract_text() for page in reader.pages])
            elif document.file.name.endswith(('.docx', '.doc')):
                from docx import Document as DocxDocument
                document.file.open()
                doc = DocxDocument(document.file)
                text = "\n".join([para.text for para in doc.paragraphs])
            else:
                text = document.file.read().decode('utf-8')
                
            return Response({'content': text})
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        

class AskAIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question = request.data.get('question')
        context = request.data.get('context')

        if not question or not context:
            return Response({'error': 'Missing question or context'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hf_api_token = os.getenv('HF_API_KEY') 
            headers = {"Authorization": {hf_api_token}}
            payload = {
                "inputs": {
                    "question": question,
                    "context": context
                }
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                return Response({'error': 'Failed to get response from Hugging Face', 'details': response.text},
                                status=response.status_code)

            answer = response.json().get('answer', 'No answer found.')

            return Response({'answer': answer})

        except Exception as e:
            return Response({'error': str(e)}, status=500)
