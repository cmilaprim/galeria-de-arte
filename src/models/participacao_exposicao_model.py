# src/models/participacao_exposicao_model.py
from datetime import date

class ParticipacaoExposicao:
    def __init__(self, id=None, id_exposicao=None, id_obra=None, data_inclusao=None, observacao=None):
        self.__id = id
        self.__id_exposicao = id_exposicao
        self.__id_obra = id_obra
        self.__data_inclusao = data_inclusao or date.today().strftime("%d/%m/%Y")
        self.__observacao = observacao

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, v):
        self.__id = v

    @property
    def id_exposicao(self):
        return self.__id_exposicao

    @id_exposicao.setter
    def id_exposicao(self, v):
        self.__id_exposicao = v

    @property
    def id_obra(self):
        return self.__id_obra

    @id_obra.setter
    def id_obra(self, v):
        self.__id_obra = v

    @property
    def data_inclusao(self):
        return self.__data_inclusao

    @data_inclusao.setter
    def data_inclusao(self, v):
        self.__data_inclusao = v

    @property
    def observacao(self):
        return self.__observacao

    @observacao.setter
    def observacao(self, v):
        self.__observacao = v
