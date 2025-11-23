import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from PIL import Image, ImageTk
from src.controllers.obra_controller import ObraController
from src.models.obra_model import StatusObra

class ObraView:
    def __init__(self, root, manager=None):
        self.root = root
        self.manager = manager
        self.controller = ObraController()
        self.root.title("Sistema de Gestão de Galeria de Arte")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.imagem_path = None
        self.artistas_selecionados = []
        self.criar_interface()
        
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
        frm_cadastro = ttk.LabelFrame(self.root, text="Cadastro de Obras", padding=10)
        frm_cadastro.pack(fill="x", padx=10, pady=8)
        for i in range(9):
            frm_cadastro.columnconfigure(i, weight=1, uniform="col")

        # --- Linha 1: Ano, Título, Técnica, Dimensões --- #
        campos = [
            ("Título:", "titulo_entry", 25),
            ("Ano:", "ano_entry", 15),
            ("Técnica:", "tecnica_entry", 20),
            ("Dimensões:", "dimensoes_entry", 20)
        ]
        for idx, (label_text, attr_name, width) in enumerate(campos):
            col_label = idx * 2
            col_entry = idx * 2 + 1
            ttk.Label(frm_cadastro, text=label_text).grid(row=0, column=col_label, sticky="w", padx=(10,5), pady=5)
            entry = ttk.Entry(frm_cadastro)
            entry.grid(row=0, column=col_entry, sticky="ew", padx=(5,10), pady=5)
            setattr(self, attr_name, entry)

        # --- Linha 2: Tipo, Status, Localização, Preço --- #
        campos2 = [("Tipo:", "tipo_combo", self.controller.get_tipos_obra(), 1),
                ("Status:", "status_combo", [""] + self.controller.get_status_obra(), 3),
                ("Localização:", "localizacao_entry", None, 5),
                ("Preço:", "preco_entry", None, 7)]
        for label_text, attr_name, values, col in campos2:
            ttk.Label(frm_cadastro, text=label_text).grid(row=1, column=col-1, sticky="w", padx=(10,5), pady=5)
            if "combo" in attr_name:
                combo = ttk.Combobox(frm_cadastro, values=values, state="readonly")
                combo.grid(row=1, column=col, sticky="ew", padx=(5,10), pady=5)
                if attr_name=="status_combo": combo.set("Disponível")
                setattr(self, attr_name, combo)
            else:
                entry = ttk.Entry(frm_cadastro)
                entry.grid(row=1, column=col, sticky="ew", padx=(5,10), pady=5)
                if attr_name=="preco_entry": entry.insert(0, "0.00")
                setattr(self, attr_name, entry)

        # --- Linha 3: Data e Imagem --- #
        ttk.Label(frm_cadastro, text="Data cadastro:").grid(row=2, column=0, sticky="w", padx=(10,5), pady=5)
        self.data_entry = ttk.Entry(frm_cadastro)
        self.data_entry.grid(row=2, column=1, sticky="ew", padx=(5,10), pady=5)
        self.data_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        ttk.Label(frm_cadastro, text="(DD/MM/AAAA)", font=("Arial", 8), foreground="gray").grid(row=3, column=0, columnspan=2, sticky="w", padx=(10,5), pady=(0,5))
        self.atualizar_data()

        ttk.Label(frm_cadastro, text="Imagem:").grid(row=2, column=2, sticky="w", padx=(10,5), pady=5)
        imagem_frame = ttk.Frame(frm_cadastro)
        imagem_frame.grid(row=2, column=3, columnspan=3, sticky="ew", padx=5, pady=5)
        imagem_frame.columnconfigure(0, weight=1)

        self.preview_frame = ttk.Frame(imagem_frame)
        self.preview_frame.grid(row=0, column=0, padx=(0,10), sticky="w")

        self.imagem_label = ttk.Label(
            self.preview_frame,
            text="Nenhuma imagem",
            relief="solid",
            width=22,
            anchor="center"
        )
        self.imagem_label.grid(row=0, column=0, pady=(0,5))

        botoes_imagem_frame = ttk.Frame(self.preview_frame)
        botoes_imagem_frame.grid(row=1, column=0, pady=5)
        ttk.Button(botoes_imagem_frame, text="Selecionar", command=self.selecionar_imagem, width=10).grid(row=0, column=0, padx=(0,4))
        ttk.Button(botoes_imagem_frame, text="Visualizar", command=self.visualizar_imagem, width=10).grid(row=0, column=1, padx=4)
        ttk.Button(botoes_imagem_frame, text="Remover", command=self.remover_imagem, width=10).grid(row=0, column=2, padx=4)

        # --- Linha 3: Artistas --- #
        ttk.Label(frm_cadastro, text="Artista(s):").grid(row=2, column=6, sticky="w", padx=(10,5), pady=5)
        self.botao_artistas = ttk.Button(frm_cadastro, text="Selecionar Artistas", command=self.abrir_selecionar_artistas, width=18)
        self.botao_artistas.grid(row=2, column=7, sticky="ew", padx=5, pady=5)
        self.label_artistas_selecionados = ttk.Label(frm_cadastro, text="Nenhum artista selecionado", wraplength=300, justify="left", foreground="gray")
        self.label_artistas_selecionados.grid(row=3, column=0, columnspan=8, sticky="w", padx=10, pady=(0,5))

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
        btns_frame.grid(row=0, column=8, rowspan=3, sticky="n", padx=10, pady=5)
        self.botao_salvar = ttk.Button(btns_frame, text="Salvar", command=self.salvar_obra, width=16)
        self.botao_salvar.pack(pady=4)
        ttk.Button(btns_frame, text="Cancelar", command=self.limpar_form, width=16).pack(pady=4)
        ttk.Button(btns_frame, text="Remover", command=self.remover_visual, width=16).pack(pady=4)

        # --- FRAME DE LISTAGEM --- #
        listagem_frame = ttk.LabelFrame(self.root, text="Listagem de Obras", padding=10)
        listagem_frame.pack(fill="both", expand=True, padx=10, pady=5)
        listagem_frame.columnconfigure(0, weight=1)
        listagem_frame.rowconfigure(0, weight=1)
        colunas = ("ID", "Título", "Artista", "Tipo", "Ano", "Técnica", "Dimensões", "Localização", "Preço")
        self.tree = ttk.Treeview(listagem_frame, columns=colunas, show="headings")
        style.configure("Treeview", bordercolor="#d0d0d0", relief="solid")
        for c in colunas:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, minwidth=50, anchor="w", stretch=True)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(listagem_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(listagem_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        listagem_frame.grid_rowconfigure(0, weight=1)
        listagem_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", self.editar_obra)
        self.carregar_obras()

    # ---------------------- IMAGEM ---------------------- #
    def selecionar_imagem(self):
        try:
            filename = filedialog.askopenfilename(
                title="Selecionar Imagem",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
            )
            if filename:
                self.imagem_path = filename
                nome_arquivo = filename.split("/")[-1]
                self.imagem_label.config(text=nome_arquivo[:20] + "..." if len(nome_arquivo) > 20 else nome_arquivo)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar imagem: {str(e)}")

    def carregar_preview_imagem(self, caminho_imagem):
        try:
            imagem = Image.open(caminho_imagem)
            imagem.thumbnail((150, 100), Image.Resampling.LANCZOS)
            self.imagem_tk = ImageTk.PhotoImage(imagem)
            self.imagem_label.config(image=self.imagem_tk, text="")
            nome_arquivo = caminho_imagem.split("/")[-1]
            self.criar_tooltip(self.imagem_label, f"Arquivo: {nome_arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar preview da imagem: {str(e)}")
            self.imagem_label.config(image="", text="Erro ao carregar")

    def visualizar_imagem(self):
        if not self.imagem_path:
            messagebox.showwarning("Aviso", "Nenhuma imagem selecionada")
            return
        try:
            janela_imagem = tk.Toplevel(self.root)
            janela_imagem.title("Visualizar Imagem")
            janela_imagem.geometry("600x500")
            janela_imagem.resizable(True, True)
            canvas = tk.Canvas(janela_imagem)
            scrollbar_v = ttk.Scrollbar(janela_imagem, orient="vertical", command=canvas.yview)
            scrollbar_h = ttk.Scrollbar(janela_imagem, orient="horizontal", command=canvas.xview)
            canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
            imagem_original = Image.open(self.imagem_path)
            if imagem_original.width > 800 or imagem_original.height > 600:
                imagem_original.thumbnail((800, 600), Image.Resampling.LANCZOS)
            imagem_tk_grande = ImageTk.PhotoImage(imagem_original)
            canvas.create_image(0, 0, anchor="nw", image=imagem_tk_grande)
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")
            janela_imagem.imagem_tk_grande = imagem_tk_grande
            info_frame = ttk.Frame(janela_imagem)
            info_frame.pack(side="bottom", fill="x", padx=10, pady=5)
            nome_arquivo = self.imagem_path.split("/")[-1]
            ttk.Label(info_frame, text=f"Arquivo: {nome_arquivo}").pack(side="left")
            ttk.Label(info_frame, text=f"Tamanho: {imagem_original.width}x{imagem_original.height}").pack(side="right")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao visualizar imagem: {str(e)}")

    def remover_imagem(self):
        if self.imagem_path:
            resposta = messagebox.askyesno("Confirmar", "Remover a imagem selecionada?")
            if resposta:
                self.imagem_path = None
                self.imagem_tk = None
                self.imagem_label.config(image="", text="Nenhuma imagem")

    def criar_tooltip(self, widget, texto):
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=texto, background="lightyellow", relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            tooltip.after(3000, tooltip.destroy)
        widget.bind("<Enter>", mostrar_tooltip)

    # ---------------------- DATA ---------------------- #
    def atualizar_data(self):
        data_atual = date.today().strftime("%d/%m/%Y")
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, data_atual)

    # ---------------------- ARTISTAS ---------------------- #
    def obter_artistas(self):
        return getattr(self, 'artistas_selecionados', [])

    # ---------------------- CADASTRO / EDIÇÃO ---------------------- #
    def salvar_obra(self):
        try:
            titulo = self.titulo_entry.get().strip()
            ano = self.ano_entry.get().strip()
            artistas = self.obter_artistas()
            tipo = self.tipo_combo.get()
            tecnica = self.tecnica_entry.get().strip()
            dimensoes = self.dimensoes_entry.get().strip()
            localizacao = self.localizacao_entry.get().strip()
            preco = self.preco_entry.get().strip()
            status = StatusObra.DISPONIVEL
            data_cadastro_str = self.data_entry.get().strip()  # Capturar data digitada

            if not artistas:
                messagebox.showerror("Erro", "Adicione pelo menos um artista")
                return

            if hasattr(self, 'obra_em_edicao') and self.obra_em_edicao:
                status = self.obra_em_edicao.status
                sucesso, mensagem = self.controller.atualizar_obra(
                    self.obra_em_edicao.id_obra, titulo, ano, artistas, tipo, 
                    tecnica, dimensoes, localizacao, preco, status, self.imagem_path,
                    data_cadastro_str  # Passar data para o controller
                )
            else:
                sucesso, mensagem = self.controller.cadastrar_obra(
                    titulo, ano, artistas, tipo, tecnica, dimensoes, 
                    localizacao, preco, status, self.imagem_path,
                    data_cadastro_str  # Passar data para o controller
                )

            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.limpar_form()
                self.carregar_obras()
            else:
                messagebox.showerror("Erro", mensagem)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

    def limpar_form(self):
        self.titulo_entry.delete(0, tk.END)
        self.ano_entry.delete(0, tk.END)
        self.tipo_combo.set('')
        self.tecnica_entry.delete(0, tk.END)
        self.dimensoes_entry.delete(0, tk.END)
        self.localizacao_entry.delete(0, tk.END)
        self.preco_entry.delete(0, tk.END)
        self.preco_entry.insert(0, "0.00")
        try:
            self.status_combo.config(state="readonly")
        except:
            pass
        self.status_combo.set("")  # Combobox vazio

        self.artistas_selecionados = []
        self.label_artistas_selecionados.config(text="Nenhum artista selecionado")

        self.imagem_path = None
        self.imagem_tk = None
        self.imagem_label.config(image="", text="Nenhuma imagem")

        self.atualizar_data()

        if hasattr(self, 'obra_em_edicao'):
            self.obra_em_edicao = None

        if hasattr(self, 'botao_salvar'):
            self.botao_salvar.config(text="Salvar")

    def remover_visual(self):
        try:
            sel = self.tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione uma obra para remover")
                return
            for item in sel:
                self.tree.delete(item)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover: {str(e)}")

    def carregar_obras(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            obras = self.controller.listar_obras()
            for obra in obras:
                artistas_text = obra.artistas_str
                self.tree.insert("", tk.END, values=(
                     obra.id_obra,
                     obra.titulo,
                     artistas_text,
                     obra.tipo,
                     obra.ano,
                     obra.tecnica,
                     obra.dimensoes,
                     obra.localizacao,
                     f"R$ {obra.preco:.2f}".replace(".", ",")
                 ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar obras: {str(e)}")

    def editar_obra(self, event):
        try:
            item = self.tree.selection()[0]
            obra_id = int(self.tree.item(item, "values")[0])
            obra = self.controller.buscar_obra_por_id(obra_id)
            if not obra:
                messagebox.showerror("Erro", "Obra não encontrada")
                return
            if obra.status.value == "Vendida" or obra.status == StatusObra.VENDIDA:
                messagebox.showwarning("Aviso", "Obras vendidas não podem ser editadas")
                return
            self.preencher_formulario_edicao(obra)
            self.obra_em_edicao = obra
            self.botao_salvar.config(text="Atualizar")
        except IndexError:
            pass
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar obra para edição: {str(e)}")

    def preencher_formulario_edicao(self, obra):
        self.limpar_form()
        self.titulo_entry.insert(0, obra.titulo)
        self.ano_entry.insert(0, str(obra.ano))
        self.tipo_combo.set(obra.tipo)
        self.tecnica_entry.insert(0, obra.tecnica or "")
        self.dimensoes_entry.insert(0, obra.dimensoes or "")
        self.localizacao_entry.insert(0, obra.localizacao or "")
        self.preco_entry.delete(0, tk.END)
        self.preco_entry.insert(0, str(obra.preco))
        self.status_combo.set(obra.status.value)
        self.status_combo.config(state="disabled")

        if obra.data_cadastro:
            self.data_entry.config(state="normal")
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, obra.data_cadastro.strftime("%d/%m/%Y"))
            self.data_entry.config(state="readonly")

        if obra.data_cadastro:
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, obra.data_cadastro.strftime("%d/%m/%Y"))

        if obra.imagem:
            self.imagem_path = obra.imagem
            if isinstance(obra.imagem, str) and obra.imagem.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                try:
                    self.carregar_preview_imagem(obra.imagem)
                except:
                    nome_arquivo = obra.imagem.split("/")[-1]
                    self.imagem_label.config(text=nome_arquivo[:15] + "..." if len(nome_arquivo) > 15 else nome_arquivo)
            else:
                self.imagem_label.config(text="Imagem carregada")

    # ---------------------- SELEÇÃO DE ARTISTAS ---------------------- #
    def abrir_selecionar_artistas(self):
        janela_artistas = tk.Toplevel(self.root)
        janela_artistas.title("Seleção de Artistas")
        janela_artistas.transient(self.root)
        janela_artistas.grab_set()
        largura, altura = 500, 400
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        janela_artistas.geometry(f"{largura}x{altura}+{x}+{y}")

        colunas = ("ID", "Nome", "Nacionalidade", "Nascimento")
        tree_artistas = ttk.Treeview(janela_artistas, columns=colunas, show="headings", selectmode="extended")
        for col in colunas:
            tree_artistas.heading(col, text=col)
            tree_artistas.column(col, width=120, anchor="center")
        tree_artistas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        artistas = self.manager.listar_artistas()
        for artista in artistas:
            tree_artistas.insert("", tk.END, values=(artista.id_artista, artista.nome, artista.nacionalidade, artista.nascimento))

        frame_botoes = ttk.Frame(janela_artistas)
        frame_botoes.pack(pady=10)

        def confirmar_selecao():
            itens = tree_artistas.selection()
            selecionados = [tree_artistas.item(i, "values")[1] for i in itens]
            self.artistas_selecionados = selecionados
            texto = "Artistas Selecionados: " + ", ".join(self.artistas_selecionados) \
                    if self.artistas_selecionados else "Nenhum artista selecionado"
            self.label_artistas_selecionados.config(text=texto)
            janela_artistas.destroy()

        ttk.Button(frame_botoes, text="Confirmar Seleção", command=confirmar_selecao).pack(side="left", padx=10)
        ttk.Button(frame_botoes, text="Cancelar", command=janela_artistas.destroy).pack(side="left", padx=10)

    def centralizar_janela(self, janela, largura, altura):
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

    def voltar_inicio(self):
        try:
            from src.views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import).")
            return
        for w in self.root.winfo_children():
            w.destroy()
        TelaInicial(self.root, self.manager)

    def run(self):
        self.root.mainloop()
