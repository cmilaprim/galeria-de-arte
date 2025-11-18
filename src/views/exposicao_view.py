import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional
from src.controllers.exposicao_controller import ExposicaoController
from src.controllers.obra_controller import ObraController

class ExposicaoView:
    def __init__(self, root, controller=None, manager=None):
        self.root = root
        self.controller = controller or ExposicaoController()
        self.obra_controller = ObraController()
        self.manager = manager

        # limpa widgets existentes
        for w in self.root.winfo_children(): w.destroy()
        # configurações básicas da janela
        self.root.title("Exposições"); self.root.geometry("800x600"); self.root.minsize(800,600)
        bg = "#F3F4F6"; self.root.configure(bg=bg)
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("TFrame", background=bg); style.configure("TLabel", background=bg)
        style.configure("TLabelframe", background=bg); style.configure("TLabelframe.Label", background=bg)

        # Top frame (formulário de cadastro/edição)
        frm_top = ttk.LabelFrame(self.root, text="Cadastro de Exposição", padding=10); frm_top.pack(fill="x", padx=10, pady=8)
        for c in range(9):
            frm_top.columnconfigure(c, weight=(1 if c < 8 else 0), uniform="col", minsize=(0 if c < 8 else 180))

        # linha 0: campos Nome, Tema, Localização, Status
        campos_linha0 = [("Nome:","entry_nome"),("Tema:","entry_tema"),("Localização:","entry_local"),("Status:","entry_status")]
        for idx, (lbl, attr) in enumerate(campos_linha0):
            ttk.Label(frm_top, text=lbl).grid(row=0, column=idx*2, sticky="w", padx=(10,5), pady=4)
            # status é readonly e preenchida automaticamente
            ent = ttk.Entry(frm_top, state="readonly") if attr=="entry_status" else ttk.Entry(frm_top)
            ent.grid(row=0, column=idx*2+1, sticky="ew", padx=(5,10), pady=4); setattr(self, attr, ent)

        # linha 1: datas (início, fim e data de cadastro)
        campos_linha1 = [("Data Início:","entry_data_inicio"),("Data Fim:","entry_data_fim"),("Data Cadastro:","entry_data_cadastro")]
        for idx, (lbl, attr) in enumerate(campos_linha1):
            ttk.Label(frm_top, text=lbl).grid(row=1, column=idx*2, sticky="w", padx=(10,5), pady=4)
            # data_cadastro é readonly e preenchida automaticamente
            ent = ttk.Entry(frm_top, state="readonly") if attr=="entry_data_cadastro" else ttk.Entry(frm_top)
            ent.grid(row=1, column=idx*2+1, sticky="ew", padx=(5,10), pady=4); setattr(self, attr, ent)

        # preenche data de cadastro com data atual
        try:
            self.entry_data_cadastro.config(state="normal"); self.entry_data_cadastro.delete(0, tk.END)
            self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y")); self.entry_data_cadastro.config(state="readonly")
        except Exception:
            pass

        # campo de descrição
        ttk.Label(frm_top, text="Descrição:").grid(row=2, column=0, sticky="nw", padx=(10,5), pady=4)
        self.text_descricao = tk.Text(frm_top, height=5, relief="solid", borderwidth=1, bg="white")
        self.text_descricao.grid(row=2, column=1, columnspan=7, sticky="nsew", padx=(5,10), pady=4); frm_top.rowconfigure(2, weight=1)

        # botão "home" (voltar)
        frame_home = tk.Frame(frm_top, bg="#f0f0f0"); frame_home.place(relx=1, rely=0, x=15, y=-35, anchor="ne")
        self.btn_home = tk.Button(frame_home, text="❌", font=("Segoe UI Emoji",10), bd=0, highlightthickness=0,
                                  padx=0, pady=0, bg="#f0f0f0", activebackground="#dddddd", cursor="hand2",
                                  command=self.voltar_inicio)
        self.btn_home.pack(expand=True, fill="both")

        # --- Botões Salvar / Cancelar / Buscar --- #
        btn_frame = ttk.Frame(frm_top); btn_frame.grid(row=0, column=8, rowspan=3, sticky="n", padx=8, pady=4)
        ttk.Button(btn_frame, text="Salvar", command=self._salvar, width=18).pack(pady=6)
        ttk.Button(btn_frame, text="Cancelar", command=self._limpar, width=18).pack(pady=6)
        ttk.Button(btn_frame, text="Buscar", command=self._buscar, width=18).pack(pady=6)

        # Listagem de exposições (Treeview)
        frm_list = ttk.LabelFrame(self.root, text="Listagem de Exposições", padding=8); frm_list.pack(fill="both", expand=True, padx=10, pady=(0,10))
        frm_list.columnconfigure(0, weight=1); frm_list.rowconfigure(0, weight=1)
        cols = ("id","nome","tema","local","status","data_inicio","data_fim","data_cadastro")
        self.tree = ttk.Treeview(frm_list, columns=cols, show="headings")
        widths = {"id":60,"nome":250,"tema":140,"local":140,"status":100,"data_inicio":90,"data_fim":90,"data_cadastro":110}
        for c in cols:
            self.tree.heading(c, text=c.replace("_"," ").title()); self.tree.column(c, width=widths.get(c,100), anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(frm_list, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=yscroll.set); yscroll.grid(row=0, column=1, sticky="ns")

        # botão gerenciar obra
        btns_bottom = ttk.Frame(self.root); btns_bottom.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(btns_bottom, text="Adicionar obras", command=self._abrir_popup_adicionar_obra, width=20).pack(side="right")

        self._id_atual = None; self._prev_status = None; self._prev_start = None; self._prev_end = None
        self._carregar_lista(); self.tree.bind("<Double-1>", self._on_duplo)

    # ---------------- helpers ----------------
    def _parse_data(self, s: str) -> Optional[date]:
        # tenta parsear string para date com formatos comuns; retorna None se inválido
        if not s: return None
        for fmt in ("%d/%m/%Y","%Y-%m-%d"):
            try: return datetime.strptime(s, fmt).date()
            except Exception: continue
        return None

    def _compute_status_from_dates(self, inicio_s: str, fim_s: str) -> str:
        # determina status automático ("Planejada","Em Curso","Finalizada") a partir das datas
        inicio = self._parse_data(inicio_s); fim = self._parse_data(fim_s); hoje = date.today()
        if inicio and fim:
            if hoje < inicio: return "Planejada"
            if inicio <= hoje <= fim: return "Em Curso"
            return "Finalizada"
        if inicio and not fim: return "Planejada" if hoje < inicio else "Em Curso"
        if not inicio and fim: return "Em Curso" if hoje <= fim else "Finalizada"
        return ""

    def _set_obra_status(self, id_obra: int, novo_status: str) -> bool:
        # atualiza status da obra utilizando controller
        if id_obra is None: return False
        try:
            if hasattr(self.obra_controller, "atualizar_status"):
                res = self.obra_controller.atualizar_status(id_obra, novo_status)
                return bool(res[0]) if isinstance(res, tuple) else bool(res)
            for name in ("set_status","update_status","atualizar","atualizar_obra","atualizarStatus"):
                if hasattr(self.obra_controller, name):
                    fn = getattr(self.obra_controller, name)
                    res = fn(id_obra, novo_status); return bool(res[0]) if isinstance(res, tuple) else bool(res)
        except Exception:
            pass
        # tenta métodos do controller da exposição que atualizem status por obra
        try:
            for name in ("atualizar_status_obra","set_status_obra","atualizarObraStatus"):
                if hasattr(self.controller, name):
                    fn = getattr(self.controller, name)
                    res = fn(self._id_atual, id_obra, novo_status); return bool(res[0]) if isinstance(res, tuple) else bool(res)
        except Exception:
            pass
        return False

    def _get_status_da_obra(self, id_obra: int) -> str:
        # tenta obter status da obra consultando controllers/listas
        try:
            if hasattr(self.obra_controller, "carregar"):
                o = self.obra_controller.carregar(id_obra)
                if o is not None:
                    status_raw = getattr(o,"status",None) or (o.get("status") if isinstance(o, dict) else None)
                    return self._normalizar_status(status_raw)
        except Exception: pass
        try:
            all_obs = self.obra_controller.listar_obras() if hasattr(self.obra_controller,"listar_obras") else (self.obra_controller.listar() if hasattr(self.obra_controller,"listar") else None)
            if all_obs:
                for ob in all_obs:
                    try:
                        oid = getattr(ob,"id_obra",None) or (ob.get("id_obra") if isinstance(ob, dict) else ob[0])
                        if int(oid) == int(id_obra):
                            status_raw = getattr(ob,"status",None) or (ob.get("status") if isinstance(ob, dict) else None)
                            return self._normalizar_status(status_raw)
                    except Exception: continue
        except Exception: pass
        return ""

    def _normalizar_status(self, status_raw) -> str:
        # normaliza diferentes tipos de retorno (enum, objeto, str, None) para string
        if status_raw is None: return ""
        try:
            if hasattr(status_raw, "value") and isinstance(status_raw.value, str):
                s = status_raw.value.strip();
                if s: return s
        except Exception: pass
        try:
            s = str(status_raw).strip(); return s if s else ""
        except Exception: return str(status_raw)

    def _obra_ocupada_em_periodo(self, id_obra:int, inicio:Optional[date], fim:Optional[date], exclude_expo_id:Optional[int]=None) -> bool:
        # verifica se a obra está ocupada (participando de outra exposição) no período
        try:
            # primeiro tenta método do controller que retorna exposições por obra
            if hasattr(self.controller, "exposicoes_por_obra"):
                expos = self.controller.exposicoes_por_obra(id_obra) or []
                for ex in expos:
                    try:
                        ex_id = getattr(ex,"id_exposicao",None) or (ex.get("id_exposicao") if isinstance(ex,dict) else ex["id_exposicao"])
                        if exclude_expo_id and int(ex_id)==int(exclude_expo_id): continue
                        s_raw = getattr(ex,"data_inicio",None) or (ex.get("data_inicio") if isinstance(ex,dict) else None)
                        e_raw = getattr(ex,"data_fim",None) or (ex.get("data_fim") if isinstance(ex,dict) else None)
                        s = self._parse_data(str(s_raw)) if s_raw else None
                        e = self._parse_data(str(e_raw)) if e_raw else None
                        if s and e and inicio and fim:
                            if not (e < inicio or s > fim): return True
                        else:
                            # se qualquer data estiver incompleta, considera ocupado por garantia
                            return True
                    except Exception: continue
            expos_all = self.controller.listar() or []
            for ex in expos_all:
                try:
                    ex_id = getattr(ex,"id_exposicao",None) or (ex.get("id_exposicao") if isinstance(ex,dict) else ex["id_exposicao"])
                    if exclude_expo_id and int(ex_id)==int(exclude_expo_id): continue
                    s = self._parse_data(getattr(ex,"data_inicio",None) or (ex.get("data_inicio") if isinstance(ex,dict) else None))
                    e = self._parse_data(getattr(ex,"data_fim",None) or (ex.get("data_fim") if isinstance(ex,dict) else None))
                    obras = self.controller.listar_obras(ex_id) or []
                    ids = { (getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"])) for p in obras }
                    if int(id_obra) not in {int(x) for x in ids}: continue
                    if s and e and inicio and fim:
                        if not (e < inicio or s > fim): return True
                    else:
                        # dados incompletos: assume ocupado
                        return True
                except Exception: continue
        except Exception:
            # se não conseguimos calcular por controller, tenta verificar pelo status da obra
            try:
                o = self.obra_controller.carregar(id_obra) if hasattr(self.obra_controller,"carregar") else None
                status_raw = getattr(o,"status",None) or (o.get("status") if isinstance(o, dict) else "")
                s = str(status_raw).strip().upper()
                if "DISPONIVEL" in s or "DISPONÍVEL" in s: return False
                return True
            except Exception:
                return False
        return False

    def _obra_em_qualquer_exposicao_ativa_hoje(self, id_obra:int, exclude_expo_id:Optional[int]=None) -> bool:
        # verifica ocupação da obra no dia de hoje
        hoje = date.today(); return self._obra_ocupada_em_periodo(id_obra, hoje, hoje, exclude_expo_id=exclude_expo_id)

    def _obra_efetivamente_disponivel(self, id_obra:int, periodo_inicio:Optional[date], periodo_fim:Optional[date], exclude_expo_id:Optional[int]=None) -> bool:
        # checa se a obra está realmente disponível no período considerando status no DB e exposições
        status_db = self._get_status_da_obra(id_obra).strip().lower() if self._get_status_da_obra(id_obra) else ""
        if not status_db:
            ocupado = self._obra_ocupada_em_periodo(id_obra, periodo_inicio, periodo_fim, exclude_expo_id=exclude_expo_id)
            return not ocupado
        if "dispon" in status_db:
            return True
        if "em expos" in status_db or "em_expos" in status_db or "emexposicao" in status_db:
            ocupado = self._obra_ocupada_em_periodo(id_obra, periodo_inicio, periodo_fim, exclude_expo_id=exclude_expo_id)
            return not ocupado
        return False

    def _buscar(self):
        # constrói filtros a partir dos campos do formulário e delega para controller.buscar
        filtros = {}
        def put(k,val):
            if val: filtros[k]=val
        put("nome", self.entry_nome.get().strip()); put("tema", self.entry_tema.get().strip()); put("localizacao", self.entry_local.get().strip())
        put("status", self.entry_status.get().strip()); put("data_inicio", self.entry_data_inicio.get().strip()); put("data_fim", self.entry_data_fim.get().strip())
        put("data_cadastro", self.entry_data_cadastro.get().strip()); put("descricao", self.text_descricao.get("1.0", tk.END).strip())
        try:
            if not filtros: self._carregar_lista(); return
            resultados = self.controller.buscar(filtros)
            # limpa tree e popula com resultados
            for i in self.tree.get_children(): self.tree.delete(i)
            for e in resultados:
                try:
                    id_ex = e.id_exposicao; nome = e.nome; tema = e.tema; local = e.localizacao; di = e.data_inicio or ""; df = e.data_fim or ""; dc = e.data_cadastro or ""
                    status_auto = self._compute_status_from_dates(str(di), str(df)) or (e.status.value if hasattr(e,"status") else (getattr(e,"status","") or ""))
                except Exception:
                    id_ex = e.get("id_exposicao") if isinstance(e,dict) else e["id_exposicao"]
                    nome = e.get("nome") if isinstance(e,dict) else e["nome"]
                    tema = e.get("tema") if isinstance(e,dict) else e["tema"]
                    local = e.get("localizacao") if isinstance(e,dict) else e["localizacao"]
                    di = e.get("data_inicio") if isinstance(e,dict) else e["data_inicio"]
                    df = e.get("data_fim") if isinstance(e,dict) else e["data_fim"]
                    dc = e.get("data_cadastro") if isinstance(e,dict) else e["data_cadastro"]
                    status_auto = self._compute_status_from_dates(str(di), str(df)) or (e.get("status") if isinstance(e,dict) else e["status"])
                status_to_show = status_auto if status_auto else (getattr(e,"status","") or (e.get("status") if isinstance(e,dict) else ""))
                self.tree.insert("", "end", values=(id_ex, nome, tema, local, status_to_show, di, df, dc))
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro na busca: {ex}")

    def _carregar_lista(self):
        # carrega todas exposições para exibir na treeview
        for i in self.tree.get_children(): self.tree.delete(i)
        expos = self.controller.listar()
        for e in expos:
            try:
                id_ex = e.id_exposicao; nome = e.nome; tema = e.tema; local = e.localizacao; di = e.data_inicio or ""; df = e.data_fim or ""; dc = e.data_cadastro or ""
                status_auto = self._compute_status_from_dates(str(di), str(df))
            except Exception:
                id_ex = e.get("id_exposicao") if isinstance(e,dict) else e["id_exposicao"]
                nome = e.get("nome") if isinstance(e,dict) else e["nome"]
                tema = e.get("tema") if isinstance(e,dict) else e["tema"]
                local = e.get("localizacao") if isinstance(e,dict) else e["localizacao"]
                di = e.get("data_inicio") if isinstance(e,dict) else e["data_inicio"]
                df = e.get("data_fim") if isinstance(e,dict) else e["data_fim"]
                dc = e.get("data_cadastro") if isinstance(e,dict) else e["data_cadastro"]
                status_auto = self._compute_status_from_dates(str(di), str(df))
            status_to_show = status_auto if status_auto else (getattr(e,"status","") or (e.get("status") if isinstance(e,dict) else ""))
            self.tree.insert("", "end", values=(id_ex, nome, tema, local, status_to_show, di, df, dc))
            try:
                # para exposiçōes finalizadas, verifica obras e atualiza status
                if status_to_show == "Finalizada":
                    obras = self.controller.listar_obras(id_ex) or []
                    for p in obras:
                        try:
                            pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p, dict) else p["id_obra"])
                            if pid is None: continue
                            if not self._obra_em_qualquer_exposicao_ativa_hoje(int(pid), exclude_expo_id=id_ex):
                                pass
                        except Exception: continue
            except Exception: pass

    def _salvar(self):
        # lê campos do formulário, calcula status automático e chama controller.salvar para persistir
        nome = self.entry_nome.get().strip(); tema = self.entry_tema.get().strip(); local = self.entry_local.get().strip()
        data_inicio = self.entry_data_inicio.get().strip(); data_fim = self.entry_data_fim.get().strip()
        data_cad = self.entry_data_cadastro.get().strip(); desc = self.text_descricao.get("1.0", tk.END).strip()
        status_auto = self._compute_status_from_dates(data_inicio, data_fim)
        status_to_save = status_auto if status_auto else (self.entry_status.get().strip() or "")
        ok, msg = self.controller.salvar(self._id_atual, nome, tema, local, status_to_save, data_inicio, data_fim, data_cad, desc)
        if ok:
            try:
                # se mudou para "Em Curso", marca obras como "Em Exposição"
                new_status = status_to_save
                if new_status == "Em Curso":
                    obras = self.controller.listar_obras(self._id_atual) or []
                    for p in obras:
                        try:
                            pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"])
                            if pid is None: continue
                            self._set_obra_status(int(pid), "Em Exposição")
                        except Exception: continue
                # se está Finalizada ou Planejada, libera obras que não estejam em outras exposições ativas
                if new_status in ("Finalizada","Planejada"):
                    obras = self.controller.listar_obras(self._id_atual) or []
                    for p in obras:
                        try:
                            pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"])
                            if pid is None: continue
                            if not self._obra_em_qualquer_exposicao_ativa_hoje(int(pid), exclude_expo_id=self._id_atual):
                                self._set_obra_status(int(pid), "Disponível")
                        except Exception: continue
            except Exception: pass
            messagebox.showinfo("Sucesso", msg); self._limpar(); self._carregar_lista()
        else:
            messagebox.showerror("Erro", msg)

    def _limpar(self):
        # limpa formulário
        self._id_atual = None; self._prev_status = None; self._prev_start = None; self._prev_end = None
        try:
            self.entry_nome.delete(0, tk.END); self.entry_tema.delete(0, tk.END); self.entry_local.delete(0, tk.END)
            try: self.entry_status.config(state="normal"); self.entry_status.delete(0, tk.END); self.entry_status.config(state="readonly")
            except Exception: pass
            self.entry_data_inicio.delete(0, tk.END); self.entry_data_fim.delete(0, tk.END); self.entry_data_cadastro.delete(0, tk.END)
            self.text_descricao.delete("1.0", tk.END)
        except Exception: pass

    def _on_duplo(self, event):
        # duplo-clique na listagem carrega exposição selecionada para edição
        sel = self.tree.selection();
        if not sel: return
        vals = self.tree.item(sel)["values"]
        if not vals: return
        id_ex = vals[0]; expos = self.controller.carregar(id_ex)
        if not expos: messagebox.showerror("Erro", "Não foi possível carregar exposição."); return
        try:
            # tenta preencher campos a partir de objeto retornado pelo controller
            e = expos
            self._id_atual = e.id_exposicao
            self.entry_nome.delete(0, tk.END); self.entry_nome.insert(0, e.nome)
            self.entry_tema.delete(0, tk.END); self.entry_tema.insert(0, e.tema)
            self.entry_local.delete(0, tk.END); self.entry_local.insert(0, e.localizacao)
            di = e.data_inicio or ""; df = e.data_fim or ""
            status_auto = self._compute_status_from_dates(str(di), str(df))
            status_val = status_auto if status_auto else (e.status.value if hasattr(e, "status") else (getattr(e,"status","") or ""))
            try: self.entry_status.config(state="normal"); self.entry_status.delete(0, tk.END); self.entry_status.insert(0, status_val); self.entry_status.config(state="readonly")
            except Exception: pass
            self.entry_data_inicio.delete(0, tk.END); self.entry_data_inicio.insert(0, di or "")
            self.entry_data_fim.delete(0, tk.END); self.entry_data_fim.insert(0, df or "")
            self.entry_data_cadastro.delete(0, tk.END); self.entry_data_cadastro.insert(0, e.data_cadastro or "")
            self.text_descricao.delete("1.0", tk.END); self.text_descricao.insert("1.0", e.descricao or "")
            self._prev_status = status_val; self._prev_start = self._parse_data(str(di)) if di else None; self._prev_end = self._parse_data(str(df)) if df else None
        except Exception:
            e = expos
            self._id_atual = e["id_exposicao"]
            self.entry_nome.delete(0, tk.END); self.entry_nome.insert(0, e["nome"])
            self.entry_tema.delete(0, tk.END); self.entry_tema.insert(0, e["tema"])
            self.entry_local.delete(0, tk.END); self.entry_local.insert(0, e["localizacao"])
            di = e.get("data_inicio","") or ""; df = e.get("data_fim","") or ""
            status_auto = self._compute_status_from_dates(str(di), str(df)); status_val = status_auto if status_auto else (e.get("status","") or "")
            try: self.entry_status.config(state="normal"); self.entry_status.delete(0, tk.END); self.entry_status.insert(0, status_val); self.entry_status.config(state="readonly")
            except Exception: pass
            self.entry_data_inicio.delete(0, tk.END); self.entry_data_inicio.insert(0, di)
            self.entry_data_fim.delete(0, tk.END); self.entry_data_fim.insert(0, df)
            self.entry_data_cadastro.delete(0, tk.END); self.entry_data_cadastro.insert(0, e.get("data_cadastro","") or "")
            self.text_descricao.delete("1.0", tk.END); self.text_descricao.insert("1.0", e.get("descricao","") or "")
            self._prev_status = status_val; self._prev_start = self._parse_data(str(di)) if di else None; self._prev_end = self._parse_data(str(df)) if df else None

    # ---------------- popup selecionador de obras (modal) ----------------
    def _abrir_popup_adicionar_obra(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma exposição para adicionar obras.")
            return
        row = self.tree.item(sel)["values"]
        try:
            id_exposicao = int(row[0])
        except Exception:
            messagebox.showerror("Erro", "ID de exposição inválido.")
            return

        data_inicio_str = row[5] if len(row) > 5 else self.entry_data_inicio.get().strip()
        data_fim_str = row[6] if len(row) > 6 else self.entry_data_fim.get().strip()
        data_inicio = self._parse_data(data_inicio_str)
        data_fim = self._parse_data(data_fim_str)

        if self._compute_status_from_dates(data_inicio_str, data_fim_str) == "Finalizada":
            messagebox.showerror("Erro", "Não é possível adicionar obras a uma exposição finalizada.")
            return

        initial_participacao_ids = set()
        to_add = set()
        to_remove = set()

        # janela/modal
        win = tk.Toplevel(self.root)
        win.title("Gerenciar Obras")
        win.transient(self.root)
        win.grab_set()
        win.geometry("900x520")

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        cols = ("id", "titulo", "artista", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
        for c, w in [("id", 60), ("titulo", 460), ("artista", 200), ("status", 120)]:
            tree.heading(c, text=c.title())
            tree.column(c, anchor="w", width=w)
        tree.pack(fill="both", expand=True, padx=6, pady=(6, 4))

        # tags visuais
        tree.tag_configure("in_exposicao", background="#E8F6E8")
        tree.tag_configure("busy", background="#F8E8E8")
        tree.tag_configure("to_add", background="#D6F5D6")
        tree.tag_configure("to_remove", background="#F5D6D6")

        def carregar():
            nonlocal initial_participacao_ids
            for i in tree.get_children():
                tree.delete(i)

            participacoes = self.controller.listar_obras(id_exposicao) or []
            initial_participacao_ids = {int(p["id_obra"]) for p in participacoes}

            obras = self.obra_controller.listar_obras() or []
            for o in obras:
                oid = int(o.id_obra)
                titulo = o.titulo
                artista = str(o.artista) if o.artista is not None else ""
                status_db = self._normalizar_status(o.status)

                # determinar status_display
                if oid in to_add or oid in initial_participacao_ids:
                    status_display = "Em Exposição"
                else:
                    if data_inicio and data_fim:
                        ocupado = self._obra_ocupada_em_periodo(oid, data_inicio, data_fim, exclude_expo_id=id_exposicao)
                        status_display = "Em Exposição" if ocupado else ("Disponível" if status_db not in ("Alugada", "Vendida", "Empréstimo") else status_db)
                    else:
                        if status_db == "Em Exposição":
                            ocupado_hoje = self._obra_em_qualquer_exposicao_ativa_hoje(oid, exclude_expo_id=id_exposicao)
                            status_display = "Em Exposição" if ocupado_hoje else "Disponível"
                        else:
                            status_display = status_db or "Disponível"

                # determinar tag
                if oid in to_add:
                    tag = "to_add"
                elif oid in to_remove:
                    tag = "to_remove"
                elif oid in initial_participacao_ids:
                    tag = "in_exposicao"
                else:
                    tag = "busy" if status_display.lower() != "disponível" else ""

                # texto do título
                if oid in to_add:
                    display_titulo = f"{titulo} (+)"
                elif oid in to_remove:
                    display_titulo = f"{titulo} (–)"
                elif oid in initial_participacao_ids:
                    display_titulo = f"{titulo} (✓)"
                else:
                    display_titulo = titulo

                tree.insert("", "end", values=(oid, display_titulo, artista, status_display), tags=(tag,))

        def toggle_adicionar():
            sel_items = tree.selection()
            if not sel_items:
                messagebox.showwarning("Aviso", "Selecione uma obra para marcar para adicionar.")
                return
            nonlocal to_add, to_remove
            changed = False
            for item in sel_items:
                values = tree.item(item, "values")
                id_obra = int(values[0])
                if id_obra in to_remove:
                    to_remove.remove(id_obra)
                    changed = True
                    continue
                if id_obra in initial_participacao_ids:
                    messagebox.showinfo("Info", f"Obra ID {id_obra} já está vinculada à exposição.")
                    continue
                if not self._obra_efetivamente_disponivel(id_obra, data_inicio, data_fim, exclude_expo_id=id_exposicao):
                    messagebox.showwarning("Atenção", f"Obra ID {id_obra} não pode ser marcada para adicionar (não disponível).")
                    continue
                if id_obra in to_add:
                    to_add.remove(id_obra)
                else:
                    to_add.add(id_obra)
                changed = True
            if changed:
                carregar()

        def toggle_remover():
            sel_items = tree.selection()
            if not sel_items:
                messagebox.showwarning("Aviso", "Selecione uma obra para marcar para remoção.")
                return
            nonlocal to_add, to_remove
            changed = False
            for item in sel_items:
                values = tree.item(item, "values")
                id_obra = int(values[0])
                if id_obra in to_add:
                    to_add.remove(id_obra)
                    changed = True
                    continue
                if id_obra not in initial_participacao_ids:
                    messagebox.showinfo("Info", f"Obra ID {id_obra} não está vinculada atualmente; marque-a para adicionar em vez disso.")
                    continue
                if id_obra in to_remove:
                    to_remove.remove(id_obra)
                else:
                    to_remove.add(id_obra)
                changed = True
            if changed:
                carregar()

        def confirmar():
            nonlocal id_exposicao
            id_exposicao = int(id_exposicao)
            any_change = False

            # ---- REMOVER ----
            for id_obra in list(to_remove):
                id_obra = int(id_obra)
                res = self.controller.remover_obra(id_exposicao, id_obra)
                ok = bool(res[0]) if isinstance(res, tuple) else bool(res)
                msg = res[1] if isinstance(res, tuple) and len(res) > 1 else None
                if ok:
                    if not self._obra_em_qualquer_exposicao_ativa_hoje(id_obra, exclude_expo_id=id_exposicao):
                        self._set_obra_status(id_obra, "Disponível")
                    any_change = True
                else:
                    messagebox.showerror("Erro", msg or f"Não foi possível remover obra ID {id_obra}.")

            # ---- ADICIONAR ----
            for id_obra in list(to_add):
                id_obra = int(id_obra)
                if not self._obra_efetivamente_disponivel(id_obra, data_inicio, data_fim, exclude_expo_id=id_exposicao):
                    messagebox.showwarning("Atenção", f"Obra ID {id_obra} não está disponível. Não será adicionada.")
                    continue

                ocupado = self._obra_ocupada_em_periodo(id_obra, data_inicio, data_fim, exclude_expo_id=id_exposicao)
                if ocupado:
                    messagebox.showwarning("Atenção", f"Obra ID {id_obra} está ocupada em período conflituoso.")
                    continue

                res = self.controller.adicionar_obra(id_exposicao, id_obra)
                ok = bool(res[0]) if isinstance(res, tuple) else bool(res)
                msg = res[1] if isinstance(res, tuple) and len(res) > 1 else None

                if ok:
                    # atualiza status na aplicação
                    self._set_obra_status(id_obra, "Em Exposição")
                    try:
                        if hasattr(self.obra_controller, "db_manager"):
                            with self.obra_controller.db_manager.cursor() as cur:
                                cur.execute("UPDATE obras SET status = ? WHERE id_obra = ?", ("Em Exposição", int(id_obra)))
                    except Exception:
                        pass
                    any_change = True
                else:
                    messagebox.showerror("Erro", msg or f"Não foi possível adicionar obra ID {id_obra}.")

            if any_change:
                messagebox.showinfo("Sucesso", "Alterações aplicadas.")
            win.destroy()
            self._carregar_lista()

        # botões
        btns_frame = ttk.Frame(frame)
        btns_frame.pack(fill="x", pady=(6, 6))
        left_frame = ttk.Frame(btns_frame)
        left_frame.pack(side="left", fill="x", expand=True)
        right_frame = ttk.Frame(btns_frame)
        right_frame.pack(side="right")

        ttk.Button(left_frame, text="Confirmar Seleção", command=confirmar).pack(side="left", padx=8)
        ttk.Button(left_frame, text="Cancelar", command=win.destroy).pack(side="left", padx=8)
        ttk.Button(right_frame, text="Remover", command=toggle_remover, width=14).pack(side="right", padx=6)
        ttk.Button(right_frame, text="Adicionar", command=toggle_adicionar, width=14).pack(side="right", padx=6)

        carregar()
        win.deiconify()
        win.wait_window()

    def voltar_inicio(self):
        try:
            from src.views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import)."); return
        for w in self.root.winfo_children(): w.destroy()
        TelaInicial(self.root, self.manager)
