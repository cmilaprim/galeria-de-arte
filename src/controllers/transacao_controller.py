from datetime import datetime
from src.database.manager import DatabaseManager
from src.models.transacao_model import Transacao, TiposTransacao

class TransacaoController:
    def __init__(self):
        self.db_manager = DatabaseManager()

    # ---------------- Cadastro ----------------
    def cadastrar_transacao(self, cliente, valor, tipo, data_transacao, observacoes="", obras=None):
        try:
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

            # Valida se as obras estão disponíveis
            for obra_titulo in obras:
                status_obra = self.db_manager.get_status_obra_por_titulo(obra_titulo)
                if tipo in ["Venda", "Aluguel", "Empréstimo"] and status_obra != "Disponível":
                    return False, f"Obra '{obra_titulo}' não está disponível para {tipo}."
                if tipo == "Devolução" and status_obra not in ["Alugada", "Empréstimo"]:
                    return False, f"Obra '{obra_titulo}' não pode ser devolvida."

            if self.db_manager.verificar_transacao_existe(cliente, data_transacao, tipo):
                return False, "Já existe uma transação com este cliente, tipo e data."

            transacao_id = self.db_manager.get_next_transacao_id()
            transacao = Transacao(
                cliente=cliente.strip(),
                valor=float(valor),
                tipo=tipo.strip(),
                data_transacao=data_transacao.strip(),
                observacoes=observacoes.strip() if observacoes else "",
                obras=obras,
                id=transacao_id,
                data_cadastro=datetime.now().strftime("%d/%m/%Y")
            )

            self.db_manager.inserir_transacao(transacao)

            # Atualiza status das obras
            status_map = {
                "Venda": "Vendida",
                "Aluguel": "Alugada",
                "Empréstimo": "Empréstimo",
                "Devolução": "Disponível"
            }
            for obra_titulo in obras:
                self.db_manager.atualizar_status_obra_por_titulo(obra_titulo, status_map[tipo])

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
    def atualizar_transacao(self, transacao_id, cliente, valor, tipo, data_transacao, observacoes="", obras=None):
        try:
            transacao = self.buscar_transacao_por_id(transacao_id)
            if not transacao:
                return False, "Transação não encontrada."

            if tipo == "Devolução" or transacao.tipo == "Devolução":
                return False, "Transações de Devolução não podem ser editadas."
            if transacao.devolucao:
                return False, "Transações com devolução registrada não podem ser editadas."

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

            # Valida disponibilidade antes de atualizar
            for obra_titulo in obras:
                status_obra = self.db_manager.get_status_obra_por_titulo(obra_titulo)
                if tipo in ["Venda", "Aluguel", "Empréstimo"] and status_obra != "Disponível":
                    return False, f"Obra '{obra_titulo}' não está disponível para {tipo}."

            # Atualiza propriedades
            transacao.cliente = cliente.strip()
            transacao.valor = float(valor)
            transacao.tipo = tipo.strip()
            transacao.data_transacao = data_transacao.strip()
            transacao.observacoes = observacoes.strip() if observacoes else ""
            transacao.obras = obras

            self.db_manager.atualizar_transacao(transacao)

            # Atualiza status das obras
            status_map = {"Venda": "Vendida", "Aluguel": "Alugada", "Empréstimo": "Empréstimo"}
            if tipo in status_map:
                for obra_titulo in obras:
                    self.db_manager.atualizar_status_obra_por_titulo(obra_titulo, status_map[tipo])

            return True, "Transação atualizada com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar transação: {str(e)}"

    # ---------------- Devolução ----------------
    def registrar_devolucao(self, transacao_id, data_devolucao, observacoes="", obras=None):
        """
        Registra uma devolução como nova transação do tipo 'Devolução'.
        Permite devolver obras múltiplas em transações diferentes.
        Bloqueia apenas se a obra já foi devolvida para a mesma transação original.
        """
        try:
            transacao_original = self.buscar_transacao_por_id(transacao_id)
            if not transacao_original:
                return False, "Transação original não encontrada."

            obras_para_devolver = obras or transacao_original.obras

            # Verifica se alguma obra já foi devolvida para esta transação original
            for t in self.listar_transacoes():
                if t.tipo == "Devolução" and f"ID {transacao_id}" in t.observacoes:
                    for obra_titulo in obras_para_devolver:
                        if obra_titulo in t.obras:
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

            # Atualiza status das obras para 'Disponível'
            for obra_titulo in obras_para_devolver:
                self.db_manager.atualizar_status_obra_por_titulo(obra_titulo, "Disponível")

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
            if t.tipo == "Devolução" and f"ID {transacao_id}" in t.observacoes:
                return f"{t.data_transacao} na transação ID: {t.id}"
        return None