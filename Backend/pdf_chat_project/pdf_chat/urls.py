from django.urls import path
from . import views

urlpatterns = [
    path('pdf_chat_backend/', views.pdf_chat_backend, name='pdf_chat_backend'),
]
