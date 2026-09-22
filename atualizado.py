from enum import Enum

# --- ARMAZENAMENTO NA MEMÓRIA ---
# Dicionário principal que vai guardar todos os equipamentos enquanto o programa roda
ativos_ti = {}

def carregar_ativos():
    try:
        with open("ativos.txt", "r") as f:
            for linha in f:
                # O .split(",", 5) garante que cortamos apenas as primeiras 5 vírgulas
                pedacos = linha.strip().split(",", 5)
                
                if len(pedacos) == 6:
                    id_str = pedacos[0]
                    nome = pedacos[1]
                    responsavel = pedacos[2]
                    setor = pedacos[3]
                    tipo = pedacos[4]
                    texto_vuls = pedacos[5] # Pega o texto final das vulnerabilidades
                    
                    lista_vuls = []
                    
                    # Verifica se o texto é diferente de "Nenhuma"
                    if texto_vuls != "Nenhuma":
                        # Separa as vulnerabilidades se houver mais de uma (separadas por ", ")
                        vuls_separadas = texto_vuls.split(", ")
                        for v_str in vuls_separadas:
                            # Tenta encontrar onde começa o parênteses do status
                            if " (" in v_str and v_str.endswith(")"):
                                # Corta o texto na última ocorrência de " ("
                                partes = v_str.rsplit(" (", 1)
                                descricao = partes[0]
                                status = partes[1].replace(")", "") # Remove o último parênteses
                                
                                lista_vuls.append({
                                    "descricao": descricao,
                                    "categoria": "Carregada do txt", # Dado não salvo no txt
                                    "severidade": "Não informada",   # Dado não salvo no txt
                                    "status": status
                                })
                    
                    # Convertendo o id_str para número e guardando no dicionário
                    ativos_ti[int(id_str)] = {
                        "nome": nome,
                        "responsavel": responsavel,
                        "setor": setor,
                        "tipo": tipo,
                        "vulnerabilidades": lista_vuls # Agora recebe a lista preenchida
                    }
    except FileNotFoundError:
        # Se o ficheiro não existir, o programa simplesmente ignora e continua
        pass

# Estrutura de enumeração para as categorias de ativos, facilitando a validação e evitando erros de digitação
class CategoriasAtivos(Enum):
    COMPUTADORES = 1
    NOTEBOOKS = 2
    SERVIDORES = 3
    SWITCHES = 4    

# --- FUNÇÕES (As ações que o sistema sabe executar) ---
def cadastrar_ativo():
    print("\n--- Cadastro de novo ativo ---")
    
    # 1. Entrada de Dados: Tenta pedir o ID e converte para número.
    try:
        id_ativo = int(input("Digite o ID do ativo (apenas números): "))    
    except ValueError:
        print("Erro: ID inválido. O ativo não será cadastrado.")
        return

    # ---Trava de segurança: Verifica se o ID já existe no dicionário.
    if id_ativo in ativos_ti:
        print("Erro: ID já cadastrado. O ativo não será cadastrado.")
        return  

    # 2. Entrada de Dados: Recebe os textos normais digitados pelo usuário
    nome = input("Digite o nome do ativo: ") 
    responsavel = input("Digite o nome do responsável pelo ativo: ")
    setor = input("Digite o setor do ativo: ")

    # 3. Entrada de Dados e Decisão Lógica: Pede o tipo de ativo e tenta buscar o nome da categoria no Enum.
    try:
        print("\nCategorias de ativos disponíveis:")
        print("1. Computadores | 2. Notebooks | 3. Servidores | 4. Switches")
        tipo_numero = int(input("Digite o número correspondente ao tipo de ativo: "))

        nome_categoria = CategoriasAtivos(tipo_numero).name
    except ValueError:  
        print("Erro: Categoria inválida ou valor incorreto. O ativo não será cadastrado.")
        return

    # 5. Processamento: Salva as informações dentro do dicionário principal
    ativos_ti[id_ativo] = {
        "nome": nome,
        "responsavel": responsavel,
        "setor": setor,
        "tipo": nome_categoria,
        "vulnerabilidades": []  
    }

    # 6. Processamento: Grava os mesmos dados no arquivo de texto 'ativos.txt'. 
    with open("ativos.txt", "a") as f:
        f.write(f"{id_ativo},{nome},{responsavel},{setor},{nome_categoria},Nenhuma\n")
        
    # 7. Saída: Confirmação visual para o usuário
    print("Ativo cadastrado com sucesso e salvo em ativos.txt!")

def listar_ativo():
    print("\n--- Consulta de ativos ---")
    
    busca = input("Digite o ID ou o Nome do ativo que deseja consultar: ")
    
    ativo_encontrado = None
    id_ativo_encontrado = 0
    
    if busca.isdigit():
        id_busca = int(busca)
        if id_busca in ativos_ti:
            ativo_encontrado = ativos_ti[id_busca]
            id_ativo_encontrado = id_busca
    else:
        for id_ativo, dados in ativos_ti.items():
            if dados['nome'] == busca:
                ativo_encontrado = dados
                id_ativo_encontrado = id_ativo
                break 
                
    if ativo_encontrado:
        print(f"\n[ID: {id_ativo_encontrado}] - {ativo_encontrado['nome']}:")
        print(f"Responsável: {ativo_encontrado['responsavel']}")
        print(f"Setor: {ativo_encontrado['setor']}")
        print(f"Tipo: {ativo_encontrado['tipo']}")
        
        vulnerabilidades = ativo_encontrado['vulnerabilidades']
        
        if len(vulnerabilidades) == 0:
            print("Vulnerabilidades: Nenhuma registrada.")
        else:
            print(f"\n--- Vulnerabilidades encontradas ({len(vulnerabilidades)}) ---")
            for contador, vulnerabilidade in enumerate(vulnerabilidades, start=1):
                print(f"{contador}. {vulnerabilidade['descricao']} - Status: {vulnerabilidade['status']}")
    else:
        print("\nErro: Nenhum ativo encontrado com esta busca.")

def cadastrar_vulnerabilidade():
    print("\n--- Cadastrar Vulnerabilidade ---")
    
    try:
        id_busca = int(input("Digite o ID do ativo para registrar a vulnerabilidade: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    if id_busca in ativos_ti:
        print(f"Ativo selecionado: {ativos_ti[id_busca]['nome']}")
        
        descricao = input("Descrição do problema: ")
        categoria = input("Categoria/Tipo (ex: Senha fraca, Software desatualizado): ")
        severidade = input("Severidade (Baixa, Média, Alta, Crítica): ")
        status = input("Status (Aberta, Em tratamento, Corrigida, Risco Aceito): ")
        
        nova_vulnerabilidade = {
            "descricao": descricao,
            "categoria": categoria,
            "severidade": severidade,
            "status": status
        }
        
        ativos_ti[id_busca]["vulnerabilidades"].append(nova_vulnerabilidade)
        with open("ativos.txt", "w") as f:
            for id_ativo, dados in ativos_ti.items():
                vuls_formatadas = ", ".join([f"{v['descricao']} ({v['status']})" for v in dados['vulnerabilidades']]) if dados['vulnerabilidades'] else "Nenhuma"
                linha = f"{id_ativo},{dados['nome']},{dados['responsavel']},{dados['setor']},{dados['tipo']},{vuls_formatadas}\n"
                f.write(linha)
        print("\nVulnerabilidade vinculada com sucesso ao ativo!") 
    else:
        print("\nErro: Nenhum ativo encontrado com este ID.")

def atualizar_ativo():                                          
    print("\n--- Atualizar Ativo ---")

    try:
        id_busca = int(input("Digite o ID do ativo que deseja atualizar: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    if id_busca in ativos_ti:
        ativo = ativos_ti[id_busca]
        print(f"Ativo encontrado: {ativo['nome']}")

        novo_responsavel = input(f"Digite o novo responsável do ativo ({ativo['nome']}): ")
        novo_setor = input(f"Digite o novo setor do ativo ({ativo['nome']}): ")

        ativos_ti[id_busca]['responsavel'] = novo_responsavel
        ativos_ti[id_busca]['setor'] = novo_setor

        with open("ativos.txt", "w") as f:
            for id_ativo, dados in ativos_ti.items():
                vuls_formatadas = ", ".join([f"{v['descricao']} ({v['status']})" for v in dados['vulnerabilidades']]) if dados['vulnerabilidades'] else "Nenhuma"
                f.write(f"{id_ativo},{dados['nome']},{dados['responsavel']},{dados['setor']},{dados['tipo']},{vuls_formatadas}\n")

        print("\nAtivo atualizado com sucesso!")

    else:
        print("\nErro: Ativo não encontrado.")
            
def excluir_ativo():
    print("\nExcluindo do banco de dados...")

    try:
        id_busca = int(input("Digite o ID do ativo que deseja excluir: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    if id_busca in ativos_ti:
        del ativos_ti[id_busca]

        with open("ativos.txt", "w") as f:
            for id_ativo, dados in ativos_ti.items():
                vuls_formatadas = ", ".join([f"{v['descricao']} ({v['status']})" for v in dados['vulnerabilidades']]) if dados['vulnerabilidades'] else "Nenhuma"
                f.write(f"{id_ativo},{dados['nome']},{dados['responsavel']},{dados['setor']},{dados['tipo']},{vuls_formatadas}\n")

        print("\nAtivo excluído com sucesso!")
    else:
        print("\nErro: Ativo não encontrado.")

def atualizar_vulnerabilidade():
    try:
        print("\n--- Atualização de vulnerabilidade ---")
        id_busca = int(input("Digite o ID do ativo para atualizar uma vulnerabilidade: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    if id_busca in ativos_ti:
        vulnerabilidades = ativos_ti[id_busca]['vulnerabilidades']
        
        if len(vulnerabilidades) == 0:
            print("Nenhuma vulnerabilidade cadastrada para este ativo.")
            return
            
        print(f"\nVulnerabilidades encontradas no ativo {ativos_ti[id_busca]['nome']}:")
        for contador, vulnerabilidade in enumerate(vulnerabilidades, start=1):
            print(f"{contador}. {vulnerabilidade['descricao']} - Status Atual: {vulnerabilidade['status']}")
            
        try:
            escolha = int(input("\nDigite o número da vulnerabilidade que deseja atualizar: "))
        except ValueError:
            print("Erro: Entrada inválida. Digite apenas o número correspondente.")
            return
        
        if 1 <= escolha <= len(vulnerabilidades):
            novo_status = input("Digite o novo status (Aberta, Em tratamento, Corrigida, Risco Aceito): ")
            vulnerabilidades[escolha - 1]['status'] = novo_status
            
            with open("ativos.txt", "w") as f:
                for id_ativo, dados in ativos_ti.items():
                    vuls_formatadas = ", ".join([f"{v['descricao']} ({v['status']})" for v in dados['vulnerabilidades']]) if dados['vulnerabilidades'] else "Nenhuma"
                    f.write(f"{id_ativo},{dados['nome']},{dados['responsavel']},{dados['setor']},{dados['tipo']},{vuls_formatadas}\n")
            
            print("\nStatus da vulnerabilidade atualizado com sucesso!")
        else:
            print("Erro: Número inválido.")
    else:
        print("\nErro: Nenhum ativo encontrado com este ID.")

# Carrega os dados do ficheiro ativos.txt para o dicionário na memória
carregar_ativos()

# --- MENU PRINCIPAL (Laço de Repetição) ---
opcao = ""

while opcao != "7":
    print("\n--- Sistema de Inventário de Cibersegurança ---")          
    print("1. Cadastrar Ativo")
    print("2. Listar Ativo")
    print("3. Atualizar Ativo")
    print("4. Excluir Ativo")
    print("5. Cadastrar Vulnerabilidade")
    print("6. Atualizar Status de Vulnerabilidade")
    print("7. Sair")

    opcao = input("Escolha uma opcao (1 a 7): ")

    if opcao == "1":
        cadastrar_ativo()
    elif opcao == "2":
        listar_ativo()
    elif opcao == "3":
        atualizar_ativo()
    elif opcao == "4":
        excluir_ativo() 
    elif opcao == "5":
        cadastrar_vulnerabilidade()
    elif opcao == "6":
        atualizar_vulnerabilidade()
    elif opcao == "7":
        print("\nSaindo do sistema...")
    else:
        print("\nOpção inválida. Por favor, escolha uma opção válida.")