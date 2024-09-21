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
