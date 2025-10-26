import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List

from src.controllers.relatorio_obra_controller import RelatorioController
from src.models.obra_model import StatusObra
class RelatorioObrasView(tk.Toplevel):
    def __init__(self, parent, manager=None):
        super().__init__(parent)
        self.manager = manager
        self.title("Relatório de Obras")
        self.geometry("1100x700")
        self.resizable(True, True)

        self.controller = RelatorioController()
        self._create_widgets()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width(); h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _create_widgets(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        filtros_frame = ttk.LabelFrame(main, text="Filtros", padding=8)
        filtros_frame.pack(fill=tk.X, padx=5, pady=5)

        row1 = ttk.Frame(filtros_frame)
        row1.pack(fill=tk.X, pady=4)
        ttk.Label(row1, text="Ano:").pack(side=tk.LEFT, padx=4)
        self.ano_entry = ttk.Entry(row1, width=10); self.ano_entry.pack(side=tk.LEFT, padx=4)
        ttk.Label(row1, text="Título:").pack(side=tk.LEFT, padx=4)
        self.titulo_entry = ttk.Entry(row1, width=30); self.titulo_entry.pack(side=tk.LEFT, padx=4)
        ttk.Label(row1, text="Técnica:").pack(side=tk.LEFT, padx=4)
        self.tecnica_entry = ttk.Entry(row1, width=25); self.tecnica_entry.pack(side=tk.LEFT, padx=4)
        ttk.Label(row1, text="Tipo:").pack(side=tk.LEFT, padx=4)
        self.tipo_combo = ttk.Combobox(row1, values=[""] + self.controller.obra_ctrl.get_tipos_obra(), width=15)
        self.tipo_combo.pack(side=tk.LEFT, padx=4)

        row2 = ttk.Frame(filtros_frame)
        row2.pack(fill=tk.X, pady=4)
        ttk.Label(row2, text="Status:").pack(side=tk.LEFT, padx=4)
        status_values = [""] + [s.value for s in StatusObra]
        self.status_combo = ttk.Combobox(row2, values=status_values, width=18)
        self.status_combo.pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="Localização:").pack(side=tk.LEFT, padx=4)
        self.localizacao_entry = ttk.Entry(row2, width=30); self.localizacao_entry.pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="Valor:").pack(side=tk.LEFT, padx=4)
        self.valor_entry = ttk.Entry(row2, width=12); self.valor_entry.pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="Data cadastro (DD/MM/AAAA):").pack(side=tk.LEFT, padx=4)
        self.data_cadastro_entry = ttk.Entry(row2, width=15); self.data_cadastro_entry.pack(side=tk.LEFT, padx=4)

        # Linha artistas / transacoes (somente listagens para seleção)
        row3 = ttk.Frame(filtros_frame)
        row3.pack(fill=tk.X, pady=6)
        artistas_frame = ttk.LabelFrame(row3, text="Artistas")
        artistas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))
        transacoes_frame = ttk.LabelFrame(row3, text="Transações")
        transacoes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.artistas_tree = ttk.Treeview(artistas_frame, columns=("id", "nome"), show="headings", height=5)
        self.artistas_tree.heading("id", text="id"); self.artistas_tree.heading("nome", text="nome")
        self.artistas_tree.column("id", width=50); self.artistas_tree.pack(fill=tk.BOTH, expand=True)
        self.transacoes_tree = ttk.Treeview(transacoes_frame, columns=("tipo", "cliente", "valor"), show="headings", height=5)
        for col, txt, w in (("tipo","tipo",100), ("cliente","cliente",200), ("valor","valor",100)):
            self.transacoes_tree.heading(col, text=txt); self.transacoes_tree.column(col, width=w)
        self.transacoes_tree.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(filtros_frame)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Gerar", command=self.gerar_relatorio).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btns, text="Limpar", command=self.limpar_filtros).pack(side=tk.RIGHT)

        # Resultados
        results_frame = ttk.LabelFrame(main, text="Listagem de Obras", padding=6)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        cols = ("id","titulo","artista","tipo","ano","tecnica","status","transacao","localizacao","valor")
        self.results_tree = ttk.Treeview(results_frame, columns=cols, show="headings")
        headings = ["ID","Título","Artista","Tipo","Ano","Técnica","Status","Transação","Localização","Valor"]
        for c,h in zip(cols, headings):
            self.results_tree.heading(c, text=h)
        self.results_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.carregar_artistas()
        self.carregar_transacoes()

    def carregar_artistas(self):
        for i in self.artistas_tree.get_children(): self.artistas_tree.delete(i)
        for a in self.controller.listar_artistas():
            self.artistas_tree.insert("", tk.END, values=(getattr(a, "id_artista", None), getattr(a, "nome", "")))

    def carregar_transacoes(self):
        for i in self.transacoes_tree.get_children(): self.transacoes_tree.delete(i)
        for t in self.controller.listar_transacoes():
            valor = getattr(t, "valor", 0.0)
            self.transacoes_tree.insert("", tk.END, values=(getattr(t, "tipo", ""), getattr(t, "cliente", ""), f"R$ {valor:.2f}"))

    def limpar_filtros(self):
        for e in (self.ano_entry, self.titulo_entry, self.tecnica_entry, self.localizacao_entry, self.valor_entry, self.data_cadastro_entry):
            e.delete(0, tk.END)
        self.tipo_combo.set("")
        self.status_combo.set("")
        for i in self.results_tree.get_children(): self.results_tree.delete(i)
        # limpar seleções
        try:
            self.artistas_tree.selection_remove(self.artistas_tree.selection())
            self.transacoes_tree.selection_remove(self.transacoes_tree.selection())
        except Exception:
            pass

    def gerar_relatorio(self):
        filtros_brutos = {
            "ano": self.ano_entry.get().strip(),
            "titulo": self.titulo_entry.get().strip(),
            "tecnica": self.tecnica_entry.get().strip(),
            "tipo": self.tipo_combo.get().strip(),
            "status": self.status_combo.get().strip(),
            "localizacao": self.localizacao_entry.get().strip(),
            "valor": self.valor_entry.get().strip(),
            "data_cadastro": self.data_cadastro_entry.get().strip()
        }
        
        filtros_brutos = {k: v for k, v in filtros_brutos.items() if v}
        
        artistas_sel = []
        for iid in self.artistas_tree.selection():
            v = self.artistas_tree.item(iid, "values")
            if v and len(v) >= 2:
                artistas_sel.append(v[1])
        if artistas_sel:
            filtros_brutos["artistas"] = artistas_sel
            
        transacoes_sel = []
        for iid in self.transacoes_tree.selection():
            v = self.transacoes_tree.item(iid, "values")
            if v and len(v) >= 2:
                transacoes_sel.append(v[1]) 
        if transacoes_sel:
            filtros_brutos["transacoes"] = transacoes_sel
                
        try:
            obras = self.controller.buscar_obras_validado(filtros_brutos)
            
            for i in self.results_tree.get_children(): 
                self.results_tree.delete(i)
                
            for o in obras:
                preco = f"R$ {float(getattr(o, 'preco', 0) or 0):.2f}" if getattr(o, "preco", None) is not None else ""
                
                transacoes_relacionadas = []
                for t in self.controller.listar_transacoes():
                    if str(o.id_obra) in t.obras:
                        transacoes_relacionadas.append(t.cliente)
                
                if transacoes_relacionadas:
                    transacao_txt = ", ".join(transacoes_relacionadas)
                else:
                    transacao_txt = "Sem transação"
                status_txt = getattr(o.status, "value", "") if o.status is not None else ""
                
                self.results_tree.insert("", tk.END, values=(
                    getattr(o, "id_obra", None),
                    getattr(o, "titulo", ""),
                    getattr(o, "artista", ""),
                    getattr(o, "tipo", ""),
                    getattr(o, "ano", ""),
                    getattr(o, "tecnica", ""),
                    status_txt,
                    transacao_txt,
                    getattr(o, "localizacao", ""),
                    preco
                ))
                
            messagebox.showinfo("Relatório", f"{len(obras)} obras encontradas.")
            
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e))

# execução independente para teste
#if __name__ == "__main__":
#    root = tk.Tk(); root.withdraw()
#    w = RelatorioObrasView(root)
#    root.mainloop()