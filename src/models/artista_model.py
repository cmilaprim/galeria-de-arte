from enum import Enum
from datetime import date

class StatusArtista(Enum):
    ATIVO = "Ativo"
    INATIVO = "Inativo"

class Artista:
    def __init__(self, id_artista, nome, nascimento, nacionalidade,
                 especialidade, status: StatusArtista, data_cadastro=None, biografia=None):
        self.__id_artista = id_artista
        self.__nome = nome
        self.__nascimento = nascimento
        self.__nacionalidade = nacionalidade
        self.__especialidade = especialidade
        self.__status = status
        self.__data_cadastro = data_cadastro if data_cadastro else date.today()
        self.__biografia = biografia

    @property
    def id_artista(self):
        return self.__id_artista

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, valor):
        if not valor:
            raise ValueError("Nome é obrigatório.")
        self.__nome = valor

    @property
    def nascimento(self):
        return self.__nascimento

    @nascimento.setter
    def nascimento(self, valor):
        if not valor:
            raise ValueError("Nascimento é obrigatório.")
        self.__nascimento = valor

    @property
    def nacionalidade(self):
        return self.__nacionalidade

    @nacionalidade.setter
    def nacionalidade(self, valor):
        if not valor:
            raise ValueError("Nacionalidade é obrigatória.")
        self.__nacionalidade = valor

    @property
    def especialidade(self):
        return self.__especialidade

    @especialidade.setter
    def especialidade(self, valor):
        if not valor:
            raise ValueError("Especialidade é obrigatória.")
        self.__especialidade = valor

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, valor):
        if not isinstance(valor, StatusArtista):
            raise ValueError("Status deve ser uma instância de StatusArtista")
        self.__status = valor

    @property
    def data_cadastro(self):
        return self.__data_cadastro

    @data_cadastro.setter
    def data_cadastro(self, valor):
        self.__data_cadastro = valor

    @property
    def biografia(self):
        return self.__biografia

    @biografia.setter
    def biografia(self, valor):
        if not valor:
            raise ValueError("Biografia é obrigatória.")
        self.__biografia = valor
