from decimal import Decimal
from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.db.models import Max, Min, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

class Vendedor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        verbose_name="Usuário Django",
    )
    nome = models.CharField(max_length=255, verbose_name="Nome do Vendedor")
    email = models.EmailField(max_length=255, unique=True, verbose_name="E-mail")
    telefone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    CURVA_CHOICES = (("A", "Curva A"), ("B", "Curva B"), ("C", "Curva C"))

    razao_social = models.CharField(max_length=255, verbose_name="Razão Social")
    nome_fantasia = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome Fantasia"
    )
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    endereco = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Endereço"
    )
    cidade = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Cidade"
    )
    estado = models.CharField(
        max_length=2, blank=True, null=True, verbose_name="Estado"
    )
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vendedor Responsável",
    )
    tabela_precos = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Tabela de Preços"
    )
    condicoes_pagamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Condições de Pagamento",
    )
    faturamento_ultimos_12m = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Faturamento (Últimos 12M)",
    )
    volume_medio_pedido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Volume Médio por Pedido",
    )
    frequencia_compra_dias = models.IntegerField(
        default=0, verbose_name="Frequência de Compra (dias)"
    )
    prazo_medio_pagamento_dias = models.IntegerField(
        default=0, verbose_name="Prazo Médio de Pagamento (dias)"
    )
    score_potencial = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Score de Potencial",
    )
    curva_classificacao = models.CharField(
        max_length=1,
        choices=CURVA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Curva de Classificação",
    )
    data_ultima_compra = models.DateField(
        blank=True, null=True, verbose_name="Data da Última Compra"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True, verbose_name="Data de Atualização"
    )

    def __str__(self):
        return self.nome_fantasia or self.razao_social

    def calcular_e_salvar_score(self):
        # Agrega valores globais
        agregados = Cliente.objects.aggregate(
            max_faturamento=Max("faturamento_ultimos_12m"),
            min_prazo=Min("prazo_medio_pagamento_dias"),
            min_frequencia=Min("frequencia_compra_dias"),
        )
        max_mix_agregado = (
            Cliente.objects.annotate(num_produtos=Count("mix_produtos"))
            .aggregate(max_num=Max("num_produtos"))
        )

        max_faturamento = agregados.get("max_faturamento") or 0
        min_prazo = agregados.get("min_prazo") or 0
        min_frequencia = agregados.get("min_frequencia") or 0
        max_mix = max_mix_agregado.get("max_num") or 0

        # Cálculo de scores parciais
        score_faturamento = (
            (self.faturamento_ultimos_12m / max_faturamento) * 100
            if max_faturamento
            else 0
        )
        score_prazo = (
            (Decimal(min_prazo) / Decimal(self.prazo_medio_pagamento_dias)) * 100
            if self.prazo_medio_pagamento_dias and min_prazo > 0
            else 0
        )
        score_frequencia = (
            (Decimal(min_frequencia) / Decimal(self.frequencia_compra_dias)) * 100
            if self.frequencia_compra_dias and min_frequencia > 0
            else 0
        )
        score_mix = (
            (Decimal(self.mix_produtos.count()) / Decimal(max_mix)) * 100
            if max_mix
            else 0
        )

        # Score final ponderado
        score_final = (
            (score_faturamento * Decimal("0.40"))
            + (score_prazo * Decimal("0.30"))
            + (score_frequencia * Decimal("0.20"))
            + (score_mix * Decimal("0.10"))
        )

        # Define curva
        if score_final > 80:
            curva = "A"
        elif score_final > 60:
            curva = "B"
        else:
            curva = "C"

        self.score_potencial = round(score_final, 2)
        self.curva_classificacao = curva
        self.save()
        print(
            f"Score calculado para {self.razao_social}: "
            f"{self.score_potencial} (Curva {self.curva_classificacao})"
        )

    def get_status_recorrencia(self):
        if not self.data_ultima_compra or not self.frequencia_compra_dias:
            return "Dados insuficientes"
        dias_desde = (date.today() - self.data_ultima_compra).days
        restante = self.frequencia_compra_dias - dias_desde
        if restante < 0:
            return f"Atrasado ({-restante} dias)"
        if restante <= 7:
            return f"A comprar (faltam {restante} dias)"
        return "Em dia"

class Contato(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="contatos", verbose_name="Cliente"
    )
    nome = models.CharField(max_length=255, verbose_name="Nome do Contato")
    cargo = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Cargo"
    )
    email = models.EmailField(
        max_length=255, blank=True, null=True, verbose_name="E-mail"
    )
    telefone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone"
    )

    def __str__(self):
        return f"{self.nome} ({self.cliente})"

class ClienteProdutoMix(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="mix_produtos",
        verbose_name="Cliente",
    )
    produto_sku = models.CharField(max_length=50, verbose_name="SKU do Produto")
    produto_nome = models.CharField(
        max_length=255, verbose_name="Nome do Produto"
    )

    class Meta:
        unique_together = ("cliente", "produto_sku")

    def __str__(self):
        return f"{self.produto_nome} - {self.cliente}"

class Tarefa(models.Model):
    STATUS_CHOICES = (("pendente", "Pendente"), ("concluida", "Concluída"))

    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, verbose_name="Cliente Alvo"
    )
    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.CASCADE, verbose_name="Vendedor Responsável"
    )
    titulo = models.CharField(max_length=255, verbose_name="Título da Tarefa")
    descricao = models.TextField(
        blank=True, null=True, verbose_name="Descrição"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Criação"
    )
    data_conclusao = models.DateTimeField(
        blank=True, null=True, verbose_name="Data de Conclusão"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"{self.titulo} - {self.cliente.razao_social}"

class Oportunidade(models.Model):
    ETAPAS_FUNIL_CHOICES = [
        ("prospect", "Prospect"),
        ("contato_inicial", "Contato Inicial"),
        ("proposta", "Envio de Proposta"),
        ("negociacao", "Negociação"),
        ("fechado_ganho", "Fechado (Ganho)"),
        ("fechado_perdido", "Fechado (Perdido)"),
    ]

    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    contato_nome = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome do Contato"
    )
    contato_email = models.EmailField(blank=True, null=True)
    contato_telefone = models.CharField(
        max_length=20, blank=True, null=True
    )
    vendedor_responsavel = models.ForeignKey(
        Vendedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vendedor Responsável",
    )
    etapa_funil = models.CharField(
        max_length=20,
        choices=ETAPAS_FUNIL_CHOICES,
        default="prospect",
        verbose_name="Etapa do Funil",
    )
    valor_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valor Estimado",
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(
        blank=True, null=True, verbose_name="Data de Fechamento"
    )

    class Meta:
        verbose_name = "Oportunidade"
        verbose_name_plural = "Oportunidades"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"{self.nome_empresa} - {self.get_etapa_funil_display()}"

class Pedido(models.Model):
    STATUS_CHOICES = (
        ("pendente", "Pendente"),
        ("concluido", "Concluído"),
        ("cancelado", "Cancelado"),
    )

    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="pedidos"
    )
    valor_total = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Valor Total"
    )
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status",
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.razao_social}"

@receiver(post_save, sender=User)
def criar_vendedor_quando_usuario_criado(sender, instance, created, **kwargs):
    """
    Ao criar um usuário que pertença ao grupo 'Vendedor',
    cria automaticamente o Vendedor correspondente.
    """
    if created and instance.groups.filter(name="Vendedor").exists():
        Vendedor.objects.create(
            user=instance,
            nome=instance.get_full_name() or instance.username,
            email=instance.email,
        )
