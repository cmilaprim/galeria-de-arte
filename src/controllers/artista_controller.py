from datetime import datetime
from ..database.manager import DatabaseManager
from ..models.artista_model import Artista, StatusArtista

class ArtistaController:
    def __init__(self):
        self.db = DatabaseManager()

    # util
    def _valida_data(self, s: str, campo: str):
        try:
            datetime.strptime(s, "%d/%m/%Y")
        except Exception:
            raise ValueError(f"{campo} deve estar no formato DD/MM/YYYY.")

    def salvar(self, id_artista, nome, nascimento, nacionalidade,
               especialidade, status_str, data_cadastro, biografia):
        # valida obrigatórios
        if not nome or not nome.strip():               return False, "Nome é obrigatório."
        if not nascimento or not nascimento.strip():   return False, "Nascimento é obrigatório."
        if not nacionalidade or not nacionalidade.strip(): return False, "Nacionalidade é obrigatória."
        if not especialidade or not especialidade.strip(): return False, "Especialidade é obrigatória."
        if not status_str or not status_str.strip():   return False, "Status é obrigatório."
        if not data_cadastro or not data_cadastro.strip(): return False, "Data de cadastro é obrigatória."
        if not biografia or not biografia.strip():     return False, "Biografia é obrigatória."

        # valida datas
        try:
            self._valida_data(nascimento.strip(), "Nascimento")
            self._valida_data(data_cadastro.strip(), "Data de cadastro")
        except ValueError as e:
            return False, str(e)

        try:
            status_enum = StatusArtista.ATIVO if status_str == "Ativo" else StatusArtista.INATIVO
            artista = Artista(
                int(id_artista) if id_artista else None,
                nome.strip(), nascimento.strip(), nacionalidade.strip(),
                especialidade.strip(), status_enum, data_cadastro.strip(), biografia.strip()
            )

            if artista.id_artista is None:
                new_id = self.db.inserir_artista(artista)
                return True, f"Artista '{artista.nome}' cadastrado (ID {new_id})."
            else:
                self.db.atualizar_artista(artista)
                return True, "Artista atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao salvar: {e}"

    def carregar(self, id_artista: int):
        return self.db.obter_artista(int(id_artista))

    def listar(self):
        return self.db.listar_artistas()

    def buscar(self, filtros: dict):
        return self.db.buscar_artistas(filtros)

    def get_status(self):
        return [s.value for s in StatusArtista]
