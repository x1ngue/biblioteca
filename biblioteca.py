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

    # Verificar se o ISBN já existe
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