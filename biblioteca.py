from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import configparser
import pymongo


while True:
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        senha = config['conexao']['senha']

        try:
            uri = f"mongodb+srv://x1ngue:{senha}@cluster0.uwf0d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            client = MongoClient(uri)
            db = client['biblioteca']
            db_l = client.list_database_names()
            print("\nConexão bem-sucedida ao MongoDB!\n")
            break
        except Exception as e:
            print("Erro ao conectar ao MongoDB:", e)
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        exit()
        

livros_collection = db['livros']
usuarios_collection = db['usuarios']
emprestimos_collection = db['emprestimos']

def adicionar_livro():
    try:
        titulo = input("Digite o título do livro: ")
        if not titulo.strip():
            raise ValueError("Título não pode ser vazio")

        autor = input("Digite o autor do livro: ")
        if not autor.strip():
            raise ValueError("Autor não pode ser vazio")

        genero = input("Digite o gênero do livro: ")
        if not genero.strip():
            raise ValueError("Gênero não pode ser vazio")

        ano = int(input("Digite o ano de publicação: "))
        if ano < 1900 or ano > datetime.now().year:
            raise ValueError("Ano de publicação deve ser entre 1900 e o ano atual")

        isbn = input("Digite o ISBN (código único): ")
        if not isbn.strip():
            raise ValueError("ISBN não pode ser vazio")

        quantidade = int(input("Digite a quantidade de exemplares disponíveis: "))
        if quantidade < 0:
            raise ValueError("Quantidade de exemplares não pode ser negativa")

        if livros_collection.find_one({"isbn": isbn}):
            raise ValueError(f"Erro: Já existe um livro cadastrado com o ISBN {isbn}.")

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

    except ValueError as e:
        print(f"\nErro: {e}.")

    except Exception as e:
        print(f"\nErro inesperado: {e}")

def listar_livros():
    livros = livros_collection.find()

    encontrado = False
    for livro in livros:
        print(f"\nID: {livro['_id']}, Título: {livro['titulo']}, Autor: {livro['autor']}, Gênero: {livro['genero']}, "
            f"Ano: {livro['ano']}, ISBN: {livro['isbn']}, Quantidade: {livro['quantidade']}, Disponível: {livro['disponivel']}")
        
        encontrado = True

    if not encontrado:
        print("\n\nNenhum livro encontrado.\n")
        
def atualizar_livro():
    try:
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
            try:
                novos_dados['ano'] = int(ano)
            except ValueError:
                print("\nErro: O ano de publicação deve ser um número inteiro.")
                return
        if quantidade:
            try:
                novos_dados['quantidade'] = int(quantidade)
                novos_dados['disponivel'] = int(quantidade) > 0
            except ValueError:
                print("\nErro: A quantidade de exemplares deve ser um número inteiro.")
                return
            
        try:
            livro_id_obj = ObjectId(livro_id)
        except ValueError:
            print("Erro: O ID do livro é inválido.")
            return
        
        resultado = livros_collection.update_one({"_id": ObjectId(livro_id)}, {"$set": novos_dados})
        if resultado.matched_count == 0:
            print("Erro: O livro não foi encontrado.")
        else:
            print(f"\nLivro ID {livro_id} atualizado com sucesso.")
    except pymongo.errors.PyMongoError as e:
        print(f"Erro d conexão com o banco de dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def excluir_livro():
    try:
        livro_id = input("Digite o ID do livro que deseja excluir: ")
        try:
            livro_id_obj = ObjectId(livro_id)
        except ValueError:
            print("\nErro: O ID do livro é inválido.")
            return
        
        try:
            resultado = livros_collection.delete_one({"_id": ObjectId(livro_id)})
            if resultado.deleted_count == 0:
                print("\nErro: O livro não foi encontrado.")
            else:
                print(f"Livro ID {livro_id} excluído com sucesso.")
        except pymongo.errors.PyMongoError as e:
            print(f"Erro d conexão com o banco de dados: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except EOFError:
        print("\nErro: Entrada de dados inválida. Tente novamente.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def cadastrar_usuario():
    try:
        nome = input("Digite o nome do usuário: ")
        if not nome:
            print("\nErro: O nome do usuário deve ser informado.")
            return
        
        email = input("Digite o email do usuário: ")
        if not email:
            print("\nErro: O email do usuário deve ser informado.")
            return
        
        data_nascimento = input("Digite a data de nascimento (aaaa-mm-dd): ")
        try:
            datetime.strptime(data_nascimento, "%Y-%m-%d")
        except ValueError:
            print("\nErro: A data de nascimento é invalida. Use o formato aaaa-mm-dd.")
            return
            
        documento = input("Digite o número de documento (CPF ou RG): ")
        if not documento:
            print("\nErro: O número de documento deve ser informado.")
            return
        
        try:
            if usuarios_collection.find_one({"documento": documento}):
                print(f"Erro: Já existe um usuário cadastrado com o documento {documento}.")
                return
        except pymongo.errors.PyMongoError as e:
            print(f"Erro d conexão com o banco de dados: {e}")
            return

        usuario = {
            "nome": nome,
            "email": email,
            "data_nascimento": data_nascimento,
            "documento": documento
        }

        try:
            usuarios_collection.insert_one(usuario)
            print(f"Usuário '{nome}' cadastrado com sucesso.")
        except pymongo.errors.PyMongoError as e:
            print(f"Erro d conexão com o banco de dados: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except EOFError:
        print("\nErro: Entrada de dados inválida. Tente novamente.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def listar_usuarios():
    try:
        try:
            usuarios = usuarios_collection.find()
        except pymongo.errors.PyMongoError as e:
            print(f"Erro de conexão com o banco de dados: {e}")
            return

        if usuarios is None:
            print("Erro: Não foi possível recuperar a lista de usuários.")
            return

        for usuario in usuarios:
            try:
                if '_id' not in usuario:
                    print("Erro: O usuário não tem ID.")
                    continue

                if 'nome' not in usuario:
                    print(f"Erro: O usuário {usuario['_id']} não tem nome.")
                    continue

                if 'email' not in usuario:
                    print(f"Erro: O usuário {usuario['_id']} não tem e-mail.")
                    continue

                data_nascimento = usuario.get('data_nascimento', "Não informada")
                documento = usuario.get('documento', "Não informado")

                print(f"ID: {usuario['_id']}, Nome: {usuario['nome']}, E-mail: {usuario['email']}, Data de Nascimento: {data_nascimento}, Documento: {documento}")
            except Exception as e:
                print(f"Erro inesperado ao processar o usuário {usuario['_id']}: {e}")
    except KeyboardInterrupt:
        print("Operação cancelada pelo usuário.")
    except EOFError:
        print("Erro: Entrada de dados inválida.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def atualizar_usuario():
    try:
        id_usuario = input("Digite o ID do usuário a ser atualizado: ")
        if not id_usuario:
            print("Erro: O ID do usuário é obrigatório.")
            return

        try:
            ObjectId(id_usuario)
        except ValueError:
            print("Erro: O ID do usuário é inválido.")
            return

        nome = input("Digite o novo nome do usuário (deixe em branco para manter o atual): ")
        email = input("Digite o novo email do usuário (deixe em branco para manter o atual): ")
        data_nascimento = input("Digite a nova data de nascimento (deixe em branco para manter o atual): ")
        documento = input("Digite o novo número de documento (deixe em branco para manter o atual): ")

        query = {"_id": ObjectId(id_usuario)}
        update = {"$set": {}}

        if nome:
            update["$set"]["nome"] = nome
        if email:
            update["$set"]["email"] = email
        if data_nascimento:
            try:
                datetime.strptime(data_nascimento, "%Y-%m-%d")
                update["$set"]["data_nascimento"] = data_nascimento
            except ValueError:
                print("Erro: A data de nascimento é inválida. Use o formato aaaa-mm-dd.")
                return
        if documento:
            update["$set"]["documento"] = documento

        try:
            result = usuarios_collection.update_one(query, update)
            if result.modified_count == 1:
                print(f"Usuário com ID {id_usuario} atualizado com sucesso!")
            elif result.matched_count == 0:
                print(f"Usuário com ID {id_usuario} não encontrado.")
            else:
                print(f"Usuário com ID {id_usuario} não foi atualizado.")
        except pymongo.errors.OperationFailure as e:
            print(f"Erro ao atualizar usuário: {e}")
        except pymongo.errors.PyMongoError as e:
            print(f"Erro de conexão com o banco de dados: {e}")
    except KeyboardInterrupt:
        print("Operação cancelada pelo usuário.")
    except EOFError:
        print("Erro: Entrada de dados inválida.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def deletar_usuario():
    try:
        id_usuario = input("Digite o ID do usuário a ser deletado: ")
        if not id_usuario:
            print("Erro: O ID do usuário é obrigatório.")
            return

        try:
            ObjectId(id_usuario)
        except Exception as e:
            print("Erro: O ID do usuário é inválido.")
            return

        query = {"_id": ObjectId(id_usuario)}

        try:
            resultado = usuarios_collection.delete_one(query)
        except pymongo.errors.PyMongoError as e:
            print(f"Erro de conexão com o banco de dados: {e}")
            return

        if resultado.deleted_count == 1:
            print(f"Usuário com ID {id_usuario} deletado com sucesso!")
        elif resultado.deleted_count == 0:
            print(f"Usuário com ID {id_usuario} não encontrado.")
        else:
            print(f"Erro ao deletar usuário: {resultado}")
    except KeyboardInterrupt:
        print("Operação cancelada pelo usuário.")
    except EOFError:
        print("Erro: Entrada de dados inválida.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def emprestar_livro():
    try:
        livro_id = input("Digite o ID do livro a ser emprestado: ")
        if not livro_id:
            print("Erro: O ID do livro é obrigatório.")
            return

        try:
            ObjectId(livro_id)
        except ValueError:
            print("Erro: O ID do livro é inválido.")
            return

        usuario_id = input("Digite o ID do usuário: ")
        if not usuario_id:
            print("Erro: O ID do usuário é obrigatório.")
            return

        try:
            ObjectId(usuario_id)
        except ValueError:
            print("Erro: O ID do usuário é inválido.")
            return

        try:
            livro = livros_collection.find_one({"_id": ObjectId(livro_id)})
        except pymongo.errors.PyMongoError as e:
            print(f"Erro de conexão com o banco de dados: {e}")
            return

        if livro is None:
            print(f"Livro ID {livro_id} não encontrado.")
            return

        if not livro['disponivel'] or livro['quantidade'] <= 0:
            print("Livro não disponível para empréstimo.")
            return

        emprestimo = {
            "livro_id": ObjectId(livro_id),
            "usuario_id": ObjectId(usuario_id),
            "data_emprestimo": datetime.now(),
            "devolvido": False
        }

        try:
            emprestimos_collection.insert_one(emprestimo)
        except pymongo.errors.PyMongoError as e:
            print(f"Erro ao inserir empréstimo: {e}")
            return
        
        try:
            livros_collection.update_one({"_id": ObjectId(livro_id)}, {"$inc": {"quantidade": -1}})
        except pymongo.errors.PyMongoError as e:
            print(f"\nErro ao atualizar livro: {e}")
            return
        
        livro_atualizado = livros_collection.find_one({"_id": ObjectId(livro_id)})

        if livro_atualizado['quantidade'] == 0:
            try:
                livros_collection.update_one({"_id": ObjectId(livro_id)}, {"$set": {"disponivel": False}})
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro ao atualizar livro: {e}")
                return
        
        print(f"Livro ID {livro_id} emprestado ao usuário ID {usuario_id}.")
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except EOFError:
        print("\nErro: Entrada de dados inválida. Tente novamente.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

def devolver_livro():
    try:
        emprestimo_id = input("Digite o ID do empréstimo: ")
        if not emprestimo_id:
            print("\nErro: O ID do empréstimo é obrigatório.")
            return
        
        try:
            ObjectId(emprestimo_id)
        except ValueError:
            print("\nErro: O ID do empréstimo é inválido.")
            return
        
        try:
            emprestimo = emprestimos_collection.find_one({"_id": ObjectId(emprestimo_id)})
        except pymongo.errors.PyMongoError as e:
            print(f"\nErro de conexão com o banco de dados: {e}")
            return
        
        if emprestimo is None:
            print(f"\nEmpréstimo ID {emprestimo_id} não encontrado.")
            return
        
        if emprestimo['devolvido']:
            print(f"\nEmpréstimo ID {emprestimo_id} já foi finalizado.")
            return
        
        try:
            livros_collection.update_one({"_id": emprestimo['livro_id']}, {"$inc": {"quantidade": 1}})
        except pymongo.errors.PyMongoError as e:
            print(f"\nErro ao atualizar livro: {e}")
            return
        
        try:
            emprestimos_collection.update_one({"_id": ObjectId(emprestimo_id)}, {"$set": {"devolvido": True}})
        except pymongo.errors.PyMongoError as e:
            print(f"\nErro ao atualizar empréstimo: {e}")
            return

        try:
            livro = livros_collection.find_one({"_id": emprestimo['livro_id']})
        except pymongo.errors.PyMongoError as e:
            print(f"\nErro de conexão com o banco de dados: {e}")
            return
        
        if livro['quantidade'] > 0:
            try:
                livros_collection.update_one({"_id": emprestimo['livro_id']}, {"$set": {"disponivel": True}})
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro ao atualizar livro: {e}")
                return
            
        print(f"\nEmpréstimo ID {emprestimo_id} finalizado e livro ID {livro['_id']} devolvido com sucesso.")
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except EOFError:
        print("\nErro: Entrada de dados inválida. Tente novamente.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")

def listar_emprestimos():
    try:
        data_inicial = input("\nDigite a data inicial (aaaa-mm-dd): ")
        if not data_inicial:
            print("\nErro: A data inicial é obrigatória.")
            return
        
        try:
            data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
        except ValueError:
            print(f"\nErro: A data inicial é inválida. Use o formato aaaa-mm-dd.")
            return
        
        data_final = input("Digite a data final (aaaa-mm-dd): ")
        if not data_final:
            print("\nErro: A data final é obrigatória.")
            return
        
        try:
            data_final = datetime.strptime(data_final, "%Y-%m-%d")
        except ValueError:
            print(f"\nErro: A data final é inválida. Use o formato aaaa-mm-dd.")
            return
        
        if data_inicial > data_final:
            print("\nErro: A data inicial deve ser anterior a data final.")
            return

        data_inicial = data_inicial.replace(hour=0, minute=0, second=0)
        data_final = data_final.replace(hour=23, minute=59, second=59)

        try:
            emprestimos = emprestimos_collection.find({
                "data_emprestimo": {
                    "$gte": data_inicial,
                    "$lte": data_final
                }
            })
        except pymongo.errors.PyMongoError as e:
            print(f"\nErro de conexão com o banco de dados: {e}")
            return

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
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except EOFError:
        print("\nErro: Entrada de dados inválida. Tente novamente.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
try:

    while True:
        print("\nMenu Biblioteca: (utilize os números para escolher uma opção).\n")
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

except KeyboardInterrupt:
    print("\n\nOperação cancelada pelo usuário.")