import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.artista_controller import ArtistaController

NACIONALIDADES = ["Brasil","Argentina","Chile","Espanha","Portugal","França","Itália","Alemanha","Estados Unidos","Outro"]
ESPECIALIDADES = ["Pintura","Escultura","Fotografia","Gravura","Instalação","Performance","Outros"]

class ArtistaView:
    def __init__(self, root, controller=None, manager=None):
        self.root = root

        for w in self.root.winfo_children():
            w.destroy()

        self.controller = controller or ArtistaController()
        self.manager = manager

        self.root.title("Sistema de Gestão de Galeria de Arte")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        bg = "#F3F4F6"
        self.root.configure(bg=bg)
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg)
        style.configure("TLabel", background=bg)

        self._id_atual = None
        self.criar_interface()
        self._carregar_lista()

    def criar_interface(self):
        # --- Frame de cadastro ---
        frm_cadastro = ttk.LabelFrame(self.root, text="Cadastro de Artista", padding=10)
        frm_cadastro.pack(fill="x", padx=10, pady=8)

        for i in range(3):
            frm_cadastro.columnconfigure(i, weight=1, uniform="col")
        frm_cadastro.columnconfigure(3, weight=0)

        # Linha 1
        ttk.Label(frm_cadastro, text="Nome:").grid(row=0, column=0, sticky="w", padx=(5,2), pady=5)
        self.nome = ttk.Entry(frm_cadastro)
        self.nome.grid(row=0, column=0, sticky="ew", padx=(70,10), pady=5)

        ttk.Label(frm_cadastro, text="Nascimento (DD/MM/YYYY):").grid(row=0, column=1, sticky="w", padx=(5,2), pady=5)
        self.nascimento = ttk.Entry(frm_cadastro)
        self.nascimento.grid(row=0, column=1, sticky="ew", padx=(70,10), pady=5)

        ttk.Label(frm_cadastro, text="Nacionalidade:").grid(row=0, column=2, sticky="w", padx=(5,2), pady=5)
        self.nacionalidade = ttk.Combobox(frm_cadastro, values=NACIONALIDADES, state="readonly")
        self.nacionalidade.grid(row=0, column=2, sticky="ew", padx=(70,10), pady=5)

        # Linha 2
        ttk.Label(frm_cadastro, text="Especialidade:").grid(row=1, column=0, sticky="w", padx=(5,2), pady=5)
        self.especialidade = ttk.Combobox(frm_cadastro, values=ESPECIALIDADES, state="readonly")
        self.especialidade.grid(row=1, column=0, sticky="ew", padx=(90,10), pady=5)

        ttk.Label(frm_cadastro, text="Status:").grid(row=1, column=1, sticky="w", padx=(5,2), pady=5)
        self.status = ttk.Combobox(frm_cadastro, values=self.controller.get_status(), state="readonly")
        self.status.grid(row=1, column=1, sticky="ew", padx=(50,10), pady=5)

        ttk.Label(frm_cadastro, text="Data cadastro:").grid(row=1, column=2, sticky="w", padx=(5,2), pady=5)
        self.data_cadastro = ttk.Entry(frm_cadastro)
        self.data_cadastro.grid(row=1, column=2, sticky="ew", padx=(100,10), pady=5)

        # Linha 3 - Biografia
        ttk.Label(frm_cadastro, text="Biografia:").grid(row=2, column=0, sticky="nw", padx=(5,2), pady=5)
        self.biografia = tk.Text(frm_cadastro, height=5, bg="white", fg="black", insertbackground="black")
        self.biografia.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=(70,10), pady=(0,5))
        frm_cadastro.rowconfigure(2, weight=1)

        # --- Botões ---
        btns = ttk.Frame(frm_cadastro)
        btns.grid(row=0, column=3, rowspan=3, sticky="n", padx=10)

        # Botão Home (Voltar)
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

        ttk.Button(btns, text="Salvar", command=self._salvar, width=16).pack(pady=4)
        ttk.Button(btns, text="Cancelar", command=self._limpar, width=16).pack(pady=4)
        ttk.Button(btns, text="Buscar", command=self._buscar, width=16).pack(pady=4)

        # --- Frame de listagem ---
        lista_frame = ttk.LabelFrame(self.root, text="Listagem de Artistas", padding=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        colunas = ("ID", "Nome", "Nascimento", "Nacionalidade", "Especialidade", "Status", "Data Cadastro")
        self.tree = ttk.Treeview(lista_frame, columns=colunas, show="headings")
        for c, w in zip(colunas, (60,220,140,160,160,100,140)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # --- Ações ---
    def _salvar(self):
        ok, msg = self.controller.salvar(
            self._id_atual,
            self.nome.get(),
            self.nascimento.get(),
            self.nacionalidade.get(),
            self.especialidade.get(),
            self.status.get(),
            self.data_cadastro.get(),
            self.biografia.get("1.0", tk.END).strip()
        )
        if ok:
            messagebox.showinfo("Artistas", msg)
            self._limpar()
            self._carregar_lista()
        else:
            messagebox.showerror("Artistas", msg)

    def _buscar(self):
        filtros = {
            "nome": self.nome.get().strip(),
            "nascimento": self.nascimento.get().strip().replace("DD/MM/YYYY", "").strip(),
            "nacionalidade": (self.nacionalidade.get() or "").strip(),
            "especialidade": (self.especialidade.get() or "").strip(),
            "status": (self.status.get() or "").strip(),
            "data_cadastro": self.data_cadastro.get().strip().replace("DD/MM/YYYY", "").strip(),
        }
        artistas = self.controller.buscar(filtros)
        self._preencher_tree(artistas)

    def _carregar_lista(self):
        self._preencher_tree(self.controller.listar())

    def _preencher_tree(self, artistas):
        for i in self.tree.get_children(): self.tree.delete(i)
        for a in artistas:
            self.tree.insert("", tk.END, values=(
                a.id_artista, a.nome, a.nascimento, a.nacionalidade,
                a.especialidade, a.status.value, a.data_cadastro
            ))

    def _on_select(self, _):
        item = self.tree.focus()
        if not item: return
        vals = self.tree.item(item, "values")
        art = self.controller.carregar(vals[0])
        if not art: return
        self._id_atual = art.id_artista
        self.nome.delete(0, tk.END); self.nome.insert(0, art.nome)
        self.nascimento.delete(0, tk.END); self.nascimento.insert(0, art.nascimento)
        self.nacionalidade.set(art.nacionalidade)
        self.especialidade.set(art.especialidade)
        self.status.set(art.status.value)
        self.data_cadastro.delete(0, tk.END); self.data_cadastro.insert(0, art.data_cadastro)
        self.biografia.delete("1.0", tk.END); self.biografia.insert("1.0", art.biografia)

    def _limpar(self):
        self._id_atual = None
        self.nome.delete(0, tk.END)
        self.nascimento.delete(0, tk.END)
        self.nacionalidade.set("")
        self.especialidade.set("")
        self.status.set("")
        self.data_cadastro.delete(0, tk.END)
        self.biografia.delete("1.0", tk.END)

    def voltar_inicio(self):
        try:
            from src.views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import).")
            return
        for w in self.root.winfo_children():
            w.destroy()
        TelaInicial(self.root, self.manager)
