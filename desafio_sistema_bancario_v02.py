## Sistema Bancário com as seguintes funcionalidades: saque, depósito e extrato
## Requisitos do Sistema:
## 1. Um único usário do sistema bancário será considerado. Desta forma não será necessário solicitar agência e conta.
## 2. Apenas valores de depósito positivo serão permitidos. Se um valor negativo for informado, 
## uma mensagem de erro deve ser exibida.
## 3. Todos os depósitos e saques devem ser armazenados em uma variável e exibidos no extrato
## 4. Será permitido até 3 saques diários, com limite de R$500,00 por saque. 
## 5. Caso seja informado um valor maior que o limite, uma mensagem de erro deve ser exibida.
## 6. Caso o usuário tente realizar mais de 3 saques, uma mensagem de erro deve ser exibida.
## 7. Caso o usuário informe um valor de saque maior que o saldo, uma mensagem de erro deve ser exibida.
## 8. O extrato deve ser exibido ao usuário, mostrando todos os depósitos e saques realizados.
## 9. Além dos requisitos do desafio, foi incluida a funcionalidade de PIX.
## Para a transferência via PIX, o usuário deve informar o valor, o tipo de chave (CPF, CNPJ, Email ou Telefone)
## e a chave correspondente.

import datetime
import re
import textwrap

def menu():
    menu = """\n
        ***** Bem-vindo ao Sistema Bancário *****

        *********** Menu Principal ***********
        [1] Depósito
        [2] Saque
        [3] PIX
        [4] Extrato
        [5] Novo Usuário
        [6] Nova Conta
        [7] Listar Usuários
        [8] Listar Contas
        [9] Inativar Conta
        [0] Sair

        >>> Digite a opção desejada: """
    return input(textwrap.dedent(menu))

def validar_cpf(cpf):
    cpf = [int(char) for char in cpf if char.isdigit()]

    if len(cpf) != 11:
        return False

    # Evitar CPFs com todos os dígitos iguais (ex: 11111111111)
    if len(set(cpf)) == 1:
        return False

    # Primeiro dígito verificador
    soma = sum((10 - i) * cpf[i] for i in range(9))
    resto = (soma * 10) % 11

    dv1 = 0 if (resto == 10 | resto == 11) else resto
    
    if dv1 != cpf[9]:
        return False

    # Segundo dígito verificador
    soma = sum((11 - i) * cpf[i] for i in range(10))
    resto = (soma * 10) % 11

    dv2 = 0 if (resto == 10 | resto == 11) else resto

    if dv2 != cpf[10]:
        return False

    return True

def validar_cnpj(cnpj):
    cnpj = [int(char) for char in cnpj if char.isdigit()]

    if len(cnpj) != 14:
        return False

    # Evitar CNPJs com todos os dígitos iguais (ex: 11111111111111)
    if len(set(cnpj)) == 1:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum((5 - i) * cnpj[i] for i in range(4)) + sum((13 - i) * cnpj[i] for i in range(4, 12))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    if dv1 != cnpj[12]:
        return False

    # Cálculo do segundo dígito verificador
    soma = sum((6 - i) * cnpj[i] for i in range(5)) + sum((14 - i) * cnpj[i] for i in range(5, 12)) + dv1 * 2
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto

    if dv2 != cnpj[13]:
        return False

    return True

def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return re.match(padrao, email) is not None

def validar_telefone(telefone):
    padrao = r'^\d{10,11}$'  # Aceita números com 10 ou 11 dígitos

    return re.match(padrao, telefone) is not None
  
def validar_chave(tipo_chave, chave):
    if tipo_chave == '1':
        return validar_cpf(chave)
    
    elif tipo_chave == '2':
        return validar_cnpj(chave)
    
    elif tipo_chave == '3':
        return validar_email(chave)
    
    elif tipo_chave == '4':
        return validar_telefone(chave)
    
    else:
        return False

def informar_cpf():

    while True:
        numero_cpf = input("CPF (apenas números): ").strip()
        numero_cpf = ''.join(filter(str.isdigit, numero_cpf))  # Remove caracteres não numéricos

        if validar_chave('1', numero_cpf):
            break
        else:
            print("CPF inválido. Por favor, digite um CPF válido com 11 dígitos numéricos.")
    return numero_cpf

def informar_valor():
    
    valido = False
    entrada = input("Informe o valor: R$ ")      
    entrada = entrada.replace(",", ".")
    try:
        valor = float(entrada)

        if valor <= 0:
            print("Valor inválido! O valor deve ser numérico, positivo e maior que zero.")
        else:
            valido = True
    except ValueError:
        print("Valor inválido! O valor deve ser numérico, positivo, maior que zero e pode conter vírgula como separador decimal.")
    return valor, valido 

def informar_data():
    while True:
        data_nascimento = input("Data de nascimento(dd/mm/aaaa): ").strip()
        try:
            data_formatada = datetime.datetime.strptime(data_nascimento, '%d/%m/%Y')
            return data_formatada.strftime('%d/%m/%Y')  # Retorna a data formatada como string
        except ValueError:
            print("Data inválida. Por favor, digite uma data no formato dd/mm/aaaa.") 

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario['cpf'] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def depositar(saldo, valor, extrato):
    
    saldo += valor
    
    data_hora = datetime.datetime.now()
    data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')
    
    extrato += f"Depósito: R$ {valor:.2f} - {data_hora_formatada}\n"

    print(f"Depósito realizado com sucesso! Saldo atual: R$ {saldo:.2f}")
    
    return saldo, extrato

def sacar(*,saldo, valor, extrato, limite, numero_saques, limite_saques):

    excedeu_numero_saques = numero_saques >= limite

    excedeu_saldo = valor > saldo

    excedeu_valor_limite = valor > limite_saques
    
    if excedeu_numero_saques:
        print("Limite de saques diários atingido. Por favor, tente novamente amanhã.")
      
    elif excedeu_saldo:
        print("Saldo insuficiente para realizar o saque.")
        
    elif excedeu_valor_limite:
        print(f"Valor do saque excede o limite de R$ {LIMITE_SAQUE:.2f}.")  
        
    else:
        saldo -= valor
        numero_saques += 1

        data_hora = datetime.datetime.now()
        data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')

        extrato += f"Saque: R$ {valor:.2f} - {data_hora_formatada}\n"

        print(f"Saque realizado com sucesso! Saldo atual: R$ {saldo:.2f}")
    
    return saldo, extrato, numero_saques

def exibir_extrato(saldo, *, extrato):

    if extrato:
        print("\nExtrato:")
        print(f"\n{extrato}")
        print(f"Saldo atual: R$ {saldo:.2f}")

    else:
        print("Nenhuma transação realizada até o momento.")

def cadastrar_usuario(usuarios):

    print("\n*** Cadastro de Usuário ***")
    print("Por favor, informe os dados abaixo:")

    numero_cpf = informar_cpf()
    usuario = filtrar_usuario(numero_cpf, usuarios)

    if usuario:
        print("Já existe usuário cadastrado com o cpf informado.")
        return 

    # Solicita os dados do usuário
    nome = input("Nome Completo: ").strip()
    data_nascimento = informar_data()
    endereco = input("Endereço: ").strip()
    numero = input("Número: ").strip()
    bairro = input("Bairro: ").strip()
    cidade = input("Cidade: ").strip()
    estado = input("Estado: ").strip()
    sigla = input("Sigla do Estado: ").strip()
    endereco += f", {numero} - {bairro} - {cidade} - {estado}/{sigla}"  
    
    # Armazena os dados do usuário em uma lista
    usuarios.append({
        'cpf': numero_cpf,
        'nome': nome,
        'data_nascimento': data_nascimento,
        'endereco': endereco})
    print(f"Usuário {nome} cadastrado com sucesso.") 

def criar_conta(usuarios, contas):

    numero_cpf = informar_cpf()
        
    usuario_filtrado = filtrar_usuario(numero_cpf, usuarios) 
    if not usuario_filtrado:
        print("Usuário não cadastrado. Por favor, cadastre o usuário primeiro.")
        return

    # contas_cpf = [conta for conta in contas_correntes if conta['cpf'] == numero_cpf]

    nova_conta = len(contas) + 1  # Gera um número de conta sequencial
    contas.append(
        {
        'agencia': '0001',  # Exemplo de agência fixa
        'numero_conta': nova_conta,
        'usuario': usuario_filtrado,
        'saldo': 0,
        'extrato': "",
        'status': 'ativo'  # Status da conta
        })
    
    print(f"Conta corrente criada com sucesso para o usuário {usuario_filtrado['nome']}. Número da conta: {nova_conta}")

def listar_usuarios(usuarios):
    if usuarios:
        print("\nUsuários cadastrados:")
        for info in usuarios:
            print(f"CPF: {info['cpf']}, Nome: {info['nome']}, Data de Nascimento: {info['data_nascimento']}, Endereço: {info['endereco']}")
    else:
        print("Nenhum usuário cadastrado.")

def listar_contas(contas):
    if contas:
        print("\nContas correntes cadastradas:")
        for info in contas:
            print(f"Agência: {info['agencia']}, Número da Conta: {info['numero_conta']}, CPF: {info['usuario']['cpf']}, Status: {info['status']},  Saldo: R$ {info['saldo']:.2f}")
    else:
        print("Nenhuma conta corrente cadastrada.")

def realizar_pix(saldo, extrato, valor, *, limite):

    tipo_chave = input("Digite o tipo de chave PIX desejada - [1]CPF [2]CNPJ [3]Email [4]Telefone: ").strip()
    
    chave_pix = input("Digite a chave PIX: ")
    
    excedeu_limite = valor > limite

    tipo_chave_valida = tipo_chave in ['1', '2', '3', '4']

    chave_pix_valida = validar_chave(tipo_chave, chave_pix)
    
    if excedeu_limite:
        print(f"Valor do PIX excede o limite de R$ {LIMITE_PIX:.2f}.") 

    elif not tipo_chave_valida:
        print("Tipo de chave PIX inválido. Por favor, escolha uma opção válida: [1]CPF [2]CNPJ [3]Email [4]Telefone.")

    elif not chave_pix_valida:
        print("Chave PIX inválida. Por favor, verifique a chave e tente novamente.")

    else:
        # Realiza o PIX
        saldo -= valor
        
        data_hora = datetime.datetime.now()
        data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')

        extrato += f"PIX: R$ {valor:.2f} - {data_hora_formatada}\n"

        print(f"PIX realizado com sucesso! Saldo atual: R$ {saldo:.2f}")

    return saldo, extrato       
    
def inativar_conta(contas):

    if not contas:
        print("Nenhuma conta corrente cadastrada.")    
    else:
        try:
            numero_conta = int(input("Digite o número da conta corrente a ser inativada: ").strip())
        except ValueError:
            print("Número da conta inválido. Por favor, tente novamente.")
            
    # Verifica se a conta corrente existe
    contas_filtradas = [conta for conta in contas if conta['numero_conta'] == numero_conta]
    if contas_filtradas:
        if(contas_filtradas[0]['saldo'] != 0):
            print("Conta corrente não pode ser inativada, pois ainda possui saldo.")
        else:
            # Inativa a conta corrente
            contas_filtradas[0]['status'] = 'inativo'
            print(f"Conta corrente {numero_conta} inativada com sucesso.")
    else:
        print("Conta corrente não encontrada.") 

def main():
    
    LIMITE_PIX = 500
    LIMITE_SAQUE = 500
    TOTAL_SAQUES_PERMITIDOS = 3

    saldo = 0
    extrato = ""
    saques_realizados = 0  
    usuarios = []  # Dicionário para armazenar usuários
    contas = []  # Dicionário para armazenar contas correntes

    while True:
        
        opcao = menu()

        if opcao == '1': # Depósito

            valor, valor_valido = informar_valor()

            if valor_valido:
                
                saldo, extrato = depositar(saldo, valor, extrato)
            
        elif opcao == '2': # Saque

            valor, valor_valido = informar_valor()

            if valor_valido:

                saldo, extrato, saques_realizados = sacar(
                    saldo=saldo, 
                    valor=valor, 
                    extrato=extrato, 
                    limite=TOTAL_SAQUES_PERMITIDOS, 
                    numero_saques=saques_realizados,
                    limite_saques=LIMITE_SAQUE)      
        
        elif opcao == '3': # PIX

            valor, valor_valido = informar_valor()

            if valor_valido:

                saldo, extrato = realizar_pix(saldo, extrato, valor, limite=LIMITE_PIX)
                
        elif opcao == '4': # Extrato
            
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == '5': # Cadastrar Usuário

            cadastrar_usuario(usuarios)

        elif opcao == '6': # Criar Conta Corrente

            criar_conta(usuarios, contas)

        elif opcao == '7': # Listar Usuários

            listar_usuarios(usuarios)
        
        elif opcao == '8': # Listar Contas Correntes

            listar_contas(contas)

        elif opcao == '9': # Inativar Conta Corrente

            inativar_conta(contas)
        
        elif opcao == '0':
            print("Obrigado por utilizar nosso sistema. Até logo!")
            break

        else:
            print("Opção inválida. Por favor, escolha uma opção válida do menu.")

        if opcao in ['0','1', '2', '3', '4', '5', '6', '7', '8', '9']:
            input("Pressione qualquer tecla para continuar...")

main()