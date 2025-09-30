from enum import Enum

class StatusArtista(Enum):
    ATIVO = "Ativo"
    INATIVO = "Inativo"

class Artista:
    def __init__(self, id_artista, nome, nascimento, nacionalidade,
                 especialidade, status: StatusArtista, data_cadastro, biografia):
        self.__id_artista = id_artista
        self.nome = nome
        self.nascimento = nascimento
        self.nacionalidade = nacionalidade
        self.especialidade = especialidade
        self.status = status
        self.data_cadastro = data_cadastro
        self.biografia = biografia

    @property
    def id_artista(self): return self.__id_artista

    # validações básicas
    @property
    def nome(self): return self.__nome
    @nome.setter
    def nome(self, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Nome é obrigatório.")
        self.__nome = v

    @property
    def nascimento(self): return self.__nascimento
    @nascimento.setter
    def nascimento(self, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Nascimento é obrigatório.")
        self.__nascimento = v

    @property
    def nacionalidade(self): return self.__nacionalidade
    @nacionalidade.setter
    def nacionalidade(self, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Nacionalidade é obrigatória.")
        self.__nacionalidade = v

    @property
    def especialidade(self): return self.__especialidade
    @especialidade.setter
    def especialidade(self, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Especialidade é obrigatória.")
        self.__especialidade = v

    @property
    def status(self): return self.__status
    @status.setter
    def status(self, v):
        if isinstance(v, StatusArtista):
            self.__status = v
        elif isinstance(v, str):
            v2 = v.strip().capitalize()
            if v2 not in ("Ativo", "Inativo"):
                raise ValueError("Status inválido.")
            self.__status = StatusArtista.ATIVO if v2 == "Ativo" else StatusArtista.INATIVO
        else:
            raise ValueError("Status inválido.")

    @property
    def data_cadastro(self): return self.__data_cadastro
    @data_cadastro.setter
    def data_cadastro(self, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Data de cadastro é obrigatória.")
        self.__data_cadastro = v

    @property
    def biografia(self): return self.__biografia
    @biografia.setter
    def biografia(self, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Biografia é obrigatória.")
        self.__biografia = v
