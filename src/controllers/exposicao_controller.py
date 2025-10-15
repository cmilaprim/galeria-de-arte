# src/controllers/exposicao_controller.py
from datetime import datetime
from src.database.manager import DatabaseManager
from src.models.exposicao_model import Exposicao, StatusExposicao
from src.models.participacao_exposicao_model import ParticipacaoExposicao

class ExposicaoController:
    def __init__(self):
        self.db = DatabaseManager()

    def _valida_data(self, s: str, campo: str):
        if not s:
            return
        try:
            datetime.strptime(s, "%d/%m/%Y")
        except Exception:
            raise ValueError(f"{campo} deve estar no formato DD/MM/YYYY")

    def salvar(self, id_exposicao, nome, tema, localizacao, status_texto, data_inicio, data_fim, data_cadastro, descricao):
        try:
            if not nome:
                return False, "Nome é obrigatório."

            self._valida_data(data_inicio, "Data Início")
            self._valida_data(data_fim, "Data Fim")
            self._valida_data(data_cadastro, "Data Cadastro")

            status_enum = None
            for s in StatusExposicao:
                if s.value == status_texto:
                    status_enum = s
                    break
            if status_enum is None:
                status_enum = StatusExposicao.PLANEJADA

            exposicao = Exposicao(
                id_exposicao,
                nome,
                tema,
                localizacao,
                status_enum,
                data_inicio,
                data_fim,
                data_cadastro,
                descricao
            )

            if id_exposicao:
                ok, msg = self.db.atualizar_exposicao(exposicao)
                return ok, msg
            else:
                ok, resultado = self.db.inserir_exposicao(exposicao)
                if ok:
                    return True, "Exposição cadastrada com sucesso."
                else:
                    return False, resultado

        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            return False, f"Erro ao salvar exposição: {e}"
        
    def buscar(self, filtros: dict = None):
        if not filtros:
            return self.db.listar_exposicoes()
        # normaliza: strips
        filtros_limpos = {k: (v.strip() if isinstance(v, str) else v) for k, v in (filtros.items() if filtros else []) if v}
        return self.db.buscar_exposicoes(filtros_limpos)


    def listar(self):
        return self.db.listar_exposicoes()

    def carregar(self, id_exposicao):
        return self.db.obter_exposicao(id_exposicao)

    def buscar(self, filtros: dict):
        return self.db.buscar_exposicoes(filtros)

    def get_status(self):
        return [s.value for s in StatusExposicao]

    # participação (obra <-> exposição)
    def adicionar_obra(self, id_exposicao: int, id_obra: int, observacao: str = None):
        p = ParticipacaoExposicao(id=None, id_exposicao=id_exposicao, id_obra=id_obra, observacao=observacao)
        return self.db.inserir_participacao_exposicao(p)

    def remover_obra(self, id_exposicao: int, id_obra: int):
        return self.db.remover_participacao_exposicao(id_exposicao, id_obra)

    def listar_obras(self, id_exposicao: int):
        return self.db.listar_participacoes_por_exposicao(id_exposicao)

    def verificar_participacao(self, id_exposicao: int, id_obra: int):
        return self.db.verificar_participacao(id_exposicao, id_obra)
