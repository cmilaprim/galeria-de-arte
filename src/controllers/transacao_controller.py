from datetime import datetime
from typing import List, Any, Optional
from src.database.manager import DatabaseManager
from src.models.transacao_model import Transacao, TiposTransacao
from src.models.obra_model import ObraDeArte  # usado apenas para typing/clareza


class TransacaoController:
    def __init__(self):
        # segue o padrão do exposicao_controller: cada controller instancia seu DatabaseManager
        self.db_manager = DatabaseManager()

    # ---------------- Helpers ----------------
    def _is_numeric_like(self, v: Any) -> bool:
        try:
            if v is None:
                return False
            s = str(v).strip()
            return s.isdigit()
        except Exception:
            return False

    def _get_obra_status_and_title(self, obra_identifier: Any) -> tuple[Optional[str], Optional[str]]:
        """
        Aceita `obra_identifier` que pode ser:
         - id (numérico ou string numérica) -> busca por id e retorna (status_string, titulo)
         - título (string) -> usa métodos por título (status) e retorna (status_string, titulo)
        Retorna (None, None) se não encontrar.
        """
        try:
            if self._is_numeric_like(obra_identifier):
                oid = int(str(obra_identifier).strip())
                obra = self.db_manager.buscar_obra_por_id(oid)
                if not obra:
                    return None, None
                status = obra.status.value if hasattr(obra.status, "value") else str(obra.status or "")
                return status, obra.titulo
            else:
                # tratamento por título (fallback compatível)
                titulo = str(obra_identifier)
                status = self.db_manager.get_status_obra_por_titulo(titulo)
                return status, titulo
        except Exception:
            return None, None

    # ---------------- Cadastro ----------------
    def cadastrar_transacao(self, cliente: str, valor: Any, tipo: str, data_transacao: str, observacoes: str = "", obras: List[Any] = None):
        try:
            # validações básicas
            if not cliente or not cliente.strip():
                return False, "Cliente é obrigatório."
            if valor is None or valor == "":
                return False, "Valor é obrigatório."
            if not tipo or not tipo.strip():
                return False, "Tipo é obrigatório."
            if not data_transacao or not data_transacao.strip():
                return False, "Data da transação é obrigatória."
            try:
                datetime.strptime(data_transacao.strip(), "%d/%m/%Y")
            except ValueError:
                return False, "Data da transação deve estar no formato DD/MM/YYYY."
            if not obras or len(obras) == 0:
                return False, "É necessário informar ao menos uma obra."

            # converte valor para float (ou falha)
            try:
                valor_float = float(valor)
            except Exception:
                return False, "Valor inválido."

            # Valida se as obras estão disponíveis (aceita ids ou títulos)
            for obra_id_or_title in obras:
                status_obra, titulo = self._get_obra_status_and_title(obra_id_or_title)
                if status_obra is None:
                    return False, f"Obra '{obra_id_or_title}' não encontrada."
                # regras de negócio: para Venda/Aluguel/Empréstimo, obra deve estar "Disponível"
                if tipo in ["Venda", "Aluguel", "Empréstimo"] and status_obra != "Disponível":
                    return False, f"Obra '{titulo or obra_id_or_title}' não está disponível para {tipo}."
                if tipo == "Devolução" and status_obra not in ["Alugada", "Empréstimo"]:
                    return False, f"Obra '{titulo or obra_id_or_title}' não pode ser devolvida."

            # verifica existência de transação similar (cliente, data, valor)
            if self.db_manager.verificar_transacao_existe(cliente, data_transacao, valor_float):
                return False, "Já existe uma transação com este cliente, data e valor."

            # monta objeto Transacao
            transacao_id = self.db_manager.get_next_transacao_id()
            transacao = Transacao(
                cliente=cliente.strip(),
                valor=valor_float,
                tipo=tipo.strip(),
                data_transacao=data_transacao.strip(),
                observacoes=observacoes.strip() if observacoes else "",
                obras=obras,
                id=transacao_id,
                data_cadastro=datetime.now().strftime("%d/%m/%Y")
            )

            # insere no DB
            self.db_manager.inserir_transacao(transacao)

            # Atualiza status das obras (usa título quando possível para manter método existente no manager)
            status_map = {
                "Venda": "Vendida",
                "Aluguel": "Alugada",
                "Empréstimo": "Empréstimo",
                "Devolução": "Disponível"
            }
            novo_status = status_map.get(tipo)
            if novo_status:
                for obra_id_or_title in obras:
                    # obtém título para usar atualizar_status_obra_por_titulo
                    _, titulo = self._get_obra_status_and_title(obra_id_or_title)
                    if titulo:
                        try:
                            self.db_manager.atualizar_status_obra_por_titulo(titulo, novo_status)
                        except Exception:
                            # tentativa alternativa: se tivermos id, buscar obra e atualizar via atualizar_obra
                            if self._is_numeric_like(obra_id_or_title):
                                try:
                                    oid = int(str(obra_id_or_title).strip())
                                    obra_obj = self.db_manager.buscar_obra_por_id(oid)
                                    if obra_obj:
                                        obra_obj.status = type(obra_obj.status)(novo_status) if hasattr(obra_obj.status, "__class__") else novo_status
                                        # chamar atualizar_obra usando o objeto modificado (tentativa conservadora)
                                        try:
                                            self.db_manager.atualizar_obra(obra_obj)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                    else:
                        # se título não obtido, ignorar para evitar erro
                        continue

            return True, "Transação cadastrada com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar transação: {str(e)}"

    # ---------------- Listagem ----------------
    def listar_transacoes(self):
        return self.db_manager.listar_transacoes()

    # ---------------- Busca ----------------
    def buscar_transacao_por_id(self, transacao_id):
        return self.db_manager.buscar_transacao_por_id(transacao_id)

    # ---------------- Atualização ----------------
    def atualizar_transacao(self, transacao_id, cliente, valor, tipo, data_transacao, observacoes: str = "", obras: List[Any] = None):
        try:
            transacao = self.buscar_transacao_por_id(transacao_id)
            if not transacao:
                return False, "Transação não encontrada."

            if tipo == "Devolução" or transacao.tipo == "Devolução":
                return False, "Transações de Devolução não podem ser editadas."
            if hasattr(transacao, "devolucao") and getattr(transacao, "devolucao"):
                return False, "Transações com devolução registrada não podem ser editadas."

            # validações básicas
            if not cliente or not cliente.strip():
                return False, "Cliente é obrigatório."
            if valor is None or valor == "":
                return False, "Valor é obrigatório."
            if not tipo or not tipo.strip():
                return False, "Tipo é obrigatório."
            if not data_transacao or not data_transacao.strip():
                return False, "Data da transação é obrigatória."
            try:
                datetime.strptime(data_transacao.strip(), "%d/%m/%Y")
            except ValueError:
                return False, "Data da transação deve estar no formato DD/MM/YYYY."
            if not obras or len(obras) == 0:
                return False, "É necessário informar ao menos uma obra."

            # converte valor
            try:
                valor_float = float(valor)
            except Exception:
                return False, "Valor inválido."

            # prepara conjunto das obras que já pertenciam à transação original
            try:
                existing_obras_raw = getattr(transacao, "obras", None) or []
                existing_obras_set = {str(x).strip() for x in existing_obras_raw}
            except Exception:
                existing_obras_set = set()

            # Valida disponibilidade antes de atualizar (aceita ids ou títulos).
            # Importante: obras que já faziam parte da transação original são permitidas mesmo que não estejam "Disponível".
            for obra_id_or_title in obras:
                s_key = str(obra_id_or_title).strip()
                # se já fazia parte da transação original, pular validação de disponibilidade
                if s_key in existing_obras_set:
                    continue

                status_obra, titulo = self._get_obra_status_and_title(obra_id_or_title)
                if status_obra is None:
                    return False, f"Obra '{obra_id_or_title}' não encontrada."

                # normaliza status para comparação (lida com enum/string)
                try:
                    st = status_obra.value if hasattr(status_obra, "value") else str(status_obra)
                except Exception:
                    st = str(status_obra or "")

                st_norm = st.strip().lower()
                if tipo in ["Venda", "Aluguel", "Empréstimo"] and "dispon" not in st_norm:
                    return False, f"Obra '{titulo or obra_id_or_title}' não está disponível para {tipo}."

            # Atualiza propriedades no objeto transacao e persiste
            transacao.cliente = cliente.strip()
            transacao.valor = float(valor_float)
            transacao.tipo = tipo.strip()
            transacao.data_transacao = data_transacao.strip()
            transacao.observacoes = observacoes.strip() if observacoes else ""
            transacao.obras = obras

            self.db_manager.atualizar_transacao(transacao)

            # Atualiza status das obras se aplicável (venda/aluguel/empréstimo)
            status_map = {"Venda": "Vendida", "Aluguel": "Alugada", "Empréstimo": "Empréstimo"}
            novo_status = status_map.get(tipo)
            if novo_status:
                for obra_id_or_title in obras:
                    try:
                        _, titulo = self._get_obra_status_and_title(obra_id_or_title)
                        if titulo:
                            try:
                                # tenta atualizar pelo título (método existente)
                                self.db_manager.atualizar_status_obra_por_titulo(titulo, novo_status)
                            except Exception:
                                # fallback silencioso
                                pass
                    except Exception:
                        # não interrompe o processo se uma obra falhar na atualização de status
                        continue

            return True, "Transação atualizada com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar transação: {str(e)}"

    # ---------------- Devolução ----------------
    def registrar_devolucao(self, transacao_id, data_devolucao, observacoes: str = "", obras: List[Any] = None):
        """
        Registra uma devolução como nova transação do tipo 'Devolução'.
        Aceita obras identificadas por id ou título.
        """
        try:
            transacao_original = self.buscar_transacao_por_id(transacao_id)
            if not transacao_original:
                return False, "Transação original não encontrada."

            obras_para_devolver = obras or transacao_original.obras

            # Verifica se alguma obra já foi devolvida para esta transação original
            for t in self.listar_transacoes():
                if t.tipo == "Devolução" and f"ID {transacao_id}" in (t.observacoes or ""):
                    for obra_id_or_title in obras_para_devolver:
                        # compara com conteúdo armazenado (pode ser id ou título)
                        if obra_id_or_title in (t.obras or []):
                            return False, f"Obra devolvida em {t.data_transacao} na transação ID: {t.id}"

            # Cria nova transação de devolução
            devolucao = Transacao(
                cliente=transacao_original.cliente,
                valor=0.0,
                tipo="Devolução",
                data_transacao=data_devolucao,
                observacoes=observacoes or f"Devolução da transação ID {transacao_id}",
                obras=obras_para_devolver
            )

            # Insere devolução diretamente no banco
            devolucao_id = self.db_manager.inserir_transacao(devolucao)

            # Atualiza status das obras para 'Disponível' (por título quando possível)
            for obra_id_or_title in obras_para_devolver:
                _, titulo = self._get_obra_status_and_title(obra_id_or_title)
                if titulo:
                    try:
                        self.db_manager.atualizar_status_obra_por_titulo(titulo, "Disponível")
                    except Exception:
                        # se falhar e tivermos um id numérico, tentar via atualizar_obra
                        if self._is_numeric_like(obra_id_or_title):
                            try:
                                oid = int(str(obra_id_or_title).strip())
                                obra_obj = self.db_manager.buscar_obra_por_id(oid)
                                if obra_obj:
                                    obra_obj.status = type(obra_obj.status)( "Disponível") if hasattr(obra_obj.status, "__class__") else "Disponível"
                                    try:
                                        self.db_manager.atualizar_obra(obra_obj)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                else:
                    # sem título, ignorar
                    continue

            return True, f"Devolução registrada com sucesso! ID: {devolucao_id}"

        except Exception as e:
            return False, f"Erro ao registrar devolução: {str(e)}"

    # ---------------- Verificar Devolução ----------------
    def verificar_devolucao(self, transacao_id):
        """
        Retorna mensagem caso já exista devolução para a transação original.
        """
        transacao_original = self.buscar_transacao_por_id(transacao_id)
        if not transacao_original:
            return None

        for t in self.listar_transacoes():
            if t.tipo == "Devolução" and f"ID {transacao_id}" in (t.observacoes or ""):
                return f"{t.data_transacao} na transação ID: {t.id}"
        return None