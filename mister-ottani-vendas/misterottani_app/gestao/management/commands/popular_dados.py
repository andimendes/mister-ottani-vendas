import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from gestao.models import Vendedor, Cliente, Contato, ClienteProdutoMix

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fictícios para teste, incluindo mix de produtos e datas.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando o processo de popular o banco de dados...'))

        fake = Faker('pt_BR')

        # --- Limpando dados antigos ---
        self.stdout.write('Limpando dados antigos...')
        Vendedor.objects.all().delete()
        Cliente.objects.all().delete()

        PRODUTOS_FICTICIOS = [
            ('MAS-001', 'Massa de Pastel Rolo 1kg'), ('MAS-002', 'Massa de Pastel Disco 500g'),
            ('LAS-001', 'Massa de Lasanha Fresca 500g'), ('PIZ-001', 'Disco de Pizza Tradicional 35cm'),
            ('PIZ-002', 'Mini Disco de Pizza 10cm (Pacote com 10)'), ('NHO-001', 'Nhoque de Batata 1kg'),
        ]

        # --- Criando Vendedores ---
        vendedores = []
        self.stdout.write('Criando 5 vendedores fictícios...')
        for _ in range(5):
            vendedor = Vendedor.objects.create(nome=fake.name(), email=fake.email(), telefone=fake.phone_number())
            vendedores.append(vendedor)
        self.stdout.write(self.style.SUCCESS('Vendedores criados.'))

        # --- Criando Clientes ---
        self.stdout.write('Criando 50 clientes fictícios...')
        for _ in range(50):
            cliente = Cliente.objects.create(
                razao_social=fake.company(),
                nome_fantasia=fake.company_suffix(),
                cnpj=fake.cnpj(),
                endereco=fake.street_address(),
                cidade=fake.city(),
                estado=fake.state_abbr(),
                vendedor=random.choice(vendedores),
                faturamento_ultimos_12m=random.uniform(5000.0, 100000.0),
                prazo_medio_pagamento_dias=random.randint(15, 60),
                # As duas linhas abaixo são cruciais
                frequencia_compra_dias=random.randint(7, 45),
                data_ultima_compra=fake.date_between(start_date='-60d', end_date='today')
            )

            Contato.objects.create(
                cliente=cliente, nome=fake.name(), cargo="Comprador",
                email=fake.email(), telefone=fake.phone_number()
            )

            num_produtos = random.randint(1, 4)
            produtos_do_cliente = random.sample(PRODUTOS_FICTICIOS, k=num_produtos)
            
            for sku, nome in produtos_do_cliente:
                ClienteProdutoMix.objects.create(
                    cliente=cliente,
                    produto_sku=sku,
                    produto_nome=nome
                )

        self.stdout.write(self.style.SUCCESS('Clientes e seus mixes de produtos criados.'))
        self.stdout.write(self.style.SUCCESS('--- Banco de dados populado com sucesso! ---'))