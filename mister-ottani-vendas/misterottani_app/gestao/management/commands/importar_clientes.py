import csv
from django.core.management.base import BaseCommand
from gestao.models import Cliente, Contato

class Command(BaseCommand):
    help = 'Importa clientes de um arquivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('caminho_do_arquivo', type=str, help='O caminho para o arquivo CSV a ser importado.')

    def handle(self, *args, **options):
        caminho_arquivo = options['caminho_do_arquivo']
        self.stdout.write(self.style.SUCCESS(f'Iniciando a importação do arquivo: {caminho_arquivo}'))

        try:
            with open(caminho_arquivo, mode='r', encoding='latin-1') as file:
                reader = csv.DictReader(file)
                total_linhas = 0
                clientes_criados = 0
                clientes_existentes = 0

                for row in reader:
                    total_linhas += 1
                    cnpj_limpo = ''.join(filter(str.isdigit, row.get('CNPJ', '')))

                    if not cnpj_limpo:
                        self.stdout.write(self.style.WARNING(f'Linha {total_linhas} ignorada: CNPJ ausente ou inválido.'))
                        continue

                    # Usamos get_or_create para evitar duplicatas baseadas no CNPJ
                    cliente, created = Cliente.objects.get_or_create(
                        cnpj=cnpj_limpo,
                        defaults={
                            'razao_social': row.get('EMPRESA', 'Não informado'),
                            'endereco': row.get('ENDEREÇO', ''),
                            'cidade': row.get('CIDADE', ''),
                        }
                    )

                    if created:
                        clientes_criados += 1
                        self.stdout.write(self.style.SUCCESS(f'Cliente criado: {cliente.razao_social} ({cliente.cnpj})'))
                        
                        # Se o cliente foi criado, adiciona um contato principal
                        Contato.objects.create(
                            cliente=cliente,
                            nome="Contato Principal", # Nome genérico
                            telefone=row.get('TELEFONE', ''),
                            email=row.get('EMAIL', '')
                        )
                    else:
                        clientes_existentes += 1
                        self.stdout.write(self.style.NOTICE(f'Cliente já existe: {cliente.razao_social} ({cliente.cnpj})'))

            self.stdout.write(self.style.SUCCESS('--- Importação Concluída ---'))
            self.stdout.write(f'Total de linhas processadas: {total_linhas}')
            self.stdout.write(f'Novos clientes criados: {clientes_criados}')
            self.stdout.write(f'Clientes que já existiam: {clientes_existentes}')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Erro: O arquivo "{caminho_arquivo}" não foi encontrado.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro inesperado: {e}'))