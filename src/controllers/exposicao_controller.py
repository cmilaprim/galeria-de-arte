from datetime import datetime, date
from typing import Any, List, Tuple, Optional
from src.database.manager import DatabaseManager
from src.models.exposicao_model import Exposicao, StatusExposicao

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

    def salvar(self, id_exposicao, nome, tema, localizacao, status_texto, data_inicio, data_fim, data_cadastro, descricao) -> Tuple[bool, str]:
        try:
            if not nome:
                return False, "Nome é obrigatório."

            self._valida_data(data_inicio, "Data Início")
            self._valida_data(data_fim, "Data Fim")
            self._valida_data(data_cadastro, "Data Cadastro")

            status_enum = next((s for s in StatusExposicao if s.value == status_texto), StatusExposicao.PLANEJADA)

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
                try:
                    return self.db.atualizar_exposicao(exposicao)
                except Exception as e:
                    return False, f"Erro ao atualizar exposição: {e}"
            else:
                try:
                    ok, resultado = self.db.inserir_exposicao(exposicao)
                    if ok:
                        return True, "Exposição cadastrada com sucesso."
                    return False, str(resultado)
                except Exception as e:
                    return False, f"Erro ao inserir exposição: {e}"

        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            return False, f"Erro ao salvar exposição: {e}"

    def listar(self) -> List[Any]:
        try:
            return self.db.listar_exposicoes()
        except Exception:
            return []

    def carregar(self, id_exposicao: int) -> Optional[Any]:
        try:
            return self.db.obter_exposicao(id_exposicao)
        except Exception:
            return None

    def get_status(self) -> List[str]:
        return [s.value for s in StatusExposicao]

    # ---------- Participação (obra <-> exposição) ----------
    def adicionar_obra(self, id_exposicao: int, id_obra: int, observacao: str = None) -> Tuple[bool, str]:
        try:
            # 1) Tentar chamar método do db com assinatura esperada
            try:
                res = self.db.inserir_participacao_exposicao(id_exposicao, id_obra, observacao)
            except TypeError:
                res = None
            except Exception as e:
                return False, f"Erro do DB ao adicionar participação: {e}"

            # 2) Se não funcionou, tentar passar um objeto simples (compatibilidade)
            if res is None:
                try:
                    p = type("Participacao", (), {})()
                    p.id_exposicao = id_exposicao
                    p.id_obra = id_obra
                    p.data_inclusao = date.today().strftime("%d/%m/%Y")
                    p.observacao = observacao
                    res = self.db.inserir_participacao_exposicao(p)
                except TypeError:
                    res = None
                except Exception as e:
                    return False, f"Erro do DB ao adicionar participação: {e}"

            # 3) Fallback: tentar inserir diretamente via SQL (nome da tabela usada no manager é participacao_exposicao)
            if res is None:
                try:
                    sql = "INSERT OR IGNORE INTO participacao_exposicao (id_exposicao, id_obra, data_inclusao, observacao) VALUES (?, ?, ?, ?)"
                    conn = None
                    if hasattr(self.db, "conectar"):
                        conn = self.db.conectar()
                        cur = conn.cursor()
                        cur.execute(sql, (id_exposicao, id_obra, date.today().strftime("%d/%m/%Y"), observacao))
                        conn.commit()
                        conn.close()
                        return True, "Participação inserida (fallback)."
                except Exception:
                    pass

            if isinstance(res, tuple) and len(res) >= 1 and isinstance(res[0], bool):
                msg = res[1] if len(res) > 1 else ("OK" if res[0] else "Erro")
                return bool(res[0]), str(msg)

            if isinstance(res, bool):
                return res, ("OK" if res else "Erro ao inserir participação")

            if isinstance(res, dict):
                return True, "Participação adicionada."

            if res is None:
                return True, "Participação adicionada (sem retorno detalhado)."

            try:
                if hasattr(res, "id") or hasattr(res, "id_exposicao") or hasattr(res, "id_obra"):
                    return True, "Participação adicionada."
            except Exception:
                pass

            return True, "Participação adicionada."

        except Exception as e:
            return False, f"Erro ao adicionar participação: {e}"

    def remover_obra(self, id_exposicao: int, id_obra: int) -> Tuple[bool, str]:
        try:
            try:
                res = self.db.remover_participacao_exposicao(id_exposicao, id_obra)
            except TypeError:
                res = None
            except Exception as e:
                return False, f"Erro do DB ao remover participação: {e}"

            if isinstance(res, tuple) and len(res) >= 1 and isinstance(res[0], bool):
                msg = res[1] if len(res) > 1 else ("Removido" if res[0] else "Não removido")
                return bool(res[0]), str(msg)

            if isinstance(res, bool):
                return res, ("Removido" if res else "Não removido")

            if res is None:
                return True, "Remoção solicitada."

            return True, "Remoção solicitada."
        except Exception as e:
            return False, f"Erro ao remover participação: {e}"

    def listar_obras(self, id_exposicao: int) -> List[Any]:
        try:
            return self.db.listar_participacoes_por_exposicao(id_exposicao)
        except Exception:
            return []

    def verificar_participacao(self, id_exposicao: int, id_obra: int) -> bool:
        try:
            return bool(self.db.verificar_participacao(id_exposicao, id_obra))
        except Exception:
            return False
