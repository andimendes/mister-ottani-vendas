from django.core.management.base import BaseCommand
from gestao.models import Cliente, Tarefa

class Command(BaseCommand):
    help = 'Verifica clientes com compras atrasadas e gera tarefas para os vendedores.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando verificação de clientes com compras atrasadas...'))
        
        # Pega todos os clientes que têm um vendedor associado
        clientes = Cliente.objects.filter(vendedor__isnull=False)
        tarefas_criadas = 0

        for cliente in clientes:
            # Usamos a função que já criamos no model
            status = cliente.get_status_recorrencia()

            # Verificamos se o cliente está de fato atrasado
            if status.startswith('Atrasado'):
                # BOA PRÁTICA: Verificar se já não existe uma tarefa pendente para este cliente
                tarefa_existente = Tarefa.objects.filter(cliente=cliente, status='pendente').exists()

                if not tarefa_existente:
                    # Se não houver tarefa pendente, criamos uma nova
                    Tarefa.objects.create(
                        cliente=cliente,
                        vendedor=cliente.vendedor,
                        titulo=f"Verificar compra recorrente de {cliente.razao_social}",
                        descricao=f"O cliente está com o status de compra: '{status}'. Favor entrar em contato."
                    )
                    tarefas_criadas += 1
                    self.stdout.write(self.style.SUCCESS(f"Tarefa criada para o cliente: {cliente.razao_social}"))

        self.stdout.write(self.style.SUCCESS(f'--- Verificação concluída. {tarefas_criadas} novas tarefas foram criadas. ---'))