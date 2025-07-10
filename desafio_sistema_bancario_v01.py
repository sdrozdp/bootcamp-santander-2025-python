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
  
def validar_chave(tipo_chave, chave_pix):
    if tipo_chave == '1':
        return validar_cpf(chave_pix)
    
    elif tipo_chave == '2':
        return validar_cnpj(chave_pix)
    
    elif tipo_chave == '3':
        return validar_email(chave_pix)
    
    elif tipo_chave == '4':
        return validar_telefone(chave_pix)
    
    else:
        return False

def informar_valor():
    
    while True:
        entrada = input("Informe o valor: R$ ")
        
        entrada = entrada.replace(",", ".")
        try:
            valor = float(entrada)

            if valor <= 0:
                print("Valor inválido! O valor deve ser numérico e positivo.")
            else:
                break
        except ValueError:
            print("Valor inválido! O valor deve ser numérico, positivo e pode conter vírgula como separador decimal.")
    return valor  

menu = """
***** Bem-vindo ao Sistema Bancário *****

*** Menu Principal ***

[1] Depósito
[2] Saque
[3] PIX
[4] Extrato
[0] Sair

>>> Digite a opção desejada: """

saldo = 0
LIMITE_SAQUE = 500
TOTAL_SAQUES_PERMITIDOS = 3
LIMITE_PIX = 500
extrato = ""
saques_realizados = 0

while True:

    print("\n" + "="*30)
    
    opcao = input(menu)

    if opcao == '1':
        valor = informar_valor()

        if valor > 0:
            saldo += valor
            data_hora = datetime.datetime.now()
            data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')
            extrato += f"Depósito: R$ {valor:.2f} - {data_hora_formatada}\n"
            print(f"Depósito realizado com sucesso! Saldo atual: R$ {saldo:.2f}")

        else:
            print("Valor de depósito inválido. O valor deve ser positivo.")

    elif opcao == '2':

        valor = informar_valor()

        excedeu_saques = saques_realizados >= TOTAL_SAQUES_PERMITIDOS

        excedeu_saldo = valor > saldo

        excedeu_limite = valor > LIMITE_SAQUE

        valor_invalido = valor <= 0

        if excedeu_saques:
            print("Número máximo de saques excedido.")

        elif valor_invalido:
            print("Valor de saque inválido. O valor deve ser positivo.")
            
        elif excedeu_saldo:
            print("Saldo insuficiente para realizar o saque.")
            
        elif excedeu_limite:
            print(f"Valor do saque excede o limite de R$ {LIMITE_SAQUE:.2f}.")  
            
        else:
            saldo -= valor
            saques_realizados += 1

            data_hora = datetime.datetime.now()
            data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M:%S')

            extrato += f"Saque: R$ {valor:.2f} - {data_hora_formatada}\n"

            print(f"Saque realizado com sucesso! Saldo atual: R$ {saldo:.2f}")

    elif opcao == '3':
        valor = informar_valor()
        tipo_chave = input("Digite o tipo de chave PIX desejada - [1]CPF [2]CNPJ [3]Email [4]Telefone: ").strip()
        chave_pix = input("Digite a chave PIX: ")
        
        excedeu_limite = valor > LIMITE_PIX

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
            
    elif opcao == '4':
        
        if extrato:
            print("\nExtrato:")
            print(f"\n{extrato}")
            print(f"Saldo atual: R$ {saldo:.2f}")

        else:
            print("Nenhuma transação realizada até o momento.")
      
    elif opcao == '0':
        print("Obrigado por utilizar nosso sistema. Até logo!")
        break

    else:
        print("Opção inválida. Por favor, escolha uma opção válida do menu.")
        print()  # Linha em branco para melhor formatação do menu

