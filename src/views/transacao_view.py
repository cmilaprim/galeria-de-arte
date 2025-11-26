import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import locale

# ------------------ INSTALAÇÃO AUTOMÁTICA DO TKCALENDAR ------------------
try:
    from tkcalendar import DateEntry
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tkcalendar"])
    from tkcalendar import DateEntry

from src.controllers.transacao_controller import TransacaoController


class TransacaoView:
    def __init__(self, root, controller=None, manager=None):
        self.root = root

        # limpa a janela
        for w in self.root.winfo_children():
            w.destroy()

        # controller segue padrão (controller instancia seu DatabaseManager)
        self.controller = controller or TransacaoController()
        self.manager = manager  # mantido para compatibilidade, mas não usado diretamente

        self.root.title("Sistema de Gestão de Galeria de Arte")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.root.configure(bg="#eeeeee")

        # estado da view
        self.transacao_selecionada = None
        # armazenamos sempre ids (strings) das obras selecionadas
        self.obras_selecionadas = []

        # mapeamento id->titulo para exibição (reconstruído quando necessário)
        self._id_to_titulo = {}
        # mapeia item_id (tree) -> lista bruta de obras (ids ou títulos) para edição / devolução
        self._item_to_obras = {}

        # tenta pt_BR
        try:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
        except Exception:
            pass

        self.criar_interface()
        self.carregar_transacoes()

    # ------------------- Criação de widgets -------------------
    def criar_interface(self):
        bg = "#F3F4F6"
        self.root.configure(bg=bg)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg)
        style.configure("TLabel", background=bg)

        # --- FRAME DE CADASTRO --- #
        frm_cadastro = ttk.LabelFrame(self.root, text="Cadastro de Transação", padding=10)
        frm_cadastro.pack(fill="x", padx=10, pady=8)

        # colunas proporcionais
        for i in range(6):
            frm_cadastro.columnconfigure(i, weight=1, uniform="col")

        # linha 0: Cliente, Valor, Tipo
        ttk.Label(frm_cadastro, text="Cliente:").grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)
        self.entry_cliente = ttk.Entry(frm_cadastro)
        self.entry_cliente.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=5)

        ttk.Label(frm_cadastro, text="Valor:").grid(row=0, column=2, sticky="w", padx=(10, 5), pady=5)
        self.entry_valor = ttk.Entry(frm_cadastro)
        self.entry_valor.grid(row=0, column=3, sticky="ew", padx=(5, 10), pady=5)
        self.entry_valor.bind("<KeyRelease>", self.formatar_valor)

        ttk.Label(frm_cadastro, text="Tipo:").grid(row=0, column=4, sticky="w", padx=(10, 5), pady=5)
        self.combo_tipo = ttk.Combobox(frm_cadastro, values=["Venda", "Aluguel", "Empréstimo", "Aquisição"], state="readonly")
        self.combo_tipo.grid(row=0, column=5, sticky="ew", padx=(5, 10), pady=5)

        # linha 1: datas + obras
        ttk.Label(frm_cadastro, text="Data Transação:").grid(row=1, column=0, sticky="w", padx=(10, 5), pady=5)
        self.entry_data_transacao = DateEntry(frm_cadastro, date_pattern="dd/MM/yyyy", background="lightblue")
        self.entry_data_transacao.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=5)

        ttk.Label(frm_cadastro, text="Data Cadastro:").grid(row=1, column=2, sticky="w", padx=(10, 5), pady=5)
        self.entry_data_cadastro = ttk.Entry(frm_cadastro, state="readonly")
        self.entry_data_cadastro.grid(row=1, column=3, sticky="ew", padx=(5, 10), pady=5)
        self.entry_data_cadastro.config(state="normal")
        self.entry_data_cadastro.delete(0, tk.END)
        self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_data_cadastro.config(state="readonly")

        ttk.Label(frm_cadastro, text="Obra(s):").grid(row=1, column=4, sticky="w", padx=(10, 5), pady=5)
        self.botao_obras = ttk.Button(frm_cadastro, text="Selecionar Obras", command=self.abrir_selecionar_obras)
        self.botao_obras.grid(row=1, column=5, sticky="ew", padx=(5, 10), pady=5)

        # linha 2: label de obras selecionadas
        self.label_obras_selecionadas = ttk.Label(
            frm_cadastro,
            text="Nenhuma obra selecionada",
            wraplength=600,
            justify="left",
            foreground="gray"
        )
        self.label_obras_selecionadas.grid(row=2, column=0, columnspan=6, sticky="ew", padx=10, pady=(0, 5))

        # linha 3: observações
        ttk.Label(frm_cadastro, text="Observações:").grid(row=3, column=0, sticky="nw", padx=(10, 5), pady=5)
        self.text_obs = tk.Text(frm_cadastro, height=5, relief="solid", borderwidth=1, bg="white")
        self.text_obs.grid(row=3, column=1, columnspan=5, sticky="nsew", padx=5, pady=5)

        # botão home (voltar) — preservado e visível
        frame_home = tk.Frame(frm_cadastro, bg="#f0f0f0")
        frame_home.place(relx=1, rely=0, x=15, y=-35, anchor="ne")
        self.btn_home = tk.Button(
            frame_home,
            text="❌",
            font=("Segoe UI Emoji", 10),
            bd=0,
            highlightthickness=0,
            padx=0,
            pady=0,
            bg="#f0f0f0",
            activebackground="#dddddd",
            cursor="hand2",
            command=self.voltar_inicio
        )
        self.btn_home.pack(expand=True, fill="both")

        # botões salvar / cancelar
        btns_frame = ttk.Frame(frm_cadastro)
        btns_frame.grid(row=0, column=8, rowspan=4, sticky="n", padx=10, pady=5)
        ttk.Button(btns_frame, text="Salvar", command=self.salvar_transacao, width=16).pack(pady=4)
        ttk.Button(btns_frame, text="Cancelar", command=self.limpar_campos, width=16).pack(pady=4)

        # --- FRAME DE LISTAGEM --- #
        listagem_frame = ttk.LabelFrame(self.root, text="Listagem de Transações", padding=10)
        listagem_frame.pack(fill="both", expand=True, padx=10, pady=5)
        listagem_frame.columnconfigure(0, weight=1)
        listagem_frame.rowconfigure(0, weight=1)

        # botão registrar devolução
        btn_devolucao = ttk.Button(listagem_frame, text="Registrar Devolução", command=self.abrir_devolucao, width=18)
        btn_devolucao.place(relx=1.0, x=-20, y=-6, anchor="ne")

        # treeview de transações
        colunas = ("ID", "Cliente", "Valor", "Tipo", "Data Transação", "Data Cadastro", "Observações", "Obra(s)")
        self.tree = ttk.Treeview(listagem_frame, columns=colunas, show="headings")
        for c, w in zip(colunas, (60, 200, 100, 100, 90, 90, 150, 150)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=0, pady=(30, 0))

        # scrollbars
        yscroll = ttk.Scrollbar(listagem_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(listagem_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        listagem_frame.grid_rowconfigure(0, weight=1)
        listagem_frame.grid_columnconfigure(0, weight=1)

        # bind duplo clique
        self.tree.bind("<Double-1>", self.carregar_transacao_selecionada)

    # ---------------- MÉTODOS ----------------
    def formatar_valor(self, event=None):
        texto = self.entry_valor.get()
        numeros = "".join(filter(str.isdigit, texto))
        if numeros == "":
            self.entry_valor.delete(0, tk.END)
            return
        valor = int(numeros) / 100
        try:
            texto_formatado = locale.currency(valor, grouping=True)
        except Exception:
            texto_formatado = f"{valor:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, texto_formatado)

    def centralizar_janela(self, janela, largura, altura):
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

    # ---------- Salvar / Limpar ----------
    def salvar_transacao(self):
        cliente = self.entry_cliente.get().strip()
        valor_texto = self.entry_valor.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
        tipo = self.combo_tipo.get().strip()
        data_transacao = self.entry_data_transacao.get_date().strftime("%d/%m/%Y")
        observacoes = self.text_obs.get("1.0", tk.END).strip()

        if not cliente:
            messagebox.showerror("Erro", "O campo Cliente é obrigatório.")
            return

        if not valor_texto:
            messagebox.showerror("Erro", "O campo Valor é obrigatório.")
            return

        if not tipo:
            messagebox.showerror("Erro", "O campo Tipo é obrigatório.")
            return

        if not data_transacao:
            messagebox.showerror("Erro", "O campo Data da Transação é obrigatório.")
            return

        if not self.obras_selecionadas:
            messagebox.showerror("Erro", "Você deve selecionar pelo menos uma obra.")
            return

        # Validação de valor numérico
        try:
            valor = float(valor_texto)
        except ValueError:
            messagebox.showerror("Erro", "O campo Valor deve ser numérico.")
            return

        # enviamos lista de ids (strings)
        obras_para_salvar = [str(x).strip() for x in self.obras_selecionadas]

        # Atualiza ou cadastra
        if self.transacao_selecionada:
            success, msg = self.controller.atualizar_transacao(
                transacao_id=self.transacao_selecionada,
                cliente=cliente,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                observacoes=observacoes,
                obras=obras_para_salvar
            )
        else:
            success, msg = self.controller.cadastrar_transacao(
                cliente=cliente,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                observacoes=observacoes,
                obras=obras_para_salvar
            )

        if success:
            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos()
            self.carregar_transacoes()
        else:
            messagebox.showerror("Erro", msg)

    def limpar_campos(self):
        try:
            self.entry_cliente.delete(0, tk.END)
            self.entry_valor.delete(0, tk.END)
            self.combo_tipo.set("")
            self.text_obs.delete("1.0", tk.END)
            self.entry_data_transacao.set_date(date.today())
            self.entry_data_cadastro.config(state="normal")
            self.entry_data_cadastro.delete(0, tk.END)
            self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
            self.entry_data_cadastro.config(state="readonly")
        except Exception:
            pass
        self.transacao_selecionada = None
        self.obras_selecionadas = []
        self.label_obras_selecionadas.config(text="Nenhuma obra selecionada")
        self._item_to_obras.clear()

    # ---------- Carregar ----------
    def carregar_transacoes(self):
        # limpa árvore
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._item_to_obras.clear()

        # reconstrói map id->titulo para exibição
        self._rebuild_obra_cache()

        # preenche tree de transações
        for transacao in self.controller.listar_transacoes():
            obras_raw = transacao.obras or []
            display_titles = []
            parsed = []
            for o in obras_raw:
                s = str(o).strip()
                # se for id numérico, mapeia para título; caso contrário, assume título
                if s.isdigit():
                    parsed.append(s)
                    display_titles.append(self._id_to_titulo.get(s, s))
                else:
                    # se for título, tenta encontrar id correspondente; senão usa o texto
                    found = next((k for k, v in self._id_to_titulo.items() if v == s), None)
                    parsed.append(found or s)
                    display_titles.append(self._id_to_titulo.get(found, s) if found else s)
            obras_txt = ", ".join(display_titles)
            try:
                valor_fmt = locale.currency(float(transacao.valor), grouping=True)
            except Exception:
                valor_fmt = f"{float(transacao.valor):,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
            iid = self.tree.insert("", tk.END, values=(
                transacao.id,
                transacao.cliente,
                valor_fmt,
                transacao.tipo,
                transacao.data_transacao,
                transacao.data_cadastro,
                transacao.observacoes,
                obras_txt
            ))
            # armazena parsed list (ids ou titles) para uso posterior (edição/devolução)
            self._item_to_obras[iid] = parsed

    def carregar_transacao_selecionada(self, event):
        itens = self.tree.selection()
        if not itens:
            return
        iid = itens[0]
        valores = self.tree.item(iid, "values")
        self.transacao_selecionada = valores[0]

        self.entry_cliente.delete(0, tk.END)
        self.entry_cliente.insert(0, valores[1])
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, valores[2].replace("R$", "").strip())
        self.combo_tipo.set(valores[3])
        try:
            self.entry_data_transacao.set_date(datetime.strptime(valores[4], "%d/%m/%Y"))
        except Exception:
            pass
        self.text_obs.delete("1.0", tk.END)
        self.text_obs.insert("1.0", valores[6] or "")
        self.entry_data_cadastro.config(state="normal")
        self.entry_data_cadastro.delete(0, tk.END)
        self.entry_data_cadastro.insert(0, valores[5] or "")
        self.entry_data_cadastro.config(state="readonly")

        raw = self._item_to_obras.get(iid, [])
        # armazena ids (strings) quando possível; títulos ficam como fallback
        self.obras_selecionadas = [str(x) for x in raw]
        titles = [self._id_to_titulo.get(str(x), str(x)) for x in self.obras_selecionadas]
        self.label_obras_selecionadas.config(
            text="Obras Selecionadas: " + ", ".join(titles) if titles else "Nenhuma obra selecionada"
        )

    # ---------- Selecionar obras (modal maior, sem símbolos, só cores) ----------
    def abrir_selecionar_obras(self):
        win = tk.Toplevel(self.root)
        win.title("Seleção de Obras")
        win.transient(self.root)
        win.grab_set()
        # aumentado para não cortar informações (conforme exposicao_view)
        self.centralizar_janela(win, 900, 520)

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        cols = ("ID", "Título", "Artista", "Status")
        tree_obras = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
        for c, w in [("ID", 60), ("Título", 460), ("Artista", 220), ("Status", 140)]:
            tree_obras.heading(c, text=c)
            tree_obras.column(c, width=w, anchor="w")
        tree_obras.pack(fill="both", expand=True, padx=6, pady=(6, 4))

        # tags visuais — cores alinhadas ao exposicao_view
        # NOTE: mapeamento ajustado para que obras ocupadas *não* fiquem verdes.
        tree_obras.tag_configure("available", background="#D6F5D6")     # verde claro = disponível
        tree_obras.tag_configure("in_exposicao", background="#F8E8E8")  # cinza claro = em exposição (ocupada)
        tree_obras.tag_configure("busy", background="#F5D6D6")          # rosado claro = indisponível/outros
        tree_obras.tag_configure("to_add", background="#D6F5D6")
        tree_obras.tag_configure("to_remove", background="#F5D6D6")

        # busca obras via controller.db_manager (uso direto do manager do controller, como exposicao_view)
        try:
            obras = self.controller.db_manager.listar_todas_obras() or []
        except Exception:
            obras = []

        # reconstrói map id->titulo (para a label de seleção)
        self._rebuild_obra_cache()

        for o in obras:
            try:
                oid = getattr(o, "id_obra", getattr(o, "id", ""))
                titulo = getattr(o, "titulo", "") or ""
                artista_raw = getattr(o, "artista", "")
                artista = ", ".join(artista_raw) if isinstance(artista_raw, (list, tuple)) else str(artista_raw)
                status_raw = getattr(o, "status", None)
                status = status_raw.value if hasattr(status_raw, "value") else str(status_raw or "")
            except Exception:
                oid = ""
                titulo = str(o)
                artista = ""
                status = ""

            s_norm = (status or "").strip().lower()
            # ajuste: disponível => green; em exposição (ocupada) => in_exposicao (gray); outros (vendida, alugada, etc) => busy (rose)
            if "dispon" in s_norm:
                tag = "available"
            elif "em" in s_norm and ("expos" in s_norm or "exposição" in s_norm or "em_expos" in s_norm):
                tag = "in_exposicao"
            else:
                tag = "busy"

            # inserir SÓ o título (sem símbolos), tags controlam cor
            iid = tree_obras.insert("", tk.END, values=(str(oid), titulo, artista, status), tags=(tag,))

            # pre-seleciona se já estiver nas obras_selecionadas (ids)
            if any(str(oid) == str(x) for x in self.obras_selecionadas):
                tree_obras.selection_add(iid)

        # botões confirmar / cancelar
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(pady=10)

        def confirmar_selecao():
            itens = tree_obras.selection()
            selecionadas_ids = []
            titulos_para_label = []
            ignoradas = []
            for it in itens:
                vals = tree_obras.item(it, "values")
                id_obra = str(vals[0])
                titulo = str(vals[1])  # já sem símbolos
                tag = tree_obras.item(it, "tags")[0] if tree_obras.item(it, "tags") else ""
                # valida disponibilidade no momento da seleção: só aceitar tag "available"
                if tag == "available":
                    selecionadas_ids.append(id_obra)
                    titulos_para_label.append(titulo)
                else:
                    # marca como ignorada
                    ignoradas.append(titulo)
            # armazenar ids (strings)
            self.obras_selecionadas = selecionadas_ids
            texto = "Obras Selecionadas: " + ", ".join(titulos_para_label) if titulos_para_label else "Nenhuma obra selecionada"
            self.label_obras_selecionadas.config(text=texto)
            if ignoradas:
                messagebox.showwarning("Atenção", f"As seguintes obras não foram adicionadas pois não estão disponíveis: {', '.join(ignoradas)}")
            win.destroy()

        ttk.Button(frame_botoes, text="Confirmar Seleção", command=confirmar_selecao).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=win.destroy).pack(side="left", padx=10)

    def voltar_inicio(self):
        try:
            from src.views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import).")
            return
        for w in self.root.winfo_children():
            w.destroy()
        TelaInicial(self.root, self.manager)

    # ---------- Registrar devolução ----------
    def abrir_devolucao(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma transação para registrar devolução.")
            return
        iid = sel[0]
        vals = self.tree.item(iid, "values")
        id_transacao, cliente, valor, tipo, data_transacao, _, observacoes_orig, obras_display = vals

        if tipo not in ("Aluguel", "Empréstimo"):
            messagebox.showerror("Erro", "Só é possível registrar devolução de transações de Aluguel ou Empréstimo.")
            return

        devolucao = self.controller.verificar_devolucao(id_transacao)
        if devolucao:
            messagebox.showinfo("Informação", f"Esta transação já foi devolvida em {devolucao}")
            return

        win_dev = tk.Toplevel(self.root)
        win_dev.title("Registrar devolução")
        win_dev.transient(self.root)
        win_dev.grab_set()
        self.centralizar_janela(win_dev, 300, 180)

        ttk.Label(win_dev, text="Selecione a data da devolução:").pack(pady=10)
        date_dev_entry = DateEntry(win_dev, date_pattern="dd/MM/yyyy", background="lightblue", state="readonly")
        date_dev_entry.pack(pady=5)

        frame_btn = ttk.Frame(win_dev)
        frame_btn.pack(pady=20, fill="x", expand=True)

        def confirmar():
            data_dev = date_dev_entry.get_date()
            try:
                data_trans = datetime.strptime(data_transacao, "%d/%m/%Y").date()
            except Exception:
                messagebox.showerror("Erro", "Data da transação inválida.")
                return
            if data_dev <= data_trans:
                messagebox.showerror("Erro", "A data de devolução deve ser posterior à data da transação original.")
                return

            data_dev_str = data_dev.strftime("%d/%m/%Y")
            # obtém lista bruta de obras do item (ids ou titles)
            raw_obras = self._item_to_obras.get(iid, [])
            # converte ids -> títulos quando possível (controller aceita ambos)
            titulos_para_devolucao = []
            for o in raw_obras:
                s = str(o).strip()
                if s.isdigit():
                    titulos_para_devolucao.append(self._id_to_titulo.get(s, s))
                else:
                    titulos_para_devolucao.append(s)

            # registra devolução via controller (controller atualiza status das obras)
            success, msg = self.controller.registrar_devolucao(
                transacao_id=id_transacao,
                data_devolucao=data_dev_str,
                observacoes=f"Devolução de {tipo}: ID {id_transacao}.",
                obras=titulos_para_devolucao
            )

            if success:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)

            win_dev.destroy()
            self.carregar_transacoes()

        ttk.Button(frame_btn, text="Cancelar", command=win_dev.destroy).pack(side="left", padx=10, expand=True, fill="x")
        ttk.Button(frame_btn, text="Confirmar", command=confirmar).pack(side="left", padx=10, expand=True, fill="x")

    # ---------------- helpers ----------------
    def _rebuild_obra_cache(self):
        """Reconstrói cache id -> título usando controller.db_manager"""
        self._id_to_titulo.clear()
        try:
            for o in self.controller.db_manager.listar_todas_obras() or []:
                oid = getattr(o, "id_obra", getattr(o, "id", None))
                titulo = getattr(o, "titulo", "") or ""
                if oid is not None:
                    self._id_to_titulo[str(oid)] = titulo
        except Exception:
            pass
