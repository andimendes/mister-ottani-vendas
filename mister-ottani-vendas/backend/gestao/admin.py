from django.contrib import admin
from .models import Vendedor, Cliente, Contato, ClienteProdutoMix, Tarefa, Oportunidade # Adicionamos Oportunidade

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'vendedor', 'score_potencial', 'curva_classificacao', 'status_recorrencia', 'data_ultima_compra', 'frequencia_compra_dias',)
    list_filter = ('curva_classificacao', 'vendedor', 'cidade')
    search_fields = ('razao_social', 'cnpj')
    ordering = ('-score_potencial',)
    
    @admin.display(description='Status Recorrência')
    def status_recorrencia(self, obj):
        return obj.get_status_recorrencia()

class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'vendedor', 'status', 'data_criacao')
    list_filter = ('status', 'vendedor')
    search_fields = ('titulo', 'cliente__razao_social')

# --- NOVO: Customização para a exibição de Oportunidades ---
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = ('nome_empresa', 'vendedor_responsavel', 'etapa_funil', 'valor_estimado', 'data_criacao')
    list_filter = ('etapa_funil', 'vendedor_responsavel')
    search_fields = ('nome_empresa', 'contato_nome')
    ordering = ('-data_criacao',)

# Registros
admin.site.register(Vendedor)
admin.site.register(Contato)
admin.site.register(ClienteProdutoMix)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Tarefa, TarefaAdmin)
admin.site.register(Oportunidade, OportunidadeAdmin) # Registramos a Oportunidade