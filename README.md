# DocumentManagerBackend
This is the backend of the Document Management Portal, built with **Django** and **Django REST Framework**. It provides APIs for user authentication, document management, and AI-powered question answering.

## 🔑 Features

- JWT-based user authentication
- Document upload, retrieval & deletion
- Serve document content
- AI Q&A via OpenAI API

## 🛠️ Technologies Used

- Django & DRF
- Simple JWT
- CORS Headers
- Huggingface API
- SQLite (or any DB)

## 🔧 Setup Instructions

1. Clone the repository:
   git clone https://github.com/your-username/document-manager-backend.git
   cd document-manager-backend

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate # Windows: venv\Scripts\activate

3. Install requirements:
   pip install -r requirements.txt

4. Apply migrations:
   python manage.py migrate

5. Run the server:
   python manage.py runserver

6. Add your Huggingface API key or any API key you want in the view where AI Q&A is handled.

## 🚀 API Endpoints

- `POST /api/auth/register/` – Register user  
- `POST /api/auth/login/` – Login and get JWT  
- `GET /api/profile/` – Get user profile  
- `GET/POST /api/documents/` – List or upload documents  
- `DELETE /api/documents/<id>/` – Delete a document  
- `GET /api/documents/<id>/content/` – Get document content  
- `POST /ask-ai/` – Ask question to AI

## 🌐 Deployment

Backend can be deployed on platforms like Render, Railway, or Heroku.

