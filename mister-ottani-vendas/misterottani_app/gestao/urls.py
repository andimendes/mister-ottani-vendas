from django.urls import path
from .views import ClienteListAPIView

urlpatterns = [
    # Este endereço agora retornará uma lista de clientes em JSON
    path('clientes/', ClienteListAPIView.as_view(), name='cliente-list'),
]