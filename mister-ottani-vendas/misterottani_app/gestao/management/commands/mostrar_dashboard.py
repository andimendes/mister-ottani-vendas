from django.core.management.base import BaseCommand
from django.db.models import Sum, Count
from gestao.models import Cliente, Oportunidade, Tarefa
from decimal import Decimal

class Command(BaseCommand):
    help = 'Exibe um dashboard com os principais KPIs de vendas no terminal.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Mister Ottani Vendas PRO | Dashboard Gerencial ---"))

        # --- KPIs de Clientes Ativos (Módulo 1) ---
        total_clientes = Cliente.objects.count()
        faturamento_total = Cliente.objects.aggregate(total=Sum('faturamento_ultimos_12m'))['total'] or Decimal('0.00')
        clientes_curva_a = Cliente.objects.filter(curva_classificacao='A').count()

        self.stdout.write(self.style.HTTP_INFO("\n>> INDICADORES DE CLIENTES ATIVOS <<"))
        self.stdout.write(f"Número Total de Clientes: {total_clientes}")
        self.stdout.write(f"Faturamento Anualizado Total: R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.stdout.write(f"Clientes Curva 'A' (Estratégicos): {clientes_curva_a}")

        # --- KPIs de Recorrência (Módulo 2) ---
        tarefas_pendentes = Tarefa.objects.filter(status='pendente').count()

        self.stdout.write(self.style.HTTP_INFO("\n>> INDICADORES DE RECORRÊNCIA E TAREFAS <<"))
        self.stdout.write(f"Total de Tarefas Pendentes: {tarefas_pendentes}")

        # --- KPIs do Funil de Vendas (Módulo 3) ---
        oportunidades_abertas = Oportunidade.objects.exclude(etapa_funil__in=['fechado_ganho', 'fechado_perdido'])
        total_oportunidades_abertas = oportunidades_abertas.count()
        valor_total_pipeline = oportunidades_abertas.aggregate(total=Sum('valor_estimado'))['total'] or Decimal('0.00')

        self.stdout.write(self.style.HTTP_INFO("\n>> INDICADORES DO FUNIL DE VENDAS <<"))
        self.stdout.write(f"Oportunidades em Aberto: {total_oportunidades_abertas}")
        self.stdout.write(f"Valor Total em Pipeline: R$ {valor_total_pipeline:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Detalhamento do funil
        etapas_funil = Oportunidade.objects.filter(
            etapa_funil__in=['prospect', 'contato_inicial', 'proposta', 'negociacao']
        ).values('etapa_funil').annotate(total=Count('id')).order_by('etapa_funil')

        self.stdout.write("Distribuição por Etapa:")
        for etapa in etapas_funil:
            self.stdout.write(f"  - {etapa['etapa_funil'].replace('_', ' ').title()}: {etapa['total']}")

        self.stdout.write(self.style.SUCCESS("\n--- Fim do Relatório ---"))