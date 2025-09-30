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

from ..controllers.transacao_controller import TransacaoController

class TransacaoView:
    def __init__(self, root, controller=None, manager=None):
        self.root = root

        for w in self.root.winfo_children():
            w.destroy()

        self.controller = controller or TransacaoController()
        self.manager = manager

        self.root.title("Sistema de Gestão de Galeria de Arte")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.root.configure(bg="#eeeeee")

        self.transacao_selecionada = None
        self.obras_selecionadas = []

        # tentativa de setar locale pt_BR (se disponível)
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except Exception:
            # não fatal — usar fallback de formatação quando necessário
            pass

        self.criar_interface()
        self.carregar_transacoes()

    # ------------------- Interface -------------------
    def criar_interface(self):
        bg = "#F3F4F6"
        self.root.configure(bg=bg)
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg)
        style.configure("TLabel", background=bg)

        # --- FRAME DE CADASTRO --- #
        frm_cadastro = ttk.LabelFrame(self.root, text="Cadastro de Transação", padding=10)
        frm_cadastro.pack(fill="x", padx=10, pady=8)

        # Configuração das colunas para redimensionamento proporcional
        for i in range(6):
            frm_cadastro.columnconfigure(i, weight=1, uniform="col")

        # --- Linha 1: Cliente, Valor, Tipo ---
        campos_linha1 = [
            ("Cliente:", "entry_cliente", "entry"),
            ("Valor:", "entry_valor", "entry"),
            ("Tipo:", "combo_tipo", "combo")
        ]

        for idx, (label_text, attr_name, tipo) in enumerate(campos_linha1):
            col_label = idx * 2
            col_entry = idx * 2 + 1

            ttk.Label(frm_cadastro, text=label_text).grid(
                row=0, column=col_label, sticky="w", padx=(10,5), pady=5
            )

            if tipo == "combo":
                combo = ttk.Combobox(frm_cadastro, values=["Venda","Aluguel","Empréstimo","Aquisição"], state="readonly")
                combo.grid(row=0, column=col_entry, sticky="ew", padx=(5,10), pady=5)
                setattr(self, attr_name, combo)
            else:
                entry = ttk.Entry(frm_cadastro)
                entry.grid(row=0, column=col_entry, sticky="ew", padx=(5,10), pady=5)
                setattr(self, attr_name, entry)
                if attr_name == "entry_valor":
                    entry.bind("<KeyRelease>", self.formatar_valor)


        # --- Linha 2: Datas + Obras ---
        campos_linha2 = [
            ("Data Transação:", "entry_data_transacao", "date"),
            ("Data Cadastro:", "entry_data_cadastro", "readonly"),
            ("Obra(s):", "botao_obras", "button")
        ]

        for idx, (label_text, attr_name, tipo) in enumerate(campos_linha2):
            col_label = idx * 2
            col_entry = idx * 2 + 1

            ttk.Label(frm_cadastro, text=label_text).grid(
                row=1, column=col_label, sticky="w", padx=(10,5), pady=5
            )

            if tipo == "date":
                entry = DateEntry(frm_cadastro, date_pattern="dd/MM/yyyy", background="lightblue")
                entry.grid(row=1, column=col_entry, sticky="ew", padx=(5,10), pady=5)
                setattr(self, attr_name, entry)

            elif tipo == "readonly":
                entry = ttk.Entry(frm_cadastro, state="readonly")
                entry.grid(row=1, column=col_entry, sticky="ew", padx=(5,10), pady=5)
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
                entry.config(state="readonly")
                setattr(self, attr_name, entry)

            else:  # botão Obras
                btn = ttk.Button(frm_cadastro, text="Selecionar Obras", command=self.abrir_selecionar_obras)
                btn.grid(row=1, column=col_entry, sticky="ew", padx=(5,10), pady=5)
                setattr(self, attr_name, btn)


        # --- Linha 3: Label de Obras Selecionadas ---
        self.label_obras_selecionadas = ttk.Label(
            frm_cadastro,
            text="Nenhuma obra selecionada",
            wraplength=400,
            justify="left",
            foreground="gray"
        )
        self.label_obras_selecionadas.grid(
            row=2, column=0, columnspan=6, sticky="ew", padx=10, pady=(0,5)
        )

        # --- Linha 4: Observações ---
        ttk.Label(frm_cadastro, text="Observações:").grid(
            row=3, column=0, sticky="nw", padx=(10,5), pady=5
        )

        self.text_obs = tk.Text(frm_cadastro, height=5, relief="solid", borderwidth=1, bg="white")
        self.text_obs.grid(
            row=3, column=1, columnspan=5, sticky="nsew", padx=5, pady=5
        )

        # --- Botão Home (Voltar) --- #
        frame_home = tk.Frame(frm_cadastro, bg="#f0f0f0", width=0, height=0)
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

        # --- Botões Salvar / Cancelar / Buscar --- #
        btns_frame = ttk.Frame(frm_cadastro)
        btns_frame.grid(row=0, column=8, rowspan=4, sticky="n", padx=10, pady=5)
        ttk.Button(btns_frame, text="Salvar", command=self.salvar_transacao, width=16).pack(pady=4)
        ttk.Button(btns_frame, text="Cancelar", command=self.limpar_campos, width=16).pack(pady=4)
        ttk.Button(btns_frame, text="Buscar", command=self.carregar_transacoes, width=16).pack(pady=4)

        # --- FRAME DE LISTAGEM --- #
        listagem_frame = ttk.LabelFrame(self.root, text="Listagem de Transações", padding=10)
        listagem_frame.pack(fill="both", expand=True, padx=10, pady=5)
        listagem_frame.columnconfigure(0, weight=1)
        listagem_frame.rowconfigure(0, weight=1)

        colunas = ("ID","Cliente","Valor","Tipo","Data Transação","Data Cadastro","Observações","Obra(s)")
        self.tree = ttk.Treeview(listagem_frame, columns=colunas, show="headings")
        for c, w in zip(colunas, (60,200,100,100,90,90,150,150)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        yscroll = ttk.Scrollbar(listagem_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(listagem_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        listagem_frame.grid_rowconfigure(0, weight=1)
        listagem_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.carregar_transacao_selecionada)

    # ---------------- MÉTODOS ----------------
    def formatar_valor(self, event=None):
        texto = self.entry_valor.get()
        numeros = ''.join(filter(str.isdigit, texto))
        if numeros == "":
            self.entry_valor.delete(0, tk.END)
            return
        valor = int(numeros) / 100
        try:
            texto_formatado = locale.currency(valor, grouping=True)
        except Exception:
            # fallback para formatação manual (pt_BR style)
            texto_formatado = f"{valor:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
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
        cliente = self.entry_cliente.get()
        valor_texto = self.entry_valor.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
        tipo = self.combo_tipo.get()
        data_transacao = self.entry_data_transacao.get_date().strftime("%d/%m/%Y")
        observacoes = self.text_obs.get("1.0", tk.END).strip()

        if not cliente or not valor_texto or not tipo or not data_transacao or not self.obras_selecionadas:
            messagebox.showerror("Erro", "Todos os campos obrigatórios devem ser preenchidos, incluindo a seleção das obras.")
            return
        try:
            valor = float(valor_texto)
        except ValueError:
            messagebox.showerror("Erro", "O campo Valor deve ser numérico.")
            return

        if self.transacao_selecionada:
            # Atualização
            success, msg = self.controller.atualizar_transacao(
                transacao_id=self.transacao_selecionada,
                cliente=cliente,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                observacoes=observacoes,
                obras=self.obras_selecionadas
            )
        else:
            # Cadastro novo
            success, msg = self.controller.cadastrar_transacao(
                cliente=cliente,
                valor=valor,
                tipo=tipo,
                data_transacao=data_transacao,
                observacoes=observacoes,
                obras=self.obras_selecionadas
            )

        if success:
            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos()
            self.carregar_transacoes()
        else:
            messagebox.showerror("Erro", msg)

    def limpar_campos(self):
        self.entry_cliente.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.combo_tipo.set("")
        self.text_obs.delete("1.0", tk.END)
        self.entry_data_transacao.set_date(date.today())
        self.entry_data_cadastro.config(state="normal")
        self.entry_data_cadastro.delete(0, tk.END)
        self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_data_cadastro.config(state="readonly")
        self.transacao_selecionada = None
        self.obras_selecionadas = []
        self.label_obras_selecionadas.config(text="Nenhuma obra selecionada")

    # ---------- Carregar ----------
    def carregar_transacoes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for transacao in self.controller.listar_transacoes():
            valores = [transacao.id, transacao.cliente, transacao.valor, transacao.tipo,
                       transacao.data_transacao, transacao.data_cadastro, transacao.observacoes,
                       ", ".join(transacao.obras)]
            try:
                valores[2] = locale.currency(float(valores[2]), grouping=True)
            except Exception:
                valores[2] = f"{float(valores[2]):,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
            self.tree.insert("", tk.END, values=valores)

    def carregar_transacao_selecionada(self, event):
        itens = self.tree.selection()
        if not itens:
            return
        valores = self.tree.item(itens[0], "values")
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
        self.text_obs.insert("1.0", valores[6])
        self.entry_data_cadastro.config(state="normal")
        self.entry_data_cadastro.delete(0, tk.END)
        self.entry_data_cadastro.insert(0, valores[5])
        self.entry_data_cadastro.config(state="readonly")
        self.obras_selecionadas = valores[7].split(', ') if valores[7] else []
        self.label_obras_selecionadas.config(
            text="Obras Selecionadas: " + ", ".join(self.obras_selecionadas) if self.obras_selecionadas else "Nenhuma obra selecionada"
        )

    # ---------- Acessar DB com fallback flexível ----------
    def _fetch_obras_from_db(self, sql="SELECT id_obra, titulo, nome_artista, status FROM obras"):
        """
        Tenta vários caminhos para obter as obras:
        - self.manager.db.cursor()
        - self.manager.cursor() / self.manager.conectar()
        - importar database.manager (módulo) e usar db
        Retorna lista (possivelmente vazia) de rows (cada row pode ser dict-like ou tuple).
        """
        try:
            if self.manager:
                dbobj = getattr(self.manager, "db", None)
                if dbobj and hasattr(dbobj, "cursor"):
                    with dbobj.cursor() as cursor:
                        cursor.execute(sql)
                        return cursor.fetchall()

                if hasattr(self.manager, "conectar"):
                    conn = self.manager.conectar()
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    conn.close()
                    return rows

                if hasattr(self.manager, "cursor"):
                    with self.manager.cursor() as cursor:
                        cursor.execute(sql)
                        return cursor.fetchall()

            # fallback para módulo database.manager
            import database.manager as dbmod
            dbobj = getattr(dbmod, "db", None)
            if dbobj and hasattr(dbobj, "cursor"):
                with dbobj.cursor() as cursor:
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception:
            # retorna lista vazia para UI
            return []
        return []

    def _execute_update(self, sql, params=()):
        """
        Executa um update com vários fallbacks (sem levantar exceções ao UI).
        """
        try:
            if self.manager:
                dbobj = getattr(self.manager, "db", None)
                if dbobj and hasattr(dbobj, "cursor"):
                    with dbobj.cursor() as cursor:
                        cursor.execute(sql, params)
                        # commit se disponível
                        try:
                            dbobj.commit()
                        except Exception:
                            pass
                        return True

                if hasattr(self.manager, "conectar"):
                    conn = self.manager.conectar()
                    cursor = conn.cursor()
                    cursor.execute(sql, params)
                    conn.commit()
                    conn.close()
                    return True

                if hasattr(self.manager, "cursor"):
                    with self.manager.cursor() as cursor:
                        cursor.execute(sql, params)
                        try:
                            self.manager.commit()
                        except Exception:
                            pass
                        return True

            import database.manager as dbmod
            dbobj = getattr(dbmod, "db", None)
            if dbobj and hasattr(dbobj, "cursor"):
                with dbobj.cursor() as cursor:
                    cursor.execute(sql, params)
                    try:
                        dbobj.commit()
                    except Exception:
                        pass
                return True
        except Exception:
            return False
        return False

    # ---------- Selecionar obras ----------
    def abrir_selecionar_obras(self):
        janela_obras = tk.Toplevel(self.root)
        janela_obras.title("Seleção de Obras")
        janela_obras.transient(self.root)
        janela_obras.grab_set()
        self.centralizar_janela(janela_obras, 600, 400)

        colunas = ("ID", "Nome", "Artista", "Status")
        tree_obras = ttk.Treeview(janela_obras, columns=colunas, show="headings", selectmode="extended")
        for col in colunas:
            tree_obras.heading(col, text=col)
            tree_obras.column(col, width=140, anchor="center")
        tree_obras.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        obras = self._fetch_obras_from_db()
        for obra in obras:
            try:
                if isinstance(obra, dict) or hasattr(obra, "get"):
                    id_obra = obra.get("id_obra") or obra.get("id")
                    titulo = obra.get("titulo") or obra.get("nome") or ""
                    artista = obra.get("nome_artista") or obra.get("artista") or ""
                    status = obra.get("status") or ""
                else:
                    id_obra = obra[0] if len(obra) > 0 else ""
                    titulo = obra[1] if len(obra) > 1 else ""
                    artista = obra[2] if len(obra) > 2 else ""
                    status = obra[3] if len(obra) > 3 else ""
            except Exception:
                id_obra = ""
                titulo = str(obra)
                artista = ""
                status = ""

            tree_obras.insert("", tk.END, values=(id_obra, titulo, artista, status))

        frame_botoes = ttk.Frame(janela_obras)
        frame_botoes.pack(pady=10)

        def confirmar_selecao():
            itens = tree_obras.selection()
            selecionadas = [tree_obras.item(i, "values")[1] for i in itens]
            self.obras_selecionadas = selecionadas
            texto = "Obras Selecionadas: " + ", ".join(self.obras_selecionadas) if self.obras_selecionadas else "Nenhuma obra selecionada"
            self.label_obras_selecionadas.config(text=texto)
            janela_obras.destroy()

        ttk.Button(frame_botoes, text="Confirmar Seleção", command=confirmar_selecao).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=janela_obras.destroy).pack(side="left", padx=10)

    def voltar_inicio(self):
        """
        Segue o mesmo padrão das outras views: não fecha o root, apenas reconstrói (ou instancia) a tela inicial
        passando o manager para manter a sessão/DB.
        """
        try:
            from views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import).")
            return

        for w in self.root.winfo_children():
            w.destroy()
        TelaInicial(self.root, self.manager)

    # ---------- Registrar devolução ----------
    def abrir_devolucao(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Atenção", "Selecione uma transação para registrar devolução.")
            return
        valores = self.tree.item(item[0], "values")
        id_transacao, cliente, valor, tipo, data_transacao, _, observacoes_orig, obras_orig = valores

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
            data_trans = datetime.strptime(data_transacao, "%d/%m/%Y").date()
            if data_dev <= data_trans:
                messagebox.showerror("Erro", "A data de devolução deve ser posterior à data da transação original.")
                return

            data_dev_str = data_dev.strftime("%d/%m/%Y")
            obras_list = [o.strip() for o in obras_orig.split(",") if o.strip()]

            # Atualiza status das obras no banco
            for obra in obras_list:
                updated = self._execute_update("UPDATE obras SET status='Disponível' WHERE titulo=?", (obra,))
                if not updated:
                    self._execute_update("UPDATE obras SET status='Disponível' WHERE titulo=%s", (obra,))

            observacoes_dev = f"Devolução de {tipo}: ID {id_transacao}."
            self.controller.registrar_devolucao(
                transacao_id=id_transacao,
                data_devolucao=data_dev_str,
                observacoes=observacoes_dev,
                obras=obras_list
            )

            messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
            win_dev.destroy()
            self.carregar_transacoes()

        ttk.Button(frame_btn, text="Cancelar", command=win_dev.destroy).pack(side="left", padx=10, expand=True, fill="x")
        ttk.Button(frame_btn, text="Confirmar", command=confirmar).pack(side="left", padx=10, expand=True, fill="x")
