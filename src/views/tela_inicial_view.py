import tkinter as tk
from tkinter import ttk, messagebox
from src.views.obra_view import ObraView
from src.views.artista_view import ArtistaView
from src.views.transacao_view import TransacaoView
#from src.views.cronograma_view import CronogramaView
from src.views.exposicao_view import ExposicaoView
from src.views.relatorio_obra_view import RelatorioObrasView


class TelaInicial:
    def __init__(self, root, manager):
        self.root = root
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
        style.configure("TLabel", background=bg)

        # --- Título ---
        titulo = tk.Label(
            self.root,
            text="Sistema de Gestão de Galeria de Arte",
            font=("Segoe UI", 18, "bold"),
            bg=bg,
            fg="#333333",
            anchor="center"
        )
        titulo.pack(fill="x", pady=(20,10))

        # --- Frame superior ---
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=20, pady=(0,10))
        top_frame.columnconfigure(0, weight=1)

        # Notificações
        self.btn_notificacoes = tk.Button(
            top_frame, text="🔔", font=("Segoe UI Emoji", 16), bd=0, bg=bg,
            activebackground="#dddddd", cursor="hand2", command=self.abrir_notificacoes
        )
        self.btn_notificacoes.grid(row=0, column=1, sticky="e", padx=(0,5))

        # Backup
        self.btn_backup = ttk.Button(top_frame, text="Backup", command=self.fazer_backup)
        self.btn_backup.grid(row=0, column=2, sticky="e")

        # --- Frame central com cards ---
        self.frame_central = ttk.Frame(self.root)
        self.frame_central.pack(expand=True, fill="both", padx=20, pady=10)

        self.cards = [
            ("Cadastro de Obras", "🖼️", self.abrir_obras),
            ("Cadastro de Artistas", "👨‍🎨", self.abrir_artistas),
            ("Cadastro de Transações", "💰", self.abrir_transacoes),
            ("Exposições", "🏛️", self.abrir_exposicoes),
            ("Cronogramas", "📆", self.abrir_cronogramas),
            ("Relatórios", "📊", self.abrir_relatorios),
        ]

        rows, cols = 2, 3
        for i in range(rows):
            self.frame_central.rowconfigure(i, weight=1, uniform="row")
        for j in range(cols):
            self.frame_central.columnconfigure(j, weight=1, uniform="col")

        for idx, (nome, icone, comando) in enumerate(self.cards):
            row, col = divmod(idx, cols)

            card = tk.Frame(
                self.frame_central,
                bg="#ffffff",
                highlightbackground="#bbbbbb",
                highlightthickness=1,
                relief="flat",
                cursor="hand2",
                width=200,
                height=150
            )
            card.grid(row=row, column=col, sticky="nsew", padx=20, pady=20)
            card.grid_propagate(False)

            lbl_icon = tk.Label(card, text=icone, font=("Segoe UI Emoji", 40), bg="#ffffff", cursor="hand2")
            lbl_icon.pack(expand=True, fill="both")

            lbl_text = tk.Label(card, text=nome, font=("Segoe UI", 12, "bold"), bg="#ffffff", cursor="hand2")
            lbl_text.pack(pady=(5,10))

            card.bind("<Button-1>", lambda e, cmd=comando: cmd())
            lbl_icon.bind("<Button-1>", lambda e, cmd=comando: cmd())
            lbl_text.bind("<Button-1>", lambda e, cmd=comando: cmd())

    # -------------------- Métodos para abrir views --------------------
    def _open_view(self, view_class):
        for widget in self.root.winfo_children():
            widget.destroy()
        view_class(self.root, manager=self.manager)

    def abrir_obras(self):
        self._open_view(ObraView)

    def abrir_artistas(self):
        self._open_view(ArtistaView)

    def abrir_transacoes(self):
        self._open_view(TransacaoView)

    def abrir_exposicoes(self):
        self._open_view(ExposicaoView)

    def abrir_cronogramas(self):
        messagebox.showinfo("Clique", "Abrir Cronogramas ainda não implementado.")
        #self._open_view(CronogramaView)

    def abrir_relatorios(self):
        self._open_view(RelatorioObrasView)

    def fazer_backup(self):
        messagebox.showinfo("Backup", "Backup ainda não implementado.")

    def abrir_notificacoes(self):
        messagebox.showinfo("Clique", "Notificações ainda não implementado.")
