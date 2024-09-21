from pymongo import MongoClient
import getpass
from bson.objectid import ObjectId

senha = getpass.getpass("Digite a senha do MongoDB: ")

uri = f"mongodb+srv://x1ngue:{senha}@cluster0.uwf0d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(uri)
    db = client['biblioteca']
    print("Conexão bem-sucedida ao MongoDB!")
except Exception as e:
    print("Erro ao conectar ao MongoDB:", e)

livros_collection = db['livros']
usuarios_collection = db['usuarios']
emprestimos_collection = db['emprestimos']

def adicionar_livro():
    titulo = input("Digite o título do livro: ")
    autor = input("Digite o autor do livro: ")
    genero = input("Digite o gênero do livro: ")
    ano = int(input("Digite o ano de publicação: "))
    isbn = input("Digite o ISBN (código único): ")
    quantidade = int(input("Digite a quantidade de exemplares disponíveis: "))

    if livros_collection.find_one({"isbn": isbn}):
        print(f"Erro: Já existe um livro cadastrado com o ISBN {isbn}.")
        return

    livro = {
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "ano": ano,
        "isbn": isbn,
        "quantidade": quantidade,
        "disponivel": quantidade > 0 
    }

    livros_collection.insert_one(livro)
    print(f"Livro '{titulo}' adicionado com sucesso.")

def listar_livros():
    livros = livros_collection.find()
    for livro in livros:
        print(f"ID: {livro['_id']}, Título: {livro['titulo']}, Autor: {livro['autor']}, Gênero: {livro['genero']}, "
              f"Ano: {livro['ano']}, ISBN: {livro['isbn']}, Quantidade: {livro['quantidade']}, Disponível: {livro['disponivel']}")
        
def atualizar_livro():
    livro_id = input("Digite o ID do livro que deseja atualizar: ")
    novos_dados = {}
    titulo = input("Novo título (deixe em branco para manter o atual): ")
    autor = input("Novo autor (deixe em branco para manter o atual): ")
    genero = input("Novo gênero (deixe em branco para manter o atual): ")
    ano = input("Novo ano de publicação (deixe em branco para manter o atual): ")
    quantidade = input("Nova quantidade de exemplares (deixe em branco para manter o atual): ")

    if titulo:
        novos_dados['titulo'] = titulo
    if autor:
        novos_dados['autor'] = autor
    if genero:
        novos_dados['genero'] = genero
    if ano:
        novos_dados['ano'] = int(ano)
    if quantidade:
        novos_dados['quantidade'] = int(quantidade)
        novos_dados['disponivel'] = int(quantidade) > 0 

    livros_collection.update_one({"_id": ObjectId(livro_id)}, {"$set": novos_dados})
    print(f"Livro ID {livro_id} atualizado com sucesso.")

def excluir_livro():
    livro_id = input("Digite o ID do livro que deseja excluir: ")
    livros_collection.delete_one({"_id": ObjectId(livro_id)})
    print(f"Livro ID {livro_id} excluído com sucesso.")

def cadastrar_usuario():
    nome = input("Digite o nome do usuário: ")
    email = input("Digite o email do usuário: ")
    data_nascimento = input("Digite a data de nascimento (dd/mm/aaaa): ")
    documento = input("Digite o número de documento (CPF ou RG): ")

    if usuarios_collection.find_one({"email": email}):
        print(f"Erro: Já existe um usuário cadastrado com o e-mail {email}.")
        return
    if usuarios_collection.find_one({"documento": documento}):
        print(f"Erro: Já existe um usuário cadastrado com o documento {documento}.")
        return

    usuario = {
        "nome": nome,
        "email": email,
        "data_nascimento": data_nascimento,
        "documento": documento
    }

    usuarios_collection.insert_one(usuario)
    print(f"Usuário '{nome}' cadastrado com sucesso.")