from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    # --- NOVO: Campo customizado para o status de recorrência ---
    status_recorrencia = serializers.SerializerMethodField()
    # Adicionamos o nome do vendedor para exibir no card
    vendedor_nome = serializers.CharField(source='vendedor.nome', read_only=True)

    class Meta:
        model = Cliente
        # Adicionamos os novos campos à lista de fields
        fields = [
            'id', 
            'razao_social', 
            'score_potencial', 
            'curva_classificacao', 
            'cidade',
            'status_recorrencia',
            'vendedor_nome'
        ]

    # Esta função diz ao DRF como obter o valor para o campo 'status_recorrencia'
    def get_status_recorrencia(self, obj):
        # obj aqui é a instância do cliente. Nós simplesmente chamamos o método que já criamos!
        return obj.get_status_recorrencia()