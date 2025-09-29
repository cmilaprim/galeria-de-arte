import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.artista_controller import ArtistaController

NACIONALIDADES = ["Brasil","Argentina","Chile","Espanha","Portugal","França","Itália","Alemanha","Estados Unidos","Outro"]
ESPECIALIDADES = ["Pintura","Escultura","Fotografia","Gravura","Instalação","Performance","Outros"]

class ArtistaView:
    def __init__(self):
        self.controller = ArtistaController()
        self.root = tk.Tk()
        self.root.title("Cadastro de Artista")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 700)

        # tema claro
        bg = "#F3F4F6"  # cinza bem claro
        self.root.configure(bg=bg)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg)
        style.configure("TLabel", background=bg)

        self._id_atual = None
        self._montar_ui()
        self._carregar_lista()

    def _montar_ui(self):
        frm = ttk.LabelFrame(self.root, text="Cadastro de Artista", padding=10)
        frm.pack(fill=tk.X, padx=10, pady=8)

        for i in range(8):
            frm.columnconfigure(i, weight=1)

        # Nome
        ttk.Label(frm, text="Nome:").grid(row=0, column=0, sticky="w")
        self.nome = ttk.Entry(frm)
        self.nome.grid(row=0, column=0, sticky="ew", padx=(50, 15), pady=(0, 15))

        # Nascimento
        ttk.Label(frm, text="Nascimento (DD/MM/YYYY):").grid(row=0, column=1, sticky="w")
        self.nascimento = ttk.Entry(frm)
        self.nascimento.grid(row=0, column=1, sticky="ew", padx=(180, 15), pady=(0, 15))

        # Nacionalidade (combobox)
        ttk.Label(frm, text="Nacionalidade:").grid(row=0, column=2, sticky="w")
        self.nacionalidade = ttk.Combobox(frm, values=NACIONALIDADES, state="readonly")
        self.nacionalidade.grid(row=0, column=2, sticky="ew", padx=(120, 15), pady=(0, 15))

        # Especialidade (combobox)
        ttk.Label(frm, text="Especialidade:").grid(row=1, column=0, sticky="w")
        self.especialidade = ttk.Combobox(frm, values=ESPECIALIDADES, state="readonly")
        self.especialidade.grid(row=1, column=0, sticky="ew", padx=(110, 15), pady=(0, 15))

        # Status (combobox)
        ttk.Label(frm, text="Status:").grid(row=1, column=1, sticky="w")
        self.status = ttk.Combobox(frm, values=self.controller.get_status(), state="readonly")
        self.status.grid(row=1, column=1, sticky="ew", padx=(60, 15), pady=(0, 15))

        # Data cadastro
        ttk.Label(frm, text="Data cadastro (DD/MM/YYYY):").grid(row=1, column=2, sticky="w")
        self.data_cadastro = ttk.Entry(frm)
        self.data_cadastro.grid(row=1, column=2, sticky="ew", padx=(210, 15), pady=(0, 15))

        # Biografia (Text com fundo branco)
        ttk.Label(frm, text="Biografia:").grid(row=2, column=0, sticky="nw")
        self.biografia = tk.Text(frm, height=5, bg="white", fg="black", insertbackground="black")
        self.biografia.grid(row=2, column=0, columnspan=3, sticky="ew", padx=(70, 15), pady=(0, 5))

        # Botões (somente Salvar / Cancelar / Buscar)
        btns = ttk.Frame(frm)
        btns.grid(row=0, column=3, rowspan=3, sticky="n", padx=10)
        ttk.Button(btns, text="Salvar", command=self._salvar, width=16).pack(pady=4)
        ttk.Button(btns, text="Limpar", command=self._limpar, width=16).pack(pady=4)
        ttk.Button(btns, text="Buscar", command=self._buscar, width=16).pack(pady=4)

        # Lista
        lista_frame = ttk.LabelFrame(self.root, text="Listagem de Artistas", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        colunas = ("ID", "Nome", "Nascimento", "Nacionalidade", "Especialidade", "Status", "Data Cadastro")
        self.tree = ttk.Treeview(lista_frame, columns=colunas, show="headings")
        for c, w in zip(colunas, (60, 220, 140, 160, 160, 100, 140)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        yscroll = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # --- ações ---
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
            self._carregar_lista()  # lista todos
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
        # Preenche formulário para possível edição
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

    def run(self):
        self.root.mainloop()
