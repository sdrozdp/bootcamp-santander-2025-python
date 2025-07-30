from abc import ABC, abstractclassmethod, abstractproperty
import re   
import datetime
import textwrap

class Cliente():
    def __init__(self, endereco):
        self._endereco = endereco  # Endereço completo do cliente
        self._contas = []  # Lista de contas associadas ao cliente

    def __str__(self):
        return f"{self.__class__.__name__}:{', '.join([f'{chave}={valor}' for chave, valor in self.__dict__.items()])}"
    
    @classmethod
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco=None):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento
    
    def __str__(self):
        return f"{self.__class__.__name__}:{', '.join([f'{chave}={valor}' for chave, valor in self.__dict__.items()])}"    

    @property  
    def cpf(self):
        return self._cpf
    
    @property  
    def nome(self):
        return self._nome
    
    @property  
    def data_nascimento(self):
        return self._data_nascimento

class Conta():
    def __init__(self, cliente, numero, agencia='0001'):
        self._saldo = 0.0
        self._agencia = agencia  # Agência padrão'
        self._numero = numero
        self._cliente = cliente
        self._historico = Historico()  # Histórico de transações
        self._status = 'ativo'  # Status da conta

    def __str__(self):
        return f"{self.__class__.__name__}:{', '.join([f'{chave}={valor}' for chave, valor in self.__dict__.items()])}" 
  
    @classmethod
    def nova_conta(cls, cliente, numero, agencia='0001'):
        return cls(numero, agencia, cliente)
     
    @property  
    def saldo(self):
        return self._saldo
    
    @property  
    def numero(self):
        return self._numero
    
    @property  
    def agencia(self):
        return self._agencia
    
    @property  
    def cliente(self):
        return self._cliente
    
    @property  
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif valor > 0:
            self._saldo -= valor
            print(f"\n=== Saque de R$ {valor:.2f} realizado com sucesso na conta {self._numero}! ===")
            return True
        
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False
       
    def depositar(self, valor):     
        if valor > 0:
            self._saldo += valor
            print(f"\n=== Depósito de R$ {valor:.2f} realizado com sucesso na conta {self._numero}! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        
        return True
    
        
class ContaCorrente(Conta):
    def __init__(self, cliente, numero, agencia, limite=500, limite_saques=3, limite_pix=5, limite_valor_pix=1000):
        super().__init__(cliente, numero, agencia)
        self._limite = limite
        self._limite_saques = limite_saques
        self._limite_pix = limite_pix
        self._limite_valor_pix = limite_valor_pix

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes 
             if transacao["tipo"] == Saque.__name__]
            )
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print(f"@@@ Operação falhou! O valor do saque excede o limite de R$ {self._limite:.2f}. @@@")

        elif excedeu_saques:
            print(f"@@@ Operação falhou! Número máximo de saques ({self._limite_saques}) excedido. @@@")

        else:
            return super().sacar(valor)

        return False 
 
    def transferir_pix(self, valor):
        numero_pix = len(
            [transacao for transacao in self.historico.transacoes 
                if transacao["tipo"] == Transferencia_Origem.__name__]
            )
        excedeu_limite_valor_pix = valor > self._limite_valor_pix
        excedeu_limite_num_pix = numero_pix >= self._limite_pix

        if excedeu_limite_valor_pix:
            print(f"@@@ Operação falhou! O valor do PIX excede o limite de R$ {self._limite:.2f}. @@@")

        elif excedeu_limite_num_pix:
            print(f"@@@ Operação falhou! Número máximo de saques ({self._limite_saques}) excedido. @@@")

        else:
            self._saldo -= valor
            print(f"\n=== PIX de R$ {valor:.2f} realizado com sucesso na conta {self._numero}! ===")
            return True

        return False

    def receber_pix(self, valor):
        if valor > 0:
            self._saldo += valor
        else:
            return False
        
        return True

class Historico:
    def __init__(self):
        self._transacoes = []  # Lista de transações realizadas 

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao._valor,
                "data_hora": datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
           
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Transferencia_Origem(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.transferir_pix(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Transferencia_Destino(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.receber(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Banco:
    def __init__(self):
        self._clientes = []  # Lista de clientes do banco
        self._contas = []  # Lista de contas do banco
        self._agencias = {"0001","0002","0003" }  # Conjunto de agências válidas
    
    @property
    def contas(self):
        return self._contas
    
    @property
    def clientes(self):
        return self._clientes
    
    @property
    def agencias(self):
        return self._agencias

    def adicionar_cliente(self, cpf, nome, data_nascimento, endereco):

        cliente = PessoaFisica(cpf, nome, data_nascimento, endereco)
        
        self.clientes.append(cliente)  

    def criar_conta(self, cpf, numero, agencia):

        cliente = self.buscar_cliente(cpf)

        if cliente:
            conta = ContaCorrente(cliente, numero, agencia)
            cliente.adicionar_conta(conta) 
            self.contas.append(conta)
            print(f"Conta corrente criada com sucesso para o cliente {cliente.nome}. Número da conta: {numero}, Agência: {agencia}")
        
        else:
            print("@@@ Cliente não encontrado. Por favor, cadastre o cliente primeiro! @@@")       
        
    def buscar_cliente(self, cpf):
        for cliente in self.clientes:
            if cliente.cpf == cpf:
                return cliente
        return None
     
    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
            return
        else: 
            print("Clientes cadastrados:")
            for cliente in self._clientes:
                print(f"CPF: {cliente._cpf}, Nome: {cliente._nome}, Data de Nascimento: {cliente._data_nascimento}, Endereço: {cliente._endereco}")

    def listar_contas(self):
        if not self.contas:
            print("Nenhuma conta cadastrada.")
            return
        else:
            print("Contas cadastradas:")
            for conta in self.contas:
                print(f"Agência: {conta.agencia}, Número da Conta: {conta.numero}, Cliente: {conta.cliente.nome}, Saldo: R$ {conta.saldo:.2f}, Status: {conta._status}")

    def agencia_valida(self, agencia):
        valido = agencia.isdigit() and len(agencia) == 4 and agencia in self.agencias
        if not valido:
            print("Agência inválida! Verifique o número da agência.") 
        return valido
    
    def filtrar_conta(self, numero, agencia):
        
        conta = next(
                (conta for conta in self._contas if conta.numero == numero and conta.agencia == agencia), None)
        return conta   
           
    def validar_conta(self, numero, agencia):
            
            conta = next(
                    (conta for conta in self._contas if conta.numero == numero and conta.agencia == agencia), None)
            if conta:
                return True
            
            return False   

    def registrar_deposito(self, numero, agencia, valor):
    
        conta = self.filtrar_conta(numero, agencia)
        
        if conta:
            cliente = conta.cliente
            transacao = Deposito(valor)
            cliente.realizar_transacao(conta, transacao)
        
    def registrar_saque(self, numero, agencia, valor):
        
        conta = self.filtrar_conta(numero, agencia)
        
        if conta:
            cliente = conta.cliente
            transacao = Saque(valor)
            cliente.realizar_transacao(conta, transacao)

    def realizar_pix(self, numero, agencia, valor, chave):
        
        conta = self.filtrar_conta(numero, agencia)
        
        if conta:
            cliente = conta.cliente
            transacao = Transferencia_Origem(valor)
            cliente.realizar_transacao(conta, transacao)
    
    def exibir_extrato(self, numero, agencia):
        
        conta = self.filtrar_conta(numero, agencia) 

        if conta:
            transacoes = conta.historico.transacoes
            if transacoes:
                print(f"\n=== Extrato da Conta {conta.numero} - Agência {conta.agencia} ===")
                for transacao in conta.historico.transacoes:
                    print(f"{transacao['data_hora']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
                print(f"\nSaldo: R$ {conta.saldo:.2f}") 
            else:
                print("Nenhuma transação realizada.")                        

class InterfaceBancaria:
    def __init__(self):
        self._banco = Banco()
    
    @property
    def banco(self):
        return self._banco
    
    def validar_cpf(self, cpf):
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
        
    def validar_telefone(telefone):
        padrao = r'^\d{10,11}$'  # Aceita números com 10 ou 11 dígitos
        return re.match(padrao, telefone) is not None
    
    def validar_email(email):
        padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        return re.match(padrao, email) is not None
      
    def validar_chave(self, tipo_chave, chave):
        if tipo_chave == '1':
            return self.validar_cpf(chave)
        
        elif tipo_chave == '2':
            return self.validar_cnpj(chave)
        
        elif tipo_chave == '3':
            return self.validar_email(chave)
        
        elif tipo_chave == '4':
            return self.validar_telefone(chave)
        
        else:
            return False

    def exibir_menu(self):
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
            [0] Sair

            >>> Digite a opção desejada: """
        
        opção = input(textwrap.dedent(menu)) 

        return opção

    def informar_data(self):
                   
        try:
            data_nascimento = input("Data de nascimento(dd/mm/aaaa): ").strip()
            data_formatada = datetime.datetime.strptime(data_nascimento, '%d/%m/%Y')
            return data_formatada.strftime('%d/%m/%Y')  # Retorna a data formatada como string
        
        except ValueError:
            print("Data inválida. Por favor, digite uma data no formato dd/mm/aaaa.")  
            return None
    
    def informar_agencia(self):
        agencia = input("Informe a agência: ")
        if self.banco.agencia_valida(agencia): 
            return agencia
        else:
            print("\n@@@ Agência inválida! Informe uma agência válida! @@@")
        return None

    def informar_conta(self, agencia):
         
        try:
            numero = int(input("Informe o número da conta: "))
        except: 
            return None
        else:
            if self.banco.validar_conta(numero, agencia):
                return numero
        return None

    def realizar_transacao(self, tipo):

        agencia = self.informar_agencia()
        if agencia:
            numero = self.informar_conta(agencia)
            if numero:          
                try:
                    valor = float(input("Informe o valor: ").replace(',', '.'))
                    if valor <= 0:
                        print("@@@ Valor inválido! O valor deve ser numérico, positivo e maior que zero.")
                except ValueError:
                    print("@@@ Valor inválido! O valor deve ser numérico, positivo, maior que zero.")
                else:
                    if tipo == "DEPOSITO":
                        self.banco.registrar_deposito(numero, agencia, valor)  
                    elif tipo == "SAQUE":
                        self.banco.registrar_saque(numero, agencia, valor)
            else:
                print("\n@@@ Conta inválida! Informe uma conta válida! @@@")
        else:
            print("\n@@@ Agência inválida! Informe uma agência válida! @@@")

    def realizar_pix(self):

        agencia = self.informar_agencia()
        if agencia:
            numero = self.informar_conta(agencia)
            if numero:          
                try:
                    valor = float(input("Informe o valor: ").replace(',', '.'))
                    if valor <= 0:
                        print("@@@ Valor inválido! O valor deve ser numérico, positivo e maior que zero.")
                except ValueError:
                    print("@@@ Valor inválido! O valor deve ser numérico, positivo, maior que zero.")
                else:
                    tipo_chave = input("Digite o tipo de chave PIX desejada - [1]CPF [2]CNPJ [3]Email [4]Telefone: ").strip()
                    chave_pix = input("Digite a chave PIX: ")  
                    tipo_chave_valida = tipo_chave in ['1', '2', '3', '4']
                    chave_pix_valida = self.validar_chave(tipo_chave, chave_pix)

                    if not tipo_chave_valida:
                        print("\n@@@ Tipo de chave PIX inválido. Por favor, escolha uma opção válida: [1]CPF [2]CNPJ [3]Email [4]Telefone. @@@")
                    elif not chave_pix_valida:
                        print("\n@@@ Chave PIX inválida. Por favor, verifique a chave e tente novamente. @@@")
                    else:
                        self.banco.realizar_pix(numero, agencia, valor, chave_pix)
            else:
                print("\n@@@ Conta inválida! Informe uma conta válida! @@@")
        else:
            print("\n@@@ Agência inválida! Informe uma agência válida! @@@")

    def criar_cliente(self):

        cpf = input("Informe o CPF do cliente: ").strip().replace('.', '').replace('-', '')
        
        if self.validar_cpf(cpf):
            nome = input("Informe o nome do cliente: ").strip()
            data_nascimento = self.informar_data()
            if data_nascimento:
                endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ").strip()
                self.banco.adicionar_cliente(cpf, nome, data_nascimento, endereco)
                print(f"Cliente {nome} cadastrado com sucesso!")
        else:
            print("CPF inválido! Verifique o número do CPF.")

    def criar_conta(self):

        numero = len(self.banco.contas) + 1
        agencia = self.informar_agencia()

        if agencia:
            cpf = input("Informe o CPF do titular: ").strip().replace('.', '').replace('-', '')

            if self.validar_cpf(cpf):
                self.banco.criar_conta(cpf, numero, agencia)
            else:
                print("@@@ CPF inválido! Informe um CPF válido! @@@")
        else:
            print("@@@ Agência inválida! Informe uma agência válida! @@@")                            

    def listar_clientes(self):
        self.banco.listar_clientes()

    def listar_contas(self):
        self.banco.listar_contas()

    def exibir_extrato(self):
        
        agencia = self.informar_agencia()
        if agencia:
            numero = self.informar_conta(agencia)
            if numero:    
                self.banco.exibir_extrato(numero, agencia)
            else:
                print("\n@@@ Conta inválida! Informe uma conta válida! @@@")
        else:
            print("\n@@@ Agência inválida! Informe uma agência válida! @@@")
  
    def menu(self):

        while True:      
            opcao = self.exibir_menu()

            if opcao == '1': # Depósito

                self.realizar_transacao("DEPOSITO")
                
            elif opcao == '2': # Saque

                self.realizar_transacao("SAQUE")    
            
            elif opcao == '3': # PIX

                self.realizar_pix()
                    
            elif opcao == '4': # Extrato
                
                self.exibir_extrato()

            elif opcao == '5': # Cadastrar Usuário

                self.criar_cliente()   
                
            elif opcao == '6': # Criar Conta Corrente

                self.criar_conta()

            elif opcao == '7': # Listar Usuários

                self.listar_clientes()
            
            elif opcao == '8': # Listar Contas Correntes

                self.listar_contas()

          #  elif opcao == '9': # Inativar Conta Corrente

          #      self.inativar_conta()
            
            elif opcao == '0':
                print("Obrigado por utilizar nosso sistema. Até logo!")
                break

            else:
                print("Opção inválida. Por favor, escolha uma opção válida do menu.")

            if opcao in ['0','1', '2', '3', '4', '5', '6', '7', '8', '9']:
                input("\nPressione qualquer tecla para continuar...")

    def main(self):
        self.menu()

sistema = InterfaceBancaria()
sistema.main()