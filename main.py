from pymongo import MongoClient # importar pymongo para acessar o MongoDB
from bson.objectid import ObjectId # importar o ObjectId para manipular os IDs
from datetime import datetime # importar a biblioteca datetime para trabalhar com datas
from datetime import timedelta # importar timedelta para colocar prazo na devolução
import configparser
import pymongo # importar pymongo para trabalhar com o MongoDB

def main():
    while True:
        try:
            # Carrega as configurações a partir do arquivo config.ini para obter a senha do MongoDB
            config = configparser.ConfigParser()
            config.read('config.ini')

            senha = config['conexao']['senha']

            try:
                # Tentativa de conexão com o MongoDB usando a URI. A senha é passada de forma dinâmica. 
                uri = f"mongodb+srv://x1ngue:{senha}@cluster0.uwf0d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
                client = MongoClient(uri)
                db = client['biblioteca'] # Seleciona o banco de dados 'biblioteca'
                db_l = client.list_database_names()
                print("\nConexão bem-sucedida ao MongoDB!\n")
                break
            except Exception as e:
                # Caso a tentativa de conexão falhe, o erro será exibido e o loop reinicia
                print("Erro ao conectar ao MongoDB:", e)
        except KeyboardInterrupt:
            # Caso o usuário pressione Ctrl+C, o loop e encerrado
            print("\nOperação cancelada pelo usuário.")
            exit()
            
# Criar a coleção 'livros' e 'usuarios' e 'emprestimos' no banco de dados 'biblioteca'
    livros_collection = db['livros']
    usuarios_collection = db['usuarios']
    emprestimos_collection = db['emprestimos']

# Função para adicionar livros e solicita as informações do novo livro
    def adicionar_livro():
        try:
            titulo = input("\nDigite o título do livro: ")
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
                raise ValueError(f"\nErro: Já existe um livro cadastrado com o ISBN '{isbn}'.")

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
            print(f"\nLivro '{titulo}' adicionado com sucesso.")

        except ValueError as e:
            print(f"\nErro: {e}.")

        except Exception as e:
            print(f"\nErro inesperado: {e}")

    def listar_livros():
        livros = livros_collection.find()

        encontrado = False
        for livro in livros:
            print(f"\nID: '{livro['_id']}', Título: '{livro['titulo']}', Autor: '{livro['autor']}', Gênero: '{livro['genero']}', "
                f"Ano: '{livro['ano']}', ISBN: '{livro['isbn']}', Quantidade: '{livro['quantidade']}', Disponível: '{livro['disponivel']}'.")
            
            encontrado = True

        if not encontrado:
            print("\n\nNenhum livro encontrado.\n")

# Função para atualizar livros seguindo o mesmo padrão           
    def atualizar_livro():
        try:
            livro_id = input("\nDigite o ID do livro que deseja atualizar: ")
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
                print(f"\nLivro ID '{livro_id}' atualizado com sucesso.")
        except pymongo.errors.PyMongoError as e:
            print(f"Erro d conexão com o banco de dados: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

# Função para excluir livros seguindo o mesmo padrão
    def excluir_livro():
        try:
            livro_id = input("\nDigite o ID do livro que deseja excluir: ")
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
                    print(f"\nLivro ID '{livro_id}' excluído com sucesso.")
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro d conexão com o banco de dados: {e}")
            except Exception as e:
                print(f"\nErro inesperado: {e}")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

# Função para cadastrar usuários seguindo o mesmo padrão
    def cadastrar_usuario():
        try:
            nome = input("\nDigite o nome do usuário: ")
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
                if usuarios_collection.find_one({"email": email}):
                    print(f"\nErro: Já existe um usuário cadastrado com o email '{email}'.")
                    return
                if usuarios_collection.find_one({"documento": documento}):
                    print(f"\nErro: Já existe um usuário cadastrado com o documento '{documento}'.")
                    return
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro d conexão com o banco de dados: {e}")
                return

            usuario = {
                "nome": nome,
                "email": email,
                "data_nascimento": data_nascimento,
                "documento": documento
            }

            try:
                usuarios_collection.insert_one(usuario)
                print(f"\nUsuário '{nome}' cadastrado com sucesso.")
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro d conexão com o banco de dados: {e}")
            except Exception as e:
                print(f"\nErro inesperado: {e}")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"Erro inesperado: {e}")

# Função para consultar usuários seguindo o mesmo padrão
    def listar_usuarios():
        try:
            try:
                usuarios = usuarios_collection.find()
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro de conexão com o banco de dados: {e}")
                return

            if usuarios is None:
                print("\nErro: Não foi possível recuperar a lista de usuários.")
                return

            for usuario in usuarios:
                try:
                    if '_id' not in usuario:
                        print("\nErro: O usuário não tem ID.")
                        continue

                    if 'nome' not in usuario:
                        print(f"\nErro: O usuário '{usuario['_id']}' não tem nome.")
                        continue

                    if 'email' not in usuario:
                        print(f"\nErro: O usuário '{usuario['_id']}' não tem e-mail.")
                        continue

                    data_nascimento = usuario.get('data_nascimento', "Não informada")
                    documento = usuario.get('documento', "Não informado")

                    print(f"\nID: '{usuario['_id']}', Nome: '{usuario['nome']}', E-mail: '{usuario['email']}', Data de Nascimento: '{data_nascimento}', Documento: '{documento}'.")
                except Exception as e:
                    print(f"\nErro inesperado ao processar o usuário '{usuario['_id']}': {e}")
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida.")
        except Exception as e:
            print(f"Erro inesperado: {e}")

# Função para atualizar usuários seguindo o mesmo padrão
    def atualizar_usuario():
        try:
            id_usuario = input("\nDigite o ID do usuário a ser atualizado: ")
            if not id_usuario:
                print("\nErro: O ID do usuário é obrigatório.")
                return

            try:
                ObjectId(id_usuario)
            except ValueError:
                print("\nErro: O ID do usuário é inválido.")
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
                    print("\nErro: A data de nascimento é inválida. Use o formato aaaa-mm-dd.")
                    return
            if documento:
                update["$set"]["documento"] = documento

            try:
                result = usuarios_collection.update_one(query, update)
                if result.modified_count == 1:
                    print(f"\nUsuário com ID '{id_usuario}' atualizado com sucesso!")
                elif result.matched_count == 0:
                    print(f"\nUsuário com ID '{id_usuario}' não encontrado.")
                else:
                    print(f"\nUsuário com ID '{id_usuario}' não foi atualizado.")
            except pymongo.errors.OperationFailure as e:
                print(f"\nErro ao atualizar usuário: {e}")
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro de conexão com o banco de dados: {e}")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

# Função para deletar usuários seguindo o mesmo padrão
    def deletar_usuario():
        try:
            id_usuario = input("\nDigite o ID do usuário a ser deletado: ")
            if not id_usuario:
                print("\nErro: O ID do usuário é obrigatório.")
                return

            try:
                ObjectId(id_usuario)
            except Exception as e:
                print("\nErro: O ID do usuário é inválido.")
                return

            query = {"_id": ObjectId(id_usuario)}

            try:
                resultado = usuarios_collection.delete_one(query)
            except pymongo.errors.PyMongoError as e:
                print(f"Erro de conexão com o banco de dados: {e}")
                return

            if resultado.deleted_count == 1:
                print(f"\nUsuário com ID '{id_usuario}' deletado com sucesso!")
            elif resultado.deleted_count == 0:
                print(f"\nUsuário com ID '{id_usuario}' não encontrado.")
            else:
                print(f"\nErro ao deletar usuário: '{resultado}'.")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

# Função para emprestar livros seguindo o mesmo padrão
    def emprestar_livro():
        try:
            livro_id = input("\nDigite o ID do livro a ser emprestado: ")
            if not livro_id:
                print("\nErro: O ID do livro é obrigatório.")
                return

            try:
                ObjectId(livro_id)
            except ValueError:
                print("\nErro: O ID do livro é inválido.")
                return

            usuario_id = input("\nDigite o ID do usuário: ")
            if not usuario_id:
                print("\nErro: O ID do usuário é obrigatório.")
                return

            try:
                ObjectId(usuario_id)
            except ValueError:
                print("\nErro: O ID do usuário é inválido.")
                return

            try:
                livro = livros_collection.find_one({"_id": ObjectId(livro_id)})
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro de conexão com o banco de dados: {e}")
                return

            if livro is None:
                print(f"\nLivro ID '{livro_id}' não encontrado.")
                return

            if not livro['disponivel'] or livro['quantidade'] <= 0:
                print("\nLivro não disponível para empréstimo.")
                return

            # Add validation for loan period
            data_emprestimo = datetime.now()
            data_devolucao = data_emprestimo + timedelta(days=30)

            emprestimo = {
                "livro_id": ObjectId(livro_id),
                "usuario_id": ObjectId(usuario_id),
                "data_emprestimo": data_emprestimo,
                "data_devolucao": data_devolucao,
                "devolvido": False
            }

            try:
                emprestimos_collection.insert_one(emprestimo)
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro ao inserir empréstimo: {e}")
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
            
            print(f"\nLivro ID '{livro_id}' emprestado ao usuário ID '{usuario_id}'. Data de emprestimo: '{data_emprestimo.strftime('%Y-%m-%d %H:%M:%S')}', Data de devolução: '{data_devolucao.strftime('%Y-%m-%d %H:%M:%S')}'.")
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

# Função para devolver livros seguindo o mesmo padrão
    def devolver_livro():
        try:
            emprestimo_id = input("\nDigite o ID do empréstimo: ")
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
                print(f"\nEmpréstimo ID '{emprestimo_id}' não encontrado.")
                return
            
            if emprestimo['devolvido']:
                print(f"\nEmpréstimo ID '{emprestimo_id}' já foi finalizado.")
                return
            
            if not emprestimo['devolvido']:
                if datetime.now() > emprestimo['data_devolucao']:
                    print(f"\nErro: O livro está atrasado. Por favor, devolva-o imediatamente.")
            
            try:
                livros_collection.update_one({"_id": emprestimo['livro_id']}, {"$inc": {"quantidade": 1}})
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro ao atualizar livro: {e}")
                return
            
            try:
                data_devolucao = datetime.now()
                emprestimos_collection.update_one({"_id": ObjectId(emprestimo_id)}, {"$set": {"devolvido": True, "data_devolucao": data_devolucao}})
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
            
            print(f"\nEmpréstimo ID '{emprestimo_id}' finalizado e livro ID '{livro['_id']}' devolvido com sucesso na data de '{data_devolucao.strftime('%Y-%m-%d %H:%M:%S')}'.")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

# Função para pesquisar empréstimos seguindo o padrão
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
            
            data_final = input("\nDigite a data final (aaaa-mm-dd): ")
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
                print("\nNenhum empréstimo encontrado.")  
            else:
                for emprestimo in emprestimos_lista:
                    print("\n------------------------")
                    print(f"ID Empréstimo: '{emprestimo['_id']}', Livro ID: '{emprestimo['livro_id']}', Usuário ID: '{emprestimo['usuario_id']}', Devolvido: '{emprestimo['devolvido']}'.")
                    print("Dados do empréstimo:")
                    print(f"  Data do empréstimo: '{emprestimo['data_emprestimo'].strftime('%Y-%m-%d %H:%M:%S')}'.")
                    print(f"  Livro: '{emprestimo['livro_id']}'.")
                    print(f"  Usuário: '{emprestimo['usuario_id']}'.")
                    print(f"  Devolvido: '{emprestimo['devolvido']}'.")
                    if emprestimo['devolvido']:
                        if 'data_devolucao' in emprestimo:
                            print(f"  Data da devolução: '{emprestimo['data_devolucao'].strftime('%Y-%m-%d %H:%M:%S')}'.")
                            data_prazo_devolucao = emprestimo['data_emprestimo'] + timedelta(days=30)
                            if emprestimo['data_devolucao'] > data_prazo_devolucao:
                                atraso = (emprestimo['data_devolucao'] - data_prazo_devolucao).days
                                print(f"\nLivro devolvido com atraso de '{atraso}' dia(s).")
                            else:
                                antecedencia = (data_prazo_devolucao - emprestimo['data_devolucao']).days
                                print(f"\nO livro foi devolvido dentro do prazo em '{emprestimo['data_devolucao'].strftime('%Y-%m-%d %H:%M:%S')}', com '{antecedencia}' dia(s) de antecedência.")
                        else:
                            data_devolucao = datetime.now()
                            emprestimos_collection.update_one({"_id": emprestimo['_id']}, {"$set": {"data_devolucao": data_devolucao}})
                            print("\nData da devolução: ", data_devolucao.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        data_prazo_devolucao = emprestimo['data_emprestimo'] + timedelta(days=30)
                        dias_restantes = (data_prazo_devolucao - datetime.now()).days
                        if dias_restantes <= 0:
                            print("\nDevolução pendente! Prazo de devolução expirado.")
                        else:
                            print(f"\nDevolução pendente! Restam '{dias_restantes}' dia(s) para o prazo de devolução.")
                    print("------------------------")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

    # Função para pesquisar empréstimos de um determinado usuário
    def consultar_emprestimos_usuario():
        try:
            usuario_id = input("\nDigite o ID do usuário: ")
            if not usuario_id:
                print("\nErro: O ID do usuário é obrigatório.")
                return
            
            try:
                ObjectId(usuario_id)
            except ValueError:
                print("\nErro: O ID do usuário é inválido.")
                return
            
            try:
                emprestimos = emprestimos_collection.find({"usuario_id": ObjectId(usuario_id)})
            except pymongo.errors.PyMongoError as e:
                print(f"\nErro de conexão com o banco de dados: {e}")
                return
            
            emprestimos = list(emprestimos)

            if len(emprestimos) == 0:
                print("\nNenhum empréstimo encontrado para o usuário especificado.")
            else:
                for emprestimo in emprestimos:
                    print("\n------------------------")
                    print(f"ID Empréstimo: '{emprestimo['_id']}', Livro ID: '{emprestimo['livro_id']}', Usuário ID: '{emprestimo['usuario_id']}', Devolvido: '{emprestimo['devolvido']}'.")
                    print("Dados do empréstimo:")
                    print(f"  Data do empréstimo: '{emprestimo['data_emprestimo'].strftime('%Y-%m-%d %H:%M:%S')}'.")
                    print(f"  Livro: '{emprestimo['livro_id']}'.")
                    print(f"  Usuário: '{emprestimo['usuario_id']}'.")
                    print(f"  Devolvido: '{emprestimo['devolvido']}'.")
                    if emprestimo['devolvido']:
                        if 'data_devolucao' in emprestimo:
                            print(f"  Data da devolução: '{emprestimo['data_devolucao'].strftime('%Y-%m-%d %H:%M:%S')}'.")
                            data_prazo_devolucao = emprestimo['data_emprestimo'] + timedelta(days=30)
                            if emprestimo['data_devolucao'] > data_prazo_devolucao:
                                atraso = (emprestimo['data_devolucao'] - data_prazo_devolucao).days
                                print(f"\nLivro devolvido com atraso de '{atraso}' dia(s).")
                            else:
                                antecedencia = (data_prazo_devolucao - emprestimo['data_devolucao']).days
                                print(f"\nO livro foi devolvido dentro do prazo em '{emprestimo['data_devolucao'].strftime('%Y-%m-%d %H:%M:%S')}', com '{antecedencia}' dia(s) de antecedência.")
                        else:
                            data_devolucao = datetime.now()
                            emprestimos_collection.update_one({"_id": emprestimo['_id']}, {"$set": {"data_devolucao": data_devolucao}})
                            print("\nData da devolução: ", data_devolucao.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        data_prazo_devolucao = emprestimo['data_emprestimo'] + timedelta(days=30)
                        dias_restantes = (data_prazo_devolucao - datetime.now()).days
                        if dias_restantes <= 0:
                            print("\nDevolução pendente! Prazo de devolução expirado.")
                        else:
                            print(f"\nDevolução pendente! Restam '{dias_restantes}' dia(s) para o prazo de devolução.")
                    print("------------------------")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

    # Função para pesquisar empréstimos vencidos
    def consultar_usuarios_emprestimos_vencidos():
        try:
            data_atual = datetime.now()
            emprestimos_vencidos = emprestimos_collection.find({
                "data_devolucao": {"$lt": data_atual},
                "devolvido": False
            })

            usuarios_emprestimos_vencidos = []
            for emprestimo in emprestimos_vencidos:
                usuario_id = emprestimo["usuario_id"]
                if usuario_id not in usuarios_emprestimos_vencidos:
                    usuarios_emprestimos_vencidos.append(usuario_id)

            if len(usuarios_emprestimos_vencidos) == 0:
                print("\nNenhum usuário com empréstimo vencido encontrado.")
            else:
                for usuario_id in usuarios_emprestimos_vencidos:
                    print(f"\nUsuário ID: '{usuario_id}' está com emprestimos vencidos.")
                    emprestimos_vencidos_usuario = emprestimos_collection.find({
                        "usuario_id": usuario_id,
                        "data_devolução": {"$lt": data_atual},
                        "devolvido": False
                    })
                    for emprestimo in emprestimos_vencidos_usuario:
                        print(f"  - Empréstimo ID: '{emprestimo['_id']}', Livro ID: '{emprestimo['livro_id']}', Data de Empréstimo: '{emprestimo['data_emprestimo']}', Data de Devolução: '{emprestimo['data_devolucao']}'.")
        except KeyboardInterrupt:
            print("\n\nOperação cancelada pelo usuário.")
        except EOFError:
            print("\nErro: Entrada de dados inválida. Tente novamente.")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

    # Função para escolher uma opção
    def escolher_opcao(resposta_usuario, funcao):
        if resposta_usuario == 's':
            funcao()
        elif resposta_usuario == 'n':
            print("\nVoltando ao menu principal.")
        else:
            print("\nOpcão inválida. Tente novamente.")

    try:
        # Menu inicial e escolha de opções
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
            print("12. Listar Empréstimos por Usuário")
            print("13. Listar Usuários com Empréstimos Vencidos")
            print("14. Sair")

            opcao = input("\nEscolha uma opção: ")

            if opcao == '1':
                print("\nVocê selecionou a opção 'Adicionar Livro'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, adicionar_livro)
                    
            elif opcao == '2':
                print("\nVocê selecionou a opção 'Listar Livros'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, listar_livros)

            elif opcao == '3':
                print("\nVocê selecionou a opção 'Atualizar Livro'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, atualizar_livro)

            elif opcao == '4':
                print("\nVocê selecionou a opção 'Excluir Livro'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, excluir_livro)

            elif opcao == '5':
                print("\nVocê selecionou a opção 'Cadastrar Usuário'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, cadastrar_usuario)

            elif opcao == '6':
                print("\nVocê selecionou a opção 'Listar Usuários'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, listar_usuarios)

            elif opcao == '7':
                print("\nVocê selecionou a opção 'Atualizar Usuário'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, atualizar_usuario)

            elif opcao == '8':
                print("\nVocê selecionou a opção 'Deletar Usuário'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, deletar_usuario)

            elif opcao == '9':
                print("\nVocê selecionou a opção 'Emprestar Livro'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, emprestar_livro)

            elif opcao == '10':
                print("\nVocê selecionou a opção 'Devolver Livro'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, devolver_livro)

            elif opcao == '11':
                print("\nVocê selecionou a opção 'Listar Empréstimos'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, listar_emprestimos)

            elif opcao == '12':
                print("\nVocê selecionou a opção 'Consultar Empréstimo por Usuário'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, consultar_emprestimos_usuario)

            elif opcao == '13':
                print("\nVocê selecionou a opção 'Listar Usuários com Empréstimos Vencidos'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                escolher_opcao(resposta, consultar_usuarios_emprestimos_vencidos)

            elif opcao == '14':
                print("\nVocê selecionou a opção 'Sair'. Deseja continuar? (s/n)\n>> ", end='')
                resposta = input().lower()
                if resposta == 's':
                    print("\nEncerrando o sistema.\n")
                    break
                elif resposta == 'n':
                    print("\nVoltando ao menu principal")
                else:
                    print("\nOpção inválida. Tente novamente.")
            else:
                print("Opção inválida. Tente novamente.")

    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")

if __name__ == '__main__':
    main()