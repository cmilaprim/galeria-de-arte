# src/views/exposicao_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.exposicao_controller import ExposicaoController
from src.controllers.obra_controller import ObraController

class ExposicaoView:
    def __init__(self, root, controller=None, manager=None):
        self.root = root
        self.controller = controller or ExposicaoController()
        self.obra_controller = ObraController()
        self.manager = manager

        for w in self.root.winfo_children():
            w.destroy()
        self.root.title("Exposições")
        self.root.geometry("1000x700")
        bg = "#f3f3f3"
        self.root.configure(bg=bg)

        frm_top = ttk.LabelFrame(self.root, text="Cadastro de Exposição", padding=10)
        frm_top.pack(fill="x", padx=10, pady=8)
        for c in range(4):
            frm_top.columnconfigure(c, weight=1)

        ttk.Label(frm_top, text="Nome:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.entry_nome = ttk.Entry(frm_top)
        self.entry_nome.grid(row=0, column=0, sticky="ew", padx=(72,10), pady=4)

        ttk.Label(frm_top, text="Tema:").grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self.entry_tema = ttk.Entry(frm_top)
        self.entry_tema.grid(row=0, column=1, sticky="ew", padx=(40,10), pady=4)

        ttk.Label(frm_top, text="Localização:").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.entry_local = ttk.Entry(frm_top)
        self.entry_local.grid(row=0, column=2, sticky="ew", padx=(80,10), pady=4)

        ttk.Label(frm_top, text="Status:").grid(row=0, column=3, sticky="w", padx=6, pady=4)
        self.combo_status = ttk.Combobox(frm_top, values=self.controller.get_status(), state="readonly")
        self.combo_status.grid(row=0, column=3, sticky="ew", padx=(44,6), pady=4)

        ttk.Label(frm_top, text="Data Início:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.entry_data_inicio = ttk.Entry(frm_top)
        self.entry_data_inicio.grid(row=1, column=0, sticky="ew", padx=(90,10), pady=4)

        ttk.Label(frm_top, text="Data Fim:").grid(row=1, column=1, sticky="w", padx=6, pady=4)
        self.entry_data_fim = ttk.Entry(frm_top)
        self.entry_data_fim.grid(row=1, column=1, sticky="ew", padx=(60,10), pady=4)

        ttk.Label(frm_top, text="Data Cadastro:").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self.entry_data_cadastro = ttk.Entry(frm_top)
        self.entry_data_cadastro.grid(row=1, column=2, sticky="ew", padx=(40,10), pady=4)

        ttk.Label(frm_top, text="Descrição:").grid(row=2, column=0, sticky="nw", padx=6, pady=4)
        self.text_descricao = tk.Text(frm_top, height=5)
        self.text_descricao.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=(92,10), pady=4)

        btn_frame = ttk.Frame(frm_top)
        btn_frame.grid(row=0, column=3, rowspan=3, sticky="n", padx=8)
        ttk.Button(btn_frame, text="Salvar", command=self._salvar, width=18).pack(pady=6)
        ttk.Button(btn_frame, text="Cancelar", command=self._limpar, width=18).pack(pady=6)
        ttk.Button(btn_frame, text="Buscar", command=self._buscar, width=18).pack(pady=6)

        frm_list = ttk.LabelFrame(self.root, text="Listagem de Exposições", padding=8)
        frm_list.pack(fill="both", expand=True, padx=10, pady=(0,10))

        cols = ("id", "nome", "tema", "local", "status", "data_inicio", "data_fim", "data_cadastro")
        self.tree = ttk.Treeview(frm_list, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, anchor="center", width=110)
        self.tree.column("nome", width=250)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frm_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        btns_bottom = ttk.Frame(self.root)
        btns_bottom.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(btns_bottom, text="Adicionar obra", command=self._abrir_popup_adicionar_obra).pack(side="right")

        self._id_atual = None
        self._carregar_lista()

        self.tree.bind("<Double-1>", self._on_duplo)

    def _buscar(self):
        filtros = {}
        nome = self.entry_nome.get().strip()
        tema = self.entry_tema.get().strip()
        local = self.entry_local.get().strip()
        status = self.combo_status.get().strip()
        data_inicio = self.entry_data_inicio.get().strip()
        data_fim = self.entry_data_fim.get().strip()
        data_cadastro = self.entry_data_cadastro.get().strip()
        descricao = self.text_descricao.get("1.0", tk.END).strip()

        if nome:
            filtros["nome"] = nome
        if tema:
            filtros["tema"] = tema
        if local:
            filtros["localizacao"] = local
        if status:
            filtros["status"] = status
        if data_inicio:
            filtros["data_inicio"] = data_inicio
        if data_fim:
            filtros["data_fim"] = data_fim
        if data_cadastro:
            filtros["data_cadastro"] = data_cadastro
        if descricao:
            filtros["descricao"] = descricao

        try:
            if not filtros:
                # sem filtros: recarrega tudo
                self._carregar_lista()
                return

            resultados = self.controller.buscar(filtros)
            # limpar tree
            for i in self.tree.get_children():
                self.tree.delete(i)

            # pode receber objetos Exposicao ou rows/dicts; trato ambos
            for e in resultados:
                try:
                    id_ex = e.id_exposicao
                    nome = e.nome
                    tema = e.tema
                    local = e.localizacao
                    status = e.status.value
                    di = e.data_inicio or ""
                    df = e.data_fim or ""
                    dc = e.data_cadastro or ""
                except Exception:
                    id_ex = e.get("id_exposicao") if isinstance(e, dict) else e["id_exposicao"]
                    nome = e.get("nome") if isinstance(e, dict) else e["nome"]
                    tema = e.get("tema") if isinstance(e, dict) else e["tema"]
                    local = e.get("localizacao") if isinstance(e, dict) else e["localizacao"]
                    status = e.get("status") if isinstance(e, dict) else e["status"]
                    di = e.get("data_inicio") if isinstance(e, dict) else e["data_inicio"]
                    df = e.get("data_fim") if isinstance(e, dict) else e["data_fim"]
                    dc = e.get("data_cadastro") if isinstance(e, dict) else e["data_cadastro"]

                self.tree.insert("", "end", values=(id_ex, nome, tema, local, status, di, df, dc))

        except Exception as ex:
            messagebox.showerror("Erro", f"Erro na busca: {ex}")


    def _carregar_lista(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        expos = self.controller.listar()
        for e in expos:
            try:
                id_ex = e.id_exposicao
                nome = e.nome
                tema = e.tema
                local = e.localizacao
                status = e.status.value
                di = e.data_inicio or ""
                df = e.data_fim or ""
                dc = e.data_cadastro or ""
            except Exception:
                id_ex = e.get("id_exposicao") if isinstance(e, dict) else e["id_exposicao"]
                nome = e.get("nome") if isinstance(e, dict) else e["nome"]
                tema = e.get("tema") if isinstance(e, dict) else e["tema"]
                local = e.get("localizacao") if isinstance(e, dict) else e["localizacao"]
                status = e.get("status") if isinstance(e, dict) else e["status"]
                di = e.get("data_inicio") if isinstance(e, dict) else e["data_inicio"]
                df = e.get("data_fim") if isinstance(e, dict) else e["data_fim"]
                dc = e.get("data_cadastro") if isinstance(e, dict) else e["data_cadastro"]
            self.tree.insert("", "end", values=(id_ex, nome, tema, local, status, di, df, dc))

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        tema = self.entry_tema.get().strip()
        local = self.entry_local.get().strip()
        status = self.combo_status.get().strip()
        data_inicio = self.entry_data_inicio.get().strip()
        data_fim = self.entry_data_fim.get().strip()
        data_cad = self.entry_data_cadastro.get().strip()
        desc = self.text_descricao.get("1.0", tk.END).strip()

        ok, msg = self.controller.salvar(self._id_atual, nome, tema, local, status, data_inicio, data_fim, data_cad, desc)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self._limpar()
            self._carregar_lista()
        else:
            messagebox.showerror("Erro", msg)

    def _limpar(self):
        self._id_atual = None
        self.entry_nome.delete(0, tk.END)
        self.entry_tema.delete(0, tk.END)
        self.entry_local.delete(0, tk.END)
        self.combo_status.set("")
        self.entry_data_inicio.delete(0, tk.END)
        self.entry_data_fim.delete(0, tk.END)
        self.entry_data_cadastro.delete(0, tk.END)
        self.text_descricao.delete("1.0", tk.END)

    def _on_duplo(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel)["values"]
        if not vals: return
        id_ex = vals[0]
        expos = self.controller.carregar(id_ex)
        if not expos:
            messagebox.showerror("Erro", "Não foi possível carregar exposição.")
            return
        try:
            e = expos
            self._id_atual = e.id_exposicao
            self.entry_nome.delete(0, tk.END); self.entry_nome.insert(0, e.nome)
            self.entry_tema.delete(0, tk.END); self.entry_tema.insert(0, e.tema)
            self.entry_local.delete(0, tk.END); self.entry_local.insert(0, e.localizacao)
            self.combo_status.set(e.status.value)
            self.entry_data_inicio.delete(0, tk.END); self.entry_data_inicio.insert(0, e.data_inicio or "")
            self.entry_data_fim.delete(0, tk.END); self.entry_data_fim.insert(0, e.data_fim or "")
            self.entry_data_cadastro.delete(0, tk.END); self.entry_data_cadastro.insert(0, e.data_cadastro or "")
            self.text_descricao.delete("1.0", tk.END); self.text_descricao.insert("1.0", e.descricao or "")
        except Exception:
            e = expos
            self._id_atual = e["id_exposicao"]
            self.entry_nome.delete(0, tk.END); self.entry_nome.insert(0, e["nome"])
            self.entry_tema.delete(0, tk.END); self.entry_tema.insert(0, e["tema"])
            self.entry_local.delete(0, tk.END); self.entry_local.insert(0, e["localizacao"])
            self.combo_status.set(e["status"])
            self.entry_data_inicio.delete(0, tk.END); self.entry_data_inicio.insert(0, e.get("data_inicio", "") or "")
            self.entry_data_fim.delete(0, tk.END); self.entry_data_fim.insert(0, e.get("data_fim", "") or "")
            self.entry_data_cadastro.delete(0, tk.END); self.entry_data_cadastro.insert(0, e.get("data_cadastro", "") or "")
            self.text_descricao.delete("1.0", tk.END); self.text_descricao.insert("1.0", e.get("descricao", "") or "")

    def _abrir_popup_adicionar_obra(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma exposição para adicionar obras.")
            return
        id_exposicao = self.tree.item(sel)["values"][0]
        popup = ObrasExposicaoPopup(self.root, id_exposicao, self.controller, self.obra_controller)
        popup.show()
        self._carregar_lista()


class ObrasExposicaoPopup:
    def __init__(self, parent, id_exposicao, exposicao_controller: ExposicaoController, obra_controller: ObraController):
        self.parent = parent
        self.id_exposicao = id_exposicao
        self.exposicao_controller = exposicao_controller
        self.obra_controller = obra_controller

        self.win = tk.Toplevel(self.parent)
        self.win.title("Gerenciar obras da exposição")
        self.win.geometry("900x520")
        self.win.transient(self.parent)
        self.win.grab_set()

        frame = ttk.Frame(self.win, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Obras:").pack(anchor="w", pady=(2,6))
        cols = ("id", "artista", "titulo")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, anchor="center")
        self.tree.column("titulo", width=420)
        self.tree.pack(fill="both", expand=True)

        bottom = ttk.Frame(self.win, padding=12)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Cancelar", command=self.win.destroy, width=18).pack(side="left", padx=8)
        ttk.Button(bottom, text="Remover", command=self._remover, width=18).pack(side="right", padx=8)
        ttk.Button(bottom, text="Adicionar", command=self._adicionar, width=18).pack(side="right", padx=8)

        self._carregar_obras()

    def show(self):
        self.win.deiconify()
        self.win.wait_window()

    def _carregar_obras(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            obras = self.obra_controller.listar_obras()
            participacoes = self.exposicao_controller.listar_obras(self.id_exposicao)
            participacao_ids = set()
            try:
                for p in participacoes:
                    pid = getattr(p, "id_obra", None) or (p.get("id_obra") if isinstance(p, dict) else p["id_obra"])
                    participacao_ids.add(int(pid))
            except Exception:
                pass

            for o in obras:
                try:
                    oid = o.id_obra
                    artista = getattr(o.artista, "nome", str(o.artista) if hasattr(o, "artista") else "")
                    titulo = o.titulo
                except Exception:
                    oid = o.get("id_obra") if isinstance(o, dict) else o["id_obra"]
                    artista = o.get("nome_artista") if isinstance(o, dict) else o.get("artista", "")
                    titulo = o.get("titulo") if isinstance(o, dict) else o["titulo"]
                tag = ""
                if int(oid) in participacao_ids:
                    tag = " (✓)"
                self.tree.insert("", "end", values=(oid, artista, f"{titulo}{tag}"))

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar obras: {e}")

    def _adicionar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma obra para adicionar.")
            return
        id_obra = int(self.tree.item(sel)["values"][0])
        ok, msg = self.exposicao_controller.adicionar_obra(self.id_exposicao, id_obra)
        if ok:
            messagebox.showinfo("Sucesso", msg or "Obra adicionada.")
            self._carregar_obras()
        else:
            messagebox.showerror("Erro", msg or "Não foi possível adicionar obra.")

    def _remover(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma obra para remover.")
            return
        id_obra = int(self.tree.item(sel)["values"][0])
        ok, msg = self.exposicao_controller.remover_obra(self.id_exposicao, id_obra)
        if ok:
            messagebox.showinfo("Sucesso", msg or "Obra removida.")
            self._carregar_obras()
        else:
            messagebox.showerror("Erro", msg or "Não foi possível remover obra.")
