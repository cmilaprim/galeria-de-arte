import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from PIL import Image, ImageTk
from ..controllers.obra_controller import ObraController
from ..models.obra_model import StatusObra

class ObraView:
    def __init__(self):
        self.controller = ObraController()
        self.root = tk.Tk()
        self.root.title("Sistema de Galeria de Arte")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.imagem_path = None
        self.criar_interface()
        
    def criar_interface(self):
        cadastro_frame = ttk.LabelFrame(self.root, text="Cadastro de Obras", padding=15)
        cadastro_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i in range(4):
            cadastro_frame.columnconfigure(i, weight=1, minsize=250)
        
        #primeira linha -> ano, titulo, tecnica, dimensoes
        #coluna 0 - ano
        ttk.Label(cadastro_frame, text="Ano:").grid(row=0, column=0, sticky=tk.W, padx=(5, 0), pady=5)
        self.ano_entry = ttk.Entry(cadastro_frame, width=15)
        self.ano_entry.grid(row=0, column=0, sticky=tk.EW, padx=(50, 15), pady=5)
        
        #coluna 1 - titulo
        ttk.Label(cadastro_frame, text="Título:").grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.titulo_entry = ttk.Entry(cadastro_frame, width=25)
        self.titulo_entry.grid(row=0, column=1, sticky=tk.EW, padx=(60, 15), pady=5)
        
        #coluna 2 - tecnica
        ttk.Label(cadastro_frame, text="Técnica:").grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        self.tecnica_entry = ttk.Entry(cadastro_frame, width=20)
        self.tecnica_entry.grid(row=0, column=2, sticky=tk.EW, padx=(70, 15), pady=5)
        
        #coluna 3 - dimensoes
        ttk.Label(cadastro_frame, text="Dimensões:").grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        self.dimensoes_entry = ttk.Entry(cadastro_frame, width=20)
        self.dimensoes_entry.grid(row=0, column=3, sticky=tk.EW, padx=(85, 15), pady=5)
        
        #segunda linha: tipo, status, locali, preco
        #coluna 0 - tipo
        ttk.Label(cadastro_frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W, padx=(5, 0), pady=5)
        self.tipo_combo = ttk.Combobox(cadastro_frame, values=self.controller.get_tipos_obra(), state="readonly", width=13)
        self.tipo_combo.grid(row=1, column=0, sticky=tk.EW, padx=(50, 15), pady=5)
        
        #coluna 1 - status
        ttk.Label(cadastro_frame, text="Status:").grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        self.status_combo = ttk.Combobox(cadastro_frame, values=self.controller.get_status_obra(), 
                                        state="readonly", width=18)
        self.status_combo.grid(row=1, column=1, sticky=tk.EW, padx=(60, 15), pady=5)
        self.status_combo.set("Disponível")
        
        #coluna 2 - locali
        ttk.Label(cadastro_frame, text="Localização:").grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5)
        self.localizacao_entry = ttk.Entry(cadastro_frame, width=18)
        self.localizacao_entry.grid(row=1, column=2, sticky=tk.EW, padx=(90, 15), pady=5)
        
        #coluna 3 - preco
        ttk.Label(cadastro_frame, text="Preço:").grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        self.preco_entry = ttk.Entry(cadastro_frame, width=15)
        self.preco_entry.grid(row=1, column=3, sticky=tk.EW, padx=(60, 15), pady=5)
        self.preco_entry.insert(0, "0.00")
        
        #terceira linha: data e imagem
        #coluna 0 - data
        ttk.Label(cadastro_frame, text="Data cadastro:").grid(row=2, column=0, sticky=tk.W, padx=(5, 0), pady=5)
        self.data_entry = ttk.Entry(cadastro_frame, width=13, state="readonly")
        self.data_entry.grid(row=2, column=0, sticky=tk.EW, padx=(100, 15), pady=5)
        self.atualizar_data()
        
        #coluna 1 - imagem
        ttk.Label(cadastro_frame, text="Imagem:").grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        imagem_frame = ttk.Frame(cadastro_frame)
        imagem_frame.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=(70, 15), pady=5)
        
        self.preview_frame = ttk.Frame(imagem_frame)
        self.preview_frame.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        self.imagem_label = ttk.Label(self.preview_frame, text="Nenhuma imagem", relief="solid", width=20, anchor="center")
        self.imagem_label.grid(row=0, column=0, pady=(0, 5))
        
        botoes_imagem_frame = ttk.Frame(self.preview_frame)
        botoes_imagem_frame.grid(row=1, column=0, pady=5)
        
        ttk.Button(botoes_imagem_frame, text="Selecionar", command=self.selecionar_imagem, width=10).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(botoes_imagem_frame, text="Visualizar", command=self.visualizar_imagem, width=10).grid(row=0, column=1, padx=5)
        ttk.Button(botoes_imagem_frame, text="Remover", command=self.remover_imagem, width=10).grid(row=0, column=2, padx=5)
        
        imagem_frame.columnconfigure(0, weight=1)
        
        #quarta linha: artistas
        ttk.Label(cadastro_frame, text="Artistas:").grid(row=3, column=0, sticky=tk.NW, padx=(5, 0), pady=(10, 5))
        
        artistas_frame = ttk.Frame(cadastro_frame)
        artistas_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, padx=(70, 15), pady=5)
        
        entry_button_frame = ttk.Frame(artistas_frame)
        entry_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.artista_entry = ttk.Entry(entry_button_frame)
        self.artista_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.artista_entry.bind('<Return>', self.adicionar_artista)
        
        ttk.Button(entry_button_frame, text="Adicionar", command=self.adicionar_artista, width=12).pack(side=tk.RIGHT)
        
        listbox_frame = ttk.Frame(artistas_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.artistas_listbox = tk.Listbox(listbox_frame, height=3)
        self.artistas_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_artistas = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.artistas_listbox.yview)
        scrollbar_artistas.pack(side=tk.RIGHT, fill=tk.Y)
        self.artistas_listbox.configure(yscrollcommand=scrollbar_artistas.set)
        
        #botoes
        botoes_frame = ttk.Frame(cadastro_frame)
        botoes_frame.grid(row=3, column=3, sticky=tk.NE, padx=(5, 15), pady=(10, 5))
        
        self.botao_salvar = ttk.Button(botoes_frame, text="Salvar", command=self.salvar_obra, width=12)  # ← Adicionar self.
        self.botao_salvar.pack(pady=(0, 5))
        ttk.Button(botoes_frame, text="Cancelar", command=self.limpar_form, width=12).pack()
        
        #listagem de obras
        listagem_frame = ttk.LabelFrame(self.root, text="Listagem de obras", padding=10)
        listagem_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        #treeview
        colunas = ("ID", "Título", "Artista", "Tipo", "Ano", "Técnica", "Dimensões", "Localização", "Preço")
        
        self.tree = ttk.Treeview(listagem_frame, columns=colunas, show="headings", height=15)
        
        #config colunas
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50, stretch=False)
        
        self.tree.heading("Título", text="Título")
        self.tree.column("Título", width=150)
        
        self.tree.heading("Artista", text="Artista")
        self.tree.column("Artista", width=120)
        
        self.tree.heading("Tipo", text="Tipo")
        self.tree.column("Tipo", width=100)
        
        self.tree.heading("Ano", text="Ano")
        self.tree.column("Ano", width=60, stretch=False)
        
        self.tree.heading("Técnica", text="Técnica")
        self.tree.column("Técnica", width=100)
        
        self.tree.heading("Dimensões", text="Dimensões")
        self.tree.column("Dimensões", width=100)
        
        self.tree.heading("Localização", text="Localização")
        self.tree.column("Localização", width=120)
        
        self.tree.heading("Preço", text="Preço")
        self.tree.column("Preço", width=80)
        
        #scrollbars para treeview
        v_scrollbar = ttk.Scrollbar(listagem_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(listagem_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        #posicionar treeview e scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        #configurar expansao do frame de listagem
        listagem_frame.grid_rowconfigure(0, weight=1)
        listagem_frame.grid_columnconfigure(0, weight=1)
        
        #bind para duplo clique
        self.tree.bind("<Double-1>", self.editar_obra)
        
        self.carregar_obras()
    
    def selecionar_imagem(self):
        """abre diálogo para selecionar imagem"""
        try:
            filename = filedialog.askopenfilename(
                title="Selecionar Imagem",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
            )
            if filename:
                self.imagem_path = filename
                self.carregar_preview_imagem(filename)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar imagem: {str(e)}")
    
    def carregar_preview_imagem(self, caminho_imagem):
        """carrega e exibe preview da imagem"""
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
        """abre janela para visualizar a imagem em tamanho maior"""
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
        """remove a imagem selecionada"""
        if self.imagem_path:
            resposta = messagebox.askyesno("Confirmar", "Remover a imagem selecionada?")
            if resposta:
                self.imagem_path = None
                self.imagem_tk = None
                self.imagem_label.config(image="", text="Nenhuma imagem")
    
    def criar_tooltip(self, widget, texto):
        """cria tooltip para mostrar informações adicionais"""
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=texto, background="lightyellow", relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            tooltip.after(3000, tooltip.destroy)
        
        widget.bind("<Enter>", mostrar_tooltip)
    
    def atualizar_data(self):
        """atualiza o campo de data com a data atual"""
        data_atual = date.today().strftime("%d/%m/%Y")
        self.data_entry.config(state="normal")
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, data_atual)
        self.data_entry.config(state="readonly")
    
    def selecionar_imagem(self):
        """abre diálogo para selecionar imagem"""
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
    
    def adicionar_artista(self, event=None):
        """adiciona artista à lista"""
        artista = self.artista_entry.get().strip()
        if artista:
            artistas_atuais = []
            for i in range(self.artistas_listbox.size()):
                artistas_atuais.append(self.artistas_listbox.get(i))
                
            if artista not in artistas_atuais:
                self.artistas_listbox.insert(tk.END, artista)
                self.artista_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Aviso", "Artista já foi adicionado à lista")
    
    def obter_artistas(self):
        """retorna lista de artistas selecionados"""
        return [self.artistas_listbox.get(i) for i in range(self.artistas_listbox.size())]
    
    def salvar_obra(self):
        """salva a obra no banco de dados (criação ou edição)"""
        try:
            titulo = self.titulo_entry.get().strip()
            ano = self.ano_entry.get().strip()
            artistas = self.obter_artistas()
            tipo = self.tipo_combo.get()
            tecnica = self.tecnica_entry.get().strip()
            dimensoes = self.dimensoes_entry.get().strip()
            localizacao = self.localizacao_entry.get().strip()
            preco = self.preco_entry.get().strip()
            status_str = self.status_combo.get()
            
            if not artistas:
                messagebox.showerror("Erro", "Adicione pelo menos um artista")
                return
            
            status = next((s for s in StatusObra if s.value == status_str), StatusObra.DISPONIVEL)
            artista_str = ", ".join(artistas)
            
            if hasattr(self, 'obra_em_edicao') and self.obra_em_edicao:
                sucesso, mensagem = self.controller.atualizar_obra(
                    self.obra_em_edicao.id_obra, titulo, ano, artista_str, tipo, 
                    tecnica, dimensoes, localizacao, preco, status, self.imagem_path
                )
            else:
                sucesso, mensagem = self.controller.cadastrar_obra(
                    titulo, ano, artista_str, tipo, tecnica, dimensoes, 
                    localizacao, preco, status, self.imagem_path
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
        """limpa todos os campos do formulário"""
        self.titulo_entry.delete(0, tk.END)
        self.ano_entry.delete(0, tk.END)
        self.tipo_combo.set('')
        self.tecnica_entry.delete(0, tk.END)
        self.dimensoes_entry.delete(0, tk.END)
        self.localizacao_entry.delete(0, tk.END)
        self.preco_entry.delete(0, tk.END)
        self.preco_entry.insert(0, "0.00")
        self.status_combo.set("Disponível")
        self.artista_entry.delete(0, tk.END)
        
        self.artistas_listbox.delete(0, tk.END)
        
        self.imagem_path = None
        self.imagem_tk = None
        self.imagem_label.config(image="", text="Nenhuma imagem")
        
        self.atualizar_data()
        
        if hasattr(self, 'obra_em_edicao'):
            self.obra_em_edicao = None
        
        if hasattr(self, 'botao_salvar'):
            self.botao_salvar.config(text="Salvar")
    
    def carregar_obras(self):
        """carrega todas as obras na treeview"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            obras = self.controller.listar_obras()
            
            for obra in obras:
                self.tree.insert("", tk.END, values=(
                    obra.id_obra,
                    obra.titulo,
                    obra.artista,
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
        """duplo clique para editar obra"""
        try:
            item = self.tree.selection()[0]
            obra_id = self.tree.item(item, "values")[0]
            
            obra = self.controller.buscar_obra_por_id(obra_id)
            if not obra:
                messagebox.showerror("Erro", "Obra não encontrada")
                return
            
            if obra.status.value == "Vendida":
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
        """preenche o formulário com os dados da obra para edição"""
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
        
        if obra.data_cadastro:
            self.data_entry.config(state="normal")
            self.data_entry.delete(0, tk.END)
            self.data_entry.insert(0, obra.data_cadastro.strftime("%d/%m/%Y"))
            self.data_entry.config(state="readonly")
        
        if obra.artista:
            artistas = [artista.strip() for artista in obra.artista.split(',')]
            for artista in artistas:
                if artista: 
                    self.artistas_listbox.insert(tk.END, artista)
        
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

    def run(self):
        """iniciar a aplicação"""
        self.root.mainloop()