from django.core.management.base import BaseCommand
from django.db import transaction
from gestao.models import Cliente

class Command(BaseCommand):
    help = 'Calcula e salva o score de potencial para todos os clientes no banco de dados.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando o cálculo de score para todos os clientes...'))

        clientes = Cliente.objects.all()
        total_clientes = clientes.count()

        if total_clientes == 0:
            self.stdout.write(self.style.WARNING('Nenhum cliente encontrado no banco de dados.'))
            return

        for i, cliente in enumerate(clientes):
            # A linha abaixo é a única que não é print. É uma chamada de função.
            # Observe que a função calcular_e_salvar_score já tem um print embutido.
            cliente.calcular_e_salvar_score()
            # A linha abaixo é apenas uma barra de progresso.
            self.stdout.write(f'Processando cliente {i + 1}/{total_clientes}...', ending='\r')

        self.stdout.write(self.style.SUCCESS(f'\n--- Cálculo de score finalizado para {total_clientes} clientes! ---'))