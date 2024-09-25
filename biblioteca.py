from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime 
import getpass
import sys
import configparser 


while True:

    config = configparser.ConfigParser()
    config.read('config.ini')

    senha = config['conexao']['senha']

    try:
        uri = f"mongodb+srv://x1ngue:{senha}@cluster0.uwf0d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(uri)
        db = client['biblioteca']
        db_l = client.list_database_names()
        print("\nConexão bem-sucedida ao MongoDB!")
        break
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
    data_nascimento = input("Digite a data de nascimento (aaaa-mm-dd): ")
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

def listar_usuarios():
    usuarios = usuarios_collection.find()
    for usuario in usuarios:
        if 'data_nascimento' in usuario:
            data_nascimento = usuario['data_nascimento']
        else:
            data_nascimento = "Não informada"
        
        if 'documento' in usuario:
            documento = usuario['documento']
        else:
            documento = "Não informado"
        
        print(f"ID: {usuario['_id']}, Nome: {usuario['nome']}, E-mail: {usuario['email']}, Data de Nascimento: {data_nascimento}, Documento: {documento}")

def atualizar_usuario():
    id_usuario = input("Digite o ID do usuário a ser atualizado: ")
    nome = input("Digite o novo nome do usuário (deixe em branco para manter o atual): ")
    email = input("Digite o novo email do usuário (deixe em branco para manter o atual): ")
    data_nascimento = input("Digite a nova data de nascimento (deixe em branco para manter o atual): ")
    documento = input("Digite o novo número de documento (deixe em branco para manter o atual): ")

    query = {"_id": ObjectId(id_usuario)}
    update = {"$set": {"nome": nome, "email": email, "data_nascimento": data_nascimento, "documento": documento}}

    try:
        result = usuarios_collection.update_one(query, update)
        if result.modified_count == 1:
            print(f"Usuário com ID {id_usuario} atualizado com sucesso!")
        else:
            print(f"Usuário com ID {id_usuario} não encontrado.")
    except pymongo.errors.OperationFailure as e:
        print(f"Erro ao atualizar usuário: {e}")

def deletar_usuario():
    id_usuario = input("Digite o ID do usuário a ser deletado: ")
    query = {"_id": ObjectId(id_usuario)}
    try:
        result = usuarios_collection.delete_one(query)
        if result.deleted_count == 1:
            print(f"Usuário com ID {id_usuario} deletado com sucesso!")
        else:
            print(f"Usuário com ID {id_usuario} não encontrado.")
    except pymongo.errors.OperationFailure as e:
        print(f"Erro ao deletar usuário: {e}")

def emprestar_livro():
    livro_id = input("Digite o ID do livro a ser emprestado: ")
    usuario_id = input("Digite o ID do usuário: ")
    livro = livros_collection.find_one({"_id": ObjectId(livro_id)})

    if livro and livro['disponivel'] and livro['quantidade'] > 0:
        emprestimo = {
            "livro_id": ObjectId(livro_id),
            "usuario_id": ObjectId(usuario_id),
            "data_emprestimo": datetime.now(),
            "devolvido": False
        }
        emprestimos_collection.insert_one(emprestimo)
        livros_collection.update_one({"_id": ObjectId(livro_id)}, {"$inc": {"quantidade": -1}})
        livro_atualizado = livros_collection.find_one({"_id": ObjectId(livro_id)})
        if livro_atualizado['quantidade'] == 0:
            livros_collection.update_one({"_id": ObjectId(livro_id)}, {"$set": {"disponivel": False}})
        print(f"Livro ID {livro_id} emprestado ao usuário ID {usuario_id}.")
    else:
        print("Livro não disponível para empréstimo.")

def devolver_livro():
    emprestimo_id = input("Digite o ID do empréstimo: ")
    emprestimo = emprestimos_collection.find_one({"_id": ObjectId(emprestimo_id)})

    if emprestimo and not emprestimo['devolvido']:
        livros_collection.update_one({"_id": emprestimo['livro_id']}, {"$inc": {"quantidade": 1}})
        emprestimos_collection.update_one({"_id": ObjectId(emprestimo_id)}, {"$set": {"devolvido": True}})
        livro = livros_collection.find_one({"_id": emprestimo['livro_id']})
        if livro['quantidade'] > 0:
            livros_collection.update_one({"_id": livro['_id']}, {"$set": {"disponivel": True}})
        print(f"Empréstimo ID {emprestimo_id} finalizado e livro devolvido.")
    else:
        print("Empréstimo já finalizado ou inexistente.")

def listar_emprestimos():
    data_inicial = input("\nDigite a data inicial (aaaa-mm-dd): ")
    data_final = input("Digite a data final (aaaa-mm-dd): ")

    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")

    data_inicial = data_inicial.replace(hour=0, minute=0, second=0)
    data_final = data_final.replace(hour=23, minute=59, second=59)

    emprestimos = emprestimos_collection.find({
        "data_emprestimo": {
            "$gte": data_inicial,
            "$lte": data_final
        }
    })

    emprestimos_lista = list(emprestimos)

    if len(emprestimos_lista) == 0:
        print("Nenhum empréstimo encontrado.")  
    else:
        for emprestimo in emprestimos_lista:
            print("\n\n------------------------")
            print(f"ID Empréstimo: {emprestimo['_id']}, Livro ID: {emprestimo['livro_id']}, Usuário ID: {emprestimo['usuario_id']}, Devolvido: {emprestimo['devolvido']}")
            print("Dados do empréstimo:")
            print(f"  Data do empréstimo: {emprestimo['data_emprestimo'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Livro: {emprestimo['livro_id']}")
            print(f"  Usuário: {emprestimo['usuario_id']}")
            print(f"  Devolvido: {emprestimo['devolvido']}")
            print("------------------------\n")

while True:
    print("\nMenu Biblioteca:\n")
    print("1. Adicionar Livro")
    print("2. Listar Livros")
    print("3. Atualizar Livro")
    print("4. Excluir Livro")
    print("5. Cadastrar Usuário")
    print("6. Listar Usuários")
    print("7. Atualizar Usuário")
    print("8. Deletar Usuário")
    print("9. Emprestar Livro")
    print("10. Devolver Livro")
    print("11. Listar Empréstimos")
    print("12. Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == '1':
        adicionar_livro()
    elif opcao == '2':
        listar_livros()
    elif opcao == '3':
        atualizar_livro()
    elif opcao == '4':
        excluir_livro()
    elif opcao == '5':
        cadastrar_usuario()
    elif opcao == '6':
        listar_usuarios()
    elif opcao == '7':
        atualizar_usuario()
    elif opcao == '8':
        deletar_usuario()
    elif opcao == '9':
        emprestar_livro()
    elif opcao == '10':
        devolver_livro()
    elif opcao == '11':
        listar_emprestimos()
    elif opcao == '12':
        print("Encerrando o sistema.")
        break
    else:
        print("Opção inválida. Tente novamente.")