from django.core.management.base import BaseCommand
import pandas as pd
import os  # Para trabalhar com caminhos de arquivos
from django.contrib.auth.models import User
from app.models import Aluno, Curso  # Certifique-se de importar seus modelos corretamente


class Command(BaseCommand):
    help = 'Comando para carregar alunos a partir de Excel extraído do Moodle de cada recurso geral de curso'

    def add_arguments(self, parser):
        # Argumento para o arquivo Excel
        parser.add_argument('excel_file', type=str, help='Nome do arquivo Excel (localizado na pasta dados_alunos)')
        # Argumento para o curso
        parser.add_argument('curso_nome', type=str, help='Nome do curso')

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        curso_nome = options['curso_nome']

        # Gerar o caminho completo para o arquivo Excel na pasta 'dados_alunos'
        excel_file_path = os.path.join('dados_alunos', excel_file)

        # Verifica se o arquivo Excel existe
        if not os.path.exists(excel_file_path):
            self.stdout.write(self.style.ERROR(f'O arquivo Excel "{excel_file}" não foi encontrado na pasta dados_alunos'))
            return

        # Verifica se o curso existe
        try:
            curso = Curso.objects.get(nome=curso_nome)
        except Curso.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Curso "{curso_nome}" não encontrado'))
            return

        # Carregar o arquivo Excel
        df = pd.read_excel(excel_file_path)

        # Iterar sobre cada linha no DataFrame
        for index, row in df.iterrows():
            nome = row['Nome']
            nome_aluno = nome.split()[0]
            apelido = ' '.join(nome.split()[1:])
            numero_aluno = 'a' + str(row['Aluno'])
            email = row['Email']

            # Verifica se o usuário já existe pelo número de aluno (username)
            if not User.objects.filter(username=str(numero_aluno)).exists():
                # Criar um novo utilizador Django usando o número de aluno como username
                user = User.objects.create_user(username=str(numero_aluno), email=email, password=None)
                user.first_name = nome_aluno
                user.last_name = apelido
                user.save()

                # Criar a instância de Aluno associada ao usuário e ao curso
                aluno = Aluno.objects.create(user=user, numero=numero_aluno, curso=curso)

                self.stdout.write(self.style.SUCCESS(f'Utilizador criado com sucesso: {nome_aluno} {apelido}'))
            else:
                self.stdout.write(self.style.WARNING(f'Utilizador já existe: {nome_aluno} {apelido}'))

        self.stdout.write(self.style.SUCCESS('Comando executado com sucesso'))
