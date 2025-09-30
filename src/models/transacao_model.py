from datetime import datetime
from enum import Enum

class TiposTransacao(Enum):
    VENDA = "Venda"
    ALUGUEL = "Aluguel"
    AQUISIÇÃO = "Aquisição"
    EMPRÉSTIMO = "Empréstimo"

class Transacao:
    def __init__(self, cliente, valor, tipo, data_transacao, observacoes=None, obras=None, id=None, data_cadastro=None):
        self.__id = id
        self.__cliente = cliente
        self.__valor = valor
        self.__tipo = tipo
        self.__data_transacao = data_transacao or datetime.now().date()
        self.__observacoes = observacoes or ""
        self.__obras = obras or []
        self.__data_cadastro = data_cadastro if data_cadastro else datetime.now()
        self.__devolucao = None  # atributo privado para devolução, inicializado como None

    # ---------- Propriedades existentes ----------
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, valor):
        self.__id = valor

    @property
    def cliente(self):
        return self.__cliente

    @cliente.setter
    def cliente(self, valor):
        if not valor:
            raise ValueError("Cliente é obrigatório.")
        self.__cliente = valor

    @property
    def valor(self):
        return self.__valor

    @valor.setter
    def valor(self, valor):
        if not valor:
            raise ValueError("Valor é obrigatório.")
        if valor < 0:
            raise ValueError("Valor não pode ser negativo.")
        self.__valor = valor

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        if not isinstance(valor, TiposTransacao) and valor not in [t.value for t in TiposTransacao]:
            raise ValueError("Tipo Inválido")
        self.__tipo = valor

    @property
    def data_transacao(self):
        return self.__data_transacao

    @data_transacao.setter
    def data_transacao(self, valor):
        if not valor:
            raise ValueError("Data da Transação é obrigatória.")
        self.__data_transacao = valor

    @property
    def observacoes(self):
        return self.__observacoes

    @observacoes.setter
    def observacoes(self, valor):
        self.__observacoes = valor or ""

    @property
    def obras(self):
        return self.__obras

    @obras.setter
    def obras(self, valor):
        self.__obras = valor or []

    @property
    def data_cadastro(self):
        return self.__data_cadastro

    @data_cadastro.setter
    def data_cadastro(self, valor):
        self.__data_cadastro = valor

    @property
    def devolucao(self):
        return self.__devolucao

    @devolucao.setter
    def devolucao(self, valor):
        self.__devolucao = valor  # pode ser None ou uma string/data
