import sys
import os

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List

from src.controllers.relatorio_obra_controller import RelatorioController
from src.models.obra_model import StatusObra
class RelatorioObrasView(tk.Frame):
    def __init__(self, parent, manager=None):
        super().__init__(parent)
        self.parent = parent
        self.manager = manager
        self.controller = RelatorioController()
        
        parent.title("Relatório de Obras")
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()


    def create_widgets(self):
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

        self.results_tree.column("valor", stretch=True, width=100)
        for c in cols[:-1]:
            self.results_tree.column(c, stretch=True, width=120)
        self.results_tree.column("id", stretch=False, width=50)
        
        self.carregar_artistas()
        self.carregar_transacoes()

    def carregar_artistas(self):
        for i in self.artistas_tree.get_children():
            self.artistas_tree.delete(i)
        for a in self.controller.listar_artistas():
            aid = getattr(a, "id_artista", "")
            nome = getattr(a, "nome", "") or ""
            self.artistas_tree.insert("", "end", values=(aid, nome))

    def carregar_transacoes(self):
        for i in self.transacoes_tree.get_children(): self.transacoes_tree.delete(i)
        for t in self.controller.listar_transacoes():
            valor = getattr(t, "valor", 0.0)
            self.transacoes_tree.insert("", tk.END, values=(getattr(t, "tipo", ""), getattr(t, "cliente", ""), f"R$ {valor:.2f}"))

    def limpar_filtros(self):
        self.ano_entry.delete(0, "end")
        self.titulo_entry.delete(0, "end")
        self.tecnica_entry.delete(0, "end")
        self.tipo_combo.set("")
        self.status_combo.set("")
        self.localizacao_entry.delete(0, "end")
        self.valor_entry.delete(0, "end")
        self.data_cadastro_entry.delete(0, "end")
        for i in self.artistas_tree.selection():
            self.artistas_tree.selection_remove(i)
        for i in self.transacoes_tree.selection():
            self.transacoes_tree.selection_remove(i)
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)

    def gerar_relatorio(self):
        try:
            filtros = {}
            if self.ano_entry.get().strip():
                filtros["ano"] = self.ano_entry.get().strip()
            if self.titulo_entry.get().strip():
                filtros["titulo"] = self.titulo_entry.get().strip()
            if self.tecnica_entry.get().strip():
                filtros["tecnica"] = self.tecnica_entry.get().strip()
            if self.tipo_combo.get().strip():
                filtros["tipo"] = self.tipo_combo.get().strip()
            if self.status_combo.get().strip():
                filtros["status"] = self.status_combo.get().strip()
            if self.localizacao_entry.get().strip():
                filtros["localizacao"] = self.localizacao_entry.get().strip()
            if self.valor_entry.get().strip():
                filtros["valor"] = self.valor_entry.get().strip()
            if self.data_cadastro_entry.get().strip():
                filtros["data_cadastro"] = self.data_cadastro_entry.get().strip()

            sel_artistas = []
            for iid in self.artistas_tree.selection():
                vals = self.artistas_tree.item(iid, "values")
                if vals:
                    sel_artistas.append(str(vals[1]))
            if sel_artistas:
                filtros["artistas"] = sel_artistas

            sel_trans = []
            for iid in self.transacoes_tree.selection():
                vals = self.transacoes_tree.item(iid, "values")
                if vals:
                    sel_trans.append(str(vals[0]))
            if sel_trans:
                filtros["transacoes"] = sel_trans

            obras = self.controller.buscar_obras_validado(filtros)
            for i in self.results_tree.get_children():
                self.results_tree.delete(i)

            for obra in obras:
                artistas_text = getattr(obra, "artistas_str", None)
                if artistas_text is None or artistas_text == "":
                    a = getattr(obra, "artista", "")
                    if isinstance(a, (list, tuple)):
                        artistas_text = ", ".join(str(x) for x in a if x)
                    else:
                        artistas_text = str(a) if a else ""
                status_txt = getattr(obra.status, "value", "") if obra.status is not None else ""
                trans_txt = getattr(obra, "transacao", "") if hasattr(obra, "transacao") else ""
                valor = getattr(obra, "preco", 0.0) or 0.0

                self.results_tree.insert("", "end", values=(
                    obra.id_obra,
                    obra.titulo or "",
                    artistas_text,
                    obra.tipo or "",
                    getattr(obra, "ano", ""),
                    obra.tecnica or "",
                    status_txt,
                    trans_txt,
                    obra.localizacao or "",
                    f"R$ {float(valor):.2f}".replace(".", ",")
                ))
            
            # ✅ ADICIONA mensagem com total de obras encontradas
            total = len(obras)
            if total == 0:
                messagebox.showinfo("Relatório", "Nenhuma obra encontrada com os filtros aplicados.")
            else:
                messagebox.showinfo("Relatório", f"Relatório gerado com sucesso!\n{total} obra(s) encontrada(s).")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório: {e}")

# execução independente para teste
if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    w = RelatorioObrasView(root)
    root.mainloop()