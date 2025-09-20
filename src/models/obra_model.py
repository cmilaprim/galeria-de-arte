from datetime import date
from enum import Enum

class StatusObra(Enum):
    DISPONIVEL = "Disponível"
    ALUGADA = "Alugada"
    VENDIDA = "Vendida"
    EMPRÉSTIMO = "Empréstimo"
    EM_EXPOSICAO = "Em Exposição"
    
class ObraDeArte:
    def __init__(self, id_obra, titulo, ano, artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem=None, data_cadastro=None):
        self.__id_obra = id_obra
        self.__titulo = titulo
        self.__ano = ano
        self.__artista = artista
        self.__tipo = tipo
        self.__tecnica = tecnica
        self.__dimensoes = dimensoes
        self.__localizacao = localizacao
        self.__preco = preco
        self.__status = status
        self.__imagem = imagem
        self.__data_cadastro = data_cadastro if data_cadastro else date.today()

    
    @property
    def id_obra(self):
        return self.__id_obra
    
    @property
    def titulo(self):
        return self.__titulo

    @titulo.setter
    def titulo(self, valor):
        if not valor:
            raise ValueError("Título não pode estar vazio!")
        self.__titulo = valor

    @property
    def ano(self):
        return self.__ano

    @ano.setter
    def ano(self, valor):
        if int(valor) < 0:
            raise ValueError("Ano inválido!")
        self.__ano = int(valor)

    @property
    def artista(self):
        return self.__artista
    
    @artista.setter
    def artista(self, artista):
        if not artista:
            raise ValueError("Artista não pode estar vazio!")
        self.__artista = artista
    
    @property
    def tipo(self):
        return self.__tipo
    
    @tipo.setter
    def tipo(self, valor):
        if not valor:
            raise ValueError("Tipo não pode estar vazio!")
        self.__tipo = valor
    
    @property
    def tecnica(self):
        return self.__tecnica
    
    @tecnica.setter
    def tecnica(self, valor):
        if not valor:
            raise ValueError("Técnica não pode estar vazia!")
        self.__tecnica = valor
    
    @property
    def dimensoes(self):
        return self.__dimensoes
    
    @dimensoes.setter
    def dimensoes(self, valor):
        if not valor:
            raise ValueError("Dimensões não podem estar vazias!")
        self.__dimensoes = valor
    
    @property
    def localizacao(self):
        return self.__localizacao
    
    @localizacao.setter
    def localizacao(self, valor):
        if not valor:
            raise ValueError("Localização não pode estar vazia!")
        self.__localizacao = valor
    
    @property
    def preco(self):
        return self.__preco
    
    @preco.setter
    def preco(self, valor):
        if valor < 0:
            raise ValueError("Preço não pode ser negativo!")
        self.__preco = valor
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, valor):
        if not isinstance(valor, StatusObra):
            raise ValueError("Status deve ser uma instância de StatusObra")
        self.__status = valor
    
    @property
    def imagem(self):
        return self.__imagem
    
    @imagem.setter
    def imagem(self, valor):
        self.__imagem = valor

    @property
    def data_cadastro(self):
        return self.__data_cadastro