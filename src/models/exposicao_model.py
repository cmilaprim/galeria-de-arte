from enum import Enum
from datetime import date

class StatusExposicao(Enum):
    PLANEJADA = "Planejada"
    EM_CURSO = "Em Curso"
    FINALIZADA = "Finalizada"

class Exposicao:
    """
    Modelo de Exposição.
    """
    def __init__(self,
                 id_exposicao=None,
                 nome="",
                 tema="",
                 localizacao="",
                 status: StatusExposicao = StatusExposicao.PLANEJADA,
                 data_inicio=None,
                 data_fim=None,
                 data_cadastro=None,
                 descricao=None):
        self.__id_exposicao = id_exposicao
        self.__nome = nome
        self.__tema = tema
        self.__localizacao = localizacao
        if not isinstance(status, StatusExposicao):
            raise ValueError("status deve ser StatusExposicao")
        self.__status = status
        self.__data_inicio = data_inicio
        self.__data_fim = data_fim
        self.__data_cadastro = data_cadastro or date.today().strftime("%d/%m/%Y")
        self.__descricao = descricao

    @property
    def id_exposicao(self):
        return self.__id_exposicao

    @id_exposicao.setter
    def id_exposicao(self, v):
        self.__id_exposicao = v

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, v):
        self.__nome = v

    @property
    def tema(self):
        return self.__tema

    @tema.setter
    def tema(self, v):
        self.__tema = v

    @property
    def localizacao(self):
        return self.__localizacao

    @localizacao.setter
    def localizacao(self, v):
        self.__localizacao = v

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, v):
        if not isinstance(v, StatusExposicao):
            raise ValueError("status deve ser StatusExposicao")
        self.__status = v

    @property
    def data_inicio(self):
        return self.__data_inicio

    @data_inicio.setter
    def data_inicio(self, v):
        self.__data_inicio = v

    @property
    def data_fim(self):
        return self.__data_fim

    @data_fim.setter
    def data_fim(self, v):
        self.__data_fim = v

    @property
    def data_cadastro(self):
        return self.__data_cadastro

    @property
    def descricao(self):
        return self.__descricao

    @descricao.setter
    def descricao(self, v):
        self.__descricao = v
