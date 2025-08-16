from django.db import models
from django.conf import settings

class Vendedor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendedor_vendas',  # Adicionado related_name
    )

    def __str__(self):
        return self.user.username  # Ou qualquer outro campo que você queira exibir

class Pedido(models.Model):
    cliente = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='ABERTO')

    def __str__(self):
        return f"{self.cliente} – R${self.total}"
