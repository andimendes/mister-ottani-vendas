from rest_framework import generics
from .models import Cliente
from .serializers import ClienteSerializer

# Esta view usa o DRF para listar todos os clientes
class ClienteListAPIView(generics.ListAPIView):
    queryset = Cliente.objects.all().order_by('-score_potencial')
    serializer_class = ClienteSerializer

# NOTA: A view antiga 'dashboard_recorrencia' foi removida por enquanto.
# Vamos recriar essa lógica no nosso frontend depois.