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

        for w in self.root.winfo_children(): w.destroy()
        self.root.title("Exposições"); self.root.geometry("800x600"); self.root.minsize(800,600)
        bg = "#F3F4F6"; self.root.configure(bg=bg)
        style = ttk.Style()
        try: style.theme_use("clam")
        except Exception: pass
        style.configure("TFrame", background=bg); style.configure("TLabel", background=bg)
        style.configure("TLabelframe", background=bg); style.configure("TLabelframe.Label", background=bg)

        # Top frame (form)
        frm_top = ttk.LabelFrame(self.root, text="Cadastro de Exposição", padding=10); frm_top.pack(fill="x", padx=10, pady=8)
        for c in range(9):
            frm_top.columnconfigure(c, weight=(1 if c < 8 else 0), uniform="col", minsize=(0 if c < 8 else 180))

        # linha 0
        campos_linha0 = [("Nome:","entry_nome"),("Tema:","entry_tema"),("Localização:","entry_local"),("Status:","entry_status")]
        for idx, (lbl, attr) in enumerate(campos_linha0):
            ttk.Label(frm_top, text=lbl).grid(row=0, column=idx*2, sticky="w", padx=(10,5), pady=4)
            ent = ttk.Entry(frm_top, state="readonly") if attr=="entry_status" else ttk.Entry(frm_top)
            ent.grid(row=0, column=idx*2+1, sticky="ew", padx=(5,10), pady=4); setattr(self, attr, ent)

        # linha 1
        campos_linha1 = [("Data Início:","entry_data_inicio"),("Data Fim:","entry_data_fim"),("Data Cadastro:","entry_data_cadastro")]
        for idx, (lbl, attr) in enumerate(campos_linha1):
            ttk.Label(frm_top, text=lbl).grid(row=1, column=idx*2, sticky="w", padx=(10,5), pady=4)
            ent = ttk.Entry(frm_top, state="readonly") if attr=="entry_data_cadastro" else ttk.Entry(frm_top)
            ent.grid(row=1, column=idx*2+1, sticky="ew", padx=(5,10), pady=4); setattr(self, attr, ent)

        try:
            self.entry_data_cadastro.config(state="normal"); self.entry_data_cadastro.delete(0, tk.END)
            self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y")); self.entry_data_cadastro.config(state="readonly")
        except Exception:
            pass

        # descricao
        ttk.Label(frm_top, text="Descrição:").grid(row=2, column=0, sticky="nw", padx=(10,5), pady=4)
        self.text_descricao = tk.Text(frm_top, height=5, relief="solid", borderwidth=1, bg="white")
        self.text_descricao.grid(row=2, column=1, columnspan=7, sticky="nsew", padx=(5,10), pady=4); frm_top.rowconfigure(2, weight=1)

        # home button
        frame_home = tk.Frame(frm_top, bg="#f0f0f0"); frame_home.place(relx=1, rely=0, x=15, y=-35, anchor="ne")
        self.btn_home = tk.Button(frame_home, text="❌", font=("Segoe UI Emoji",10), bd=0, highlightthickness=0,
                                  padx=0, pady=0, bg="#f0f0f0", activebackground="#dddddd", cursor="hand2",
                                  command=self.voltar_inicio)
        self.btn_home.pack(expand=True, fill="both")

        # right-side buttons
        btn_frame = ttk.Frame(frm_top); btn_frame.grid(row=0, column=8, rowspan=3, sticky="n", padx=8, pady=4)
        ttk.Button(btn_frame, text="Salvar", command=self._salvar, width=18).pack(pady=6)
        ttk.Button(btn_frame, text="Cancelar", command=self._limpar, width=18).pack(pady=6)
        ttk.Button(btn_frame, text="Buscar", command=self._buscar, width=18).pack(pady=6)

        # listagem
        frm_list = ttk.LabelFrame(self.root, text="Listagem de Exposições", padding=8); frm_list.pack(fill="both", expand=True, padx=10, pady=(0,10))
        frm_list.columnconfigure(0, weight=1); frm_list.rowconfigure(0, weight=1)
        cols = ("id","nome","tema","local","status","data_inicio","data_fim","data_cadastro")
        self.tree = ttk.Treeview(frm_list, columns=cols, show="headings")
        widths = {"id":60,"nome":250,"tema":140,"local":140,"status":100,"data_inicio":90,"data_fim":90,"data_cadastro":110}
        for c in cols:
            self.tree.heading(c, text=c.replace("_"," ").title()); self.tree.column(c, width=widths.get(c,100), anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(frm_list, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=yscroll.set); yscroll.grid(row=0, column=1, sticky="ns")

        btns_bottom = ttk.Frame(self.root); btns_bottom.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(btns_bottom, text="Adicionar obra", command=self._abrir_popup_adicionar_obra, width=20).pack(side="right")

        self._id_atual = None; self._prev_status = None; self._prev_start = None; self._prev_end = None
        self._carregar_lista(); self.tree.bind("<Double-1>", self._on_duplo)

    # ---------------- helpers compactos ----------------
    def _parse_data(self, s: str) -> Optional[date]:
        if not s: return None
        for fmt in ("%d/%m/%Y","%Y-%m-%d"):
            try: return datetime.strptime(s, fmt).date()
            except Exception: continue
        return None

    def _compute_status_from_dates(self, inicio_s: str, fim_s: str) -> str:
        inicio = self._parse_data(inicio_s); fim = self._parse_data(fim_s); hoje = date.today()
        if inicio and fim:
            if hoje < inicio: return "Planejada"
            if inicio <= hoje <= fim: return "Em Curso"
            return "Finalizada"
        if inicio and not fim: return "Planejada" if hoje < inicio else "Em Curso"
        if not inicio and fim: return "Em Curso" if hoje <= fim else "Finalizada"
        return ""

    def _execute_update(self, sql, params=()):
        try:
            if self.manager:
                dbobj = getattr(self.manager, "db", None)
                if dbobj and hasattr(dbobj, "cursor"):
                    with dbobj.cursor() as c: c.execute(sql, params)
                    try: dbobj.commit()
                    except Exception: pass
                    return True
                if hasattr(self.manager, "conectar"):
                    conn = self.manager.conectar(); cur = conn.cursor(); cur.execute(sql, params); conn.commit(); conn.close(); return True
                if hasattr(self.manager, "cursor"):
                    with self.manager.cursor() as c: c.execute(sql, params); 
                    try: self.manager.commit()
                    except Exception: pass
                    return True
            import database.manager as dbmod
            dbobj = getattr(dbmod, "db", None)
            if dbobj and hasattr(dbobj, "cursor"):
                with dbobj.cursor() as c: c.execute(sql, params)
                try: dbobj.commit()
                except Exception: pass
                return True
        except Exception:
            return False
        return False

    def _set_obra_status(self, id_obra: int, novo_status: str) -> bool:
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
        try:
            for name in ("atualizar_status_obra","set_status_obra","atualizarObraStatus"):
                if hasattr(self.controller, name):
                    fn = getattr(self.controller, name)
                    res = fn(self._id_atual, id_obra, novo_status); return bool(res[0]) if isinstance(res, tuple) else bool(res)
        except Exception:
            pass
        ok = self._execute_update("UPDATE obras SET status=? WHERE id_obra=?", (novo_status, id_obra))
        if ok: return True
        return self._execute_update("UPDATE obras SET status=%s WHERE id_obra=%s", (novo_status, id_obra))

    def _get_status_da_obra(self, id_obra: int) -> str:
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
        try:
            for q, params in [("SELECT status FROM obras WHERE id_obra=?", (id_obra,)), ("SELECT status FROM obras WHERE id_obra=%s", (id_obra,))]:
                if self.manager:
                    dbobj = getattr(self.manager, "db", None)
                    if dbobj and hasattr(dbobj, "cursor"):
                        with dbobj.cursor() as c: c.execute(q, params); row = c.fetchone()
                        if row: return self._normalizar_status(row[0])
                    else:
                        conn = self.manager.conectar(); cur = conn.cursor(); cur.execute(q, params); row = cur.fetchone(); conn.close(); 
                        if row: return self._normalizar_status(row[0])
        except Exception: pass
        return ""

    def _normalizar_status(self, status_raw) -> str:
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
        try:
            if hasattr(self.controller, "exposicoes_por_obra"):
                expos = self.controller.exposicoes_por_obra(id_obra) or []
                for ex in expos:
                    try:
                        ex_id = getattr(ex,"id_exposicao",None) or (ex.get("id_exposicao") if isinstance(ex,dict) else ex["id_exposicao"])
                        if exclude_expo_id and int(ex_id)==int(exclude_expo_id): continue
                        s = self._parse_data(getattr(ex,"data_inicio",None) or (ex.get("data_inicio") if isinstance(ex,dict) else None)) 
                        e = self._parse_data(getattr(ex,"data_fim",None) or (ex.get("data_fim") if isinstance(ex,dict) else None))
                        if s and e and inicio and fim:
                            if not (e < inicio or s > fim): return True
                        else:
                            return True
                    except Exception: continue
            expos_all = self.controller.listar() or []
            for ex in expos_all:
                try:
                    ex_id = getattr(ex,"id_exposicao",None) or (ex.get("id_exposicao") if isinstance(ex,dict) else ex["id_exposicao"])
                    if exclude_expo_id and int(ex_id)==int(exclude_expo_id): continue
                    s = self._parse_data(getattr(ex,"data_inicio",None) or (ex.get("data_inicio") if isinstance(ex,dict) else None))
                    e = self._parse_data(getattr(ex,"data_fim",None) or (ex.get("data_fim") if isinstance(ex,dict) else None))
                    try:
                        obras = self.controller.listar_obras(ex_id) or []
                    except Exception:
                        obras = []
                    ids = { (getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"])) for p in obras }
                    if int(id_obra) not in {int(x) for x in ids}: continue
                    if s and e and inicio and fim:
                        if not (e < inicio or s > fim): return True
                    else:
                        return True
                except Exception: continue
        except Exception:
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
        hoje = date.today(); return self._obra_ocupada_em_periodo(id_obra, hoje, hoje, exclude_expo_id=exclude_expo_id)

    def _buscar(self):
        filtros = {}
        def put(k,val): 
            if val: filtros[k]=val
        put("nome", self.entry_nome.get().strip()); put("tema", self.entry_tema.get().strip()); put("localizacao", self.entry_local.get().strip())
        put("status", self.entry_status.get().strip()); put("data_inicio", self.entry_data_inicio.get().strip()); put("data_fim", self.entry_data_fim.get().strip())
        put("data_cadastro", self.entry_data_cadastro.get().strip()); put("descricao", self.text_descricao.get("1.0", tk.END).strip())
        try:
            if not filtros: self._carregar_lista(); return
            resultados = self.controller.buscar(filtros)
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
                if status_to_show == "Finalizada":
                    try: obras = self.controller.listar_obras(id_ex) or []
                    except Exception: obras = []
                    for p in obras:
                        try:
                            pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p, dict) else p["id_obra"])
                            if pid is None: continue
                            if not self._obra_em_qualquer_exposicao_ativa_hoje(int(pid), exclude_expo_id=id_ex):
                                self._set_obra_status(int(pid), "Disponível")
                        except Exception: continue
            except Exception: pass

    def _salvar(self):
        nome = self.entry_nome.get().strip(); tema = self.entry_tema.get().strip(); local = self.entry_local.get().strip()
        data_inicio = self.entry_data_inicio.get().strip(); data_fim = self.entry_data_fim.get().strip()
        data_cad = self.entry_data_cadastro.get().strip(); desc = self.text_descricao.get("1.0", tk.END).strip()
        status_auto = self._compute_status_from_dates(data_inicio, data_fim)
        status_to_save = status_auto if status_auto else (self.entry_status.get().strip() or "")
        ok, msg = self.controller.salvar(self._id_atual, nome, tema, local, status_to_save, data_inicio, data_fim, data_cad, desc)
        if ok:
            try:
                new_status = status_to_save
                if new_status == "Em Curso":
                    try: obras = self.controller.listar_obras(self._id_atual) or []
                    except Exception: obras = []
                    for p in obras:
                        try:
                            pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"])
                            if pid is None: continue
                            self._set_obra_status(int(pid), "Em Exposição")
                        except Exception: continue
                if new_status in ("Finalizada","Planejada"):
                    try: obras = self.controller.listar_obras(self._id_atual) or []
                    except Exception: obras = []
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
        self._id_atual = None; self._prev_status = None; self._prev_start = None; self._prev_end = None
        try:
            self.entry_nome.delete(0, tk.END); self.entry_tema.delete(0, tk.END); self.entry_local.delete(0, tk.END)
            try: self.entry_status.config(state="normal"); self.entry_status.delete(0, tk.END); self.entry_status.config(state="readonly")
            except Exception: pass
            self.entry_data_inicio.delete(0, tk.END); self.entry_data_fim.delete(0, tk.END); self.entry_data_cadastro.delete(0, tk.END)
            self.text_descricao.delete("1.0", tk.END)
        except Exception: pass

    def _on_duplo(self, event):
        sel = self.tree.selection(); 
        if not sel: return
        vals = self.tree.item(sel)["values"]
        if not vals: return
        id_ex = vals[0]; expos = self.controller.carregar(id_ex)
        if not expos: messagebox.showerror("Erro", "Não foi possível carregar exposição."); return
        try:
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
            messagebox.showwarning("Aviso", "Selecione uma exposição para adicionar obras."); return
        id_exposicao = int(self.tree.item(sel)["values"][0])
        data_inicio_str = self.entry_data_inicio.get().strip(); data_fim_str = self.entry_data_fim.get().strip()
        data_inicio = self._parse_data(data_inicio_str); data_fim = self._parse_data(data_fim_str)
        status_atual = self._compute_status_from_dates(data_inicio_str, data_fim_str)
        if status_atual == "Finalizada":
            messagebox.showerror("Erro", "Não é possível adicionar obras a uma exposição finalizada."); return

        # estado local
        initial_participacao_ids = set(); to_add = set(); to_remove = set()

        win = tk.Toplevel(self.root); win.title("Gerenciar Obras"); win.transient(self.root); win.grab_set()
        win.geometry("900x520")
        frame = ttk.Frame(win, padding=10); frame.pack(fill="both", expand=True)
        cols = ("id","titulo","artista","status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="extended")
        for c,w in [("id",60),("titulo",460),("artista",200),("status",120)]: tree.heading(c,text=c.title()); tree.column(c,anchor="w", width=w)
        tree.pack(fill="both", expand=True, padx=6, pady=(6,4))
        try:
            tree.tag_configure("in_exposicao", background="#E8F6E8"); tree.tag_configure("busy", background="#F8E8E8")
            tree.tag_configure("to_add", background="#D6F5D6"); tree.tag_configure("to_remove", background="#F5D6D6")
        except Exception: pass

        btns_frame = ttk.Frame(frame); btns_frame.pack(fill="x", pady=(6,6))
        left_frame = ttk.Frame(btns_frame); left_frame.pack(side="left", fill="x", expand=True)
        right_frame = ttk.Frame(btns_frame); right_frame.pack(side="right")
        ttk.Button(left_frame, text="Confirmar Seleção", command=lambda: confirmar()).pack(side="left", padx=8)
        ttk.Button(left_frame, text="Cancelar", command=win.destroy).pack(side="left", padx=8)
        ttk.Button(right_frame, text="Remover", command=lambda: toggle_remover(), width=14).pack(side="right", padx=6)
        ttk.Button(right_frame, text="Adicionar", command=lambda: toggle_adicionar(), width=14).pack(side="right", padx=6)

        # sincroniza exposicoes finalizadas (libera obras)
        try:
            expos = self.controller.listar() or []
        except Exception: expos = []
        hoje = date.today()
        for ex in expos:
            try:
                ex_id = getattr(ex,"id_exposicao",None) or (ex.get("id_exposicao") if isinstance(ex,dict) else ex["id_exposicao"])
                inicio = getattr(ex,"data_inicio",None) or (ex.get("data_inicio") if isinstance(ex,dict) else None)
                fim = getattr(ex,"data_fim",None) or (ex.get("data_fim") if isinstance(ex,dict) else None)
                si = self._parse_data(str(inicio)) if inicio else None; sf = self._parse_data(str(fim)) if fim else None
                if si and sf and hoje > sf:
                    try: obras = self.controller.listar_obras(ex_id) or []
                    except Exception: obras = []
                    for p in obras:
                        try:
                            pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"])
                            if pid is None: continue
                            if not self._obra_em_qualquer_exposicao_ativa_hoje(int(pid), exclude_expo_id=ex_id):
                                self._set_obra_status(int(pid), "Disponível")
                        except Exception: continue
            except Exception: continue

        def carregar():
            nonlocal initial_participacao_ids
            for i in tree.get_children(): tree.delete(i)
            participacao_ids = set()
            try:
                participacoes = self.controller.listar_obras(id_exposicao) or []
                for p in participacoes:
                    try: pid = getattr(p,"id_obra",None) or (p.get("id_obra") if isinstance(p,dict) else p["id_obra"]); participacao_ids.add(int(pid))
                    except Exception: continue
            except Exception: participacao_ids = set()
            initial_participacao_ids = participacao_ids.copy()

            try: obras = self.obra_controller.listar_obras() or []
            except Exception:
                try: obras = self.obra_controller.listar() or []
                except Exception: obras = []

            for o in obras:
                try:
                    oid = getattr(o,"id_obra",None) or (o.get("id_obra") if isinstance(o,dict) else o["id_obra"])
                except Exception: oid = ""
                try: titulo = getattr(o,"titulo",None) or (o.get("titulo") if isinstance(o,dict) else str(o))
                except Exception: titulo = str(o)
                artista = ""
                try:
                    if hasattr(o,"artista") and o.artista is not None:
                        a = o.artista; artista = a if isinstance(a,str) else (getattr(a,"nome",None) or getattr(a,"name",None) or str(a))
                    else:
                        if isinstance(o,dict): artista = o.get("nome_artista") or o.get("artista") or ""
                        else: artista = getattr(o,"nome_artista","") or getattr(o,"artista","") or ""
                    artista = str(artista) if artista is not None else ""
                except Exception: artista = ""
                try: status_db = self._normalizar_status(getattr(o,"status",None) or (o.get("status") if isinstance(o,dict) else ""))
                except Exception: status_db = ""
                status_display = status_db
                try:
                    if oid and int(oid) in participacao_ids: status_display = "Em Exposição"
                    else:
                        if data_inicio and data_fim:
                            ocupado = self._obra_ocupada_em_periodo(int(oid), data_inicio, data_fim, exclude_expo_id=id_exposicao)
                            status_display = "Em Exposição" if ocupado else "Disponível"
                        else:
                            status_display = status_db or status_display
                except Exception: status_display = status_db

                tag = ""; display_titulo = titulo
                try:
                    if oid and int(oid) in initial_participacao_ids: display_titulo = f"{titulo} (✓)"; tag = "in_exposicao"
                    if oid and int(oid) in to_add: display_titulo = f"{titulo} (✓)"; tag = "to_add"
                    if oid and int(oid) in to_remove: tag = "to_remove"
                    if (not tag) and status_display and status_display.lower() != "disponível": tag = "busy"
                except Exception: pass

                try: tree.insert("", "end", values=(oid, display_titulo, artista, status_display), tags=(tag,))
                except Exception: tree.insert("", "end", values=(oid, display_titulo, artista, status_display))

        def toggle_adicionar():
            sel_items = tree.selection()
            if not sel_items: messagebox.showwarning("Aviso", "Selecione uma obra para marcar para adicionar."); return
            nonlocal to_add, to_remove
            changed = False
            for item in sel_items:
                try:
                    values = tree.item(item, "values"); id_obra = int(values[0])
                    if id_obra in initial_participacao_ids:
                        messagebox.showinfo("Info", f"Obra ID {id_obra} já está vinculada à exposição."); continue
                    status_atual = self._get_status_da_obra(id_obra).lower() if self._get_status_da_obra(id_obra) else ""
                    if status_atual != "disponível":
                        messagebox.showwarning("Atenção", f"Obra ID {id_obra} não pode ser marcada para adicionar (status atual: {status_atual or 'desconhecido'})."); continue
                    if id_obra in to_add: to_add.remove(id_obra)
                    else:
                        if id_obra in to_remove: to_remove.remove(id_obra)
                        to_add.add(id_obra)
                    changed = True
                except Exception: continue
            if changed: carregar()

        def toggle_remover():
            sel_items = tree.selection()
            if not sel_items: messagebox.showwarning("Aviso", "Selecione uma obra para marcar para remoção."); return
            nonlocal to_add, to_remove
            changed = False
            for item in sel_items:
                try:
                    values = tree.item(item, "values"); id_obra = int(values[0])
                    if id_obra not in initial_participacao_ids:
                        messagebox.showinfo("Info", f"Obra ID {id_obra} não está vinculada atualmente; marque-a para adicionar em vez disso."); continue
                    if id_obra in to_remove: to_remove.remove(id_obra)
                    else:
                        if id_obra in to_add: to_add.remove(id_obra)
                        to_remove.add(id_obra)
                    changed = True
                except Exception: continue
            if changed: carregar()

        def confirmar():
            any_change = False
            # remover primeiro
            for id_obra in list(to_remove):
                try:
                    ok = False; msg = None
                    try:
                        res = self.controller.remover_obra(id_exposicao, id_obra)
                        if isinstance(res, tuple): ok, msg = res
                        else: ok = bool(res)
                    except Exception as e: ok = False; msg = str(e)
                    if not ok:
                        try:
                            deleted = self._execute_update("DELETE FROM participacao_exposicao WHERE id_exposicao = ? AND id_obra = ?", (id_exposicao, id_obra))
                            if deleted: ok = True
                        except Exception: pass
                    if ok:
                        if not self._obra_em_qualquer_exposicao_ativa_hoje(id_obra, exclude_expo_id=id_exposicao):
                            self._set_obra_status(id_obra, "Disponível")
                        any_change = True
                    else:
                        messagebox.showerror("Erro", msg or f"Não foi possível remover obra ID {id_obra}.")
                except Exception as e: messagebox.showerror("Erro", f"Erro ao remover obra ID {id_obra}: {e}")

            # adicionar
            for id_obra in list(to_add):
                try:
                    status_fresco = self._get_status_da_obra(id_obra).lower() if self._get_status_da_obra(id_obra) else ""
                    if status_fresco != "disponível":
                        messagebox.showwarning("Atenção", f"Obra ID {id_obra} não está disponível (status atual: {status_fresco or 'desconhecido'}). Não será adicionada."); continue
                    ocupado = False
                    if data_inicio and data_fim: ocupado = self._obra_ocupada_em_periodo(id_obra, data_inicio, data_fim, exclude_expo_id=id_exposicao)
                    else: ocupado = self._obra_ocupada_em_periodo(id_obra, None, None, exclude_expo_id=id_exposicao)
                    if ocupado:
                        messagebox.showwarning("Atenção", f"Obra ID {id_obra} está ocupada em período conflituoso e não será adicionada."); continue
                    ok = False; msg = None
                    try:
                        res = self.controller.adicionar_obra(id_exposicao, id_obra)
                        if isinstance(res, tuple): ok, msg = res
                        else: ok = bool(res)
                    except Exception as e: ok=False; msg=str(e)
                    if not ok:
                        try:
                            now_str = date.today().strftime("%d/%m/%Y")
                            inserted = self._execute_update("INSERT OR IGNORE INTO participacao_exposicao (id_exposicao,id_obra,data_inclusao,observacao) VALUES (?, ?, ?, ?)", (id_exposicao, id_obra, now_str, None))
                            if inserted: ok = True
                        except Exception: pass
                        if not ok:
                            try:
                                if hasattr(self.controller, "db") and hasattr(self.controller.db, "inserir_participacao_exposicao"):
                                    p = type("P", (), {})()
                                    p.id_exposicao = id_exposicao; p.id_obra = id_obra; p.data_inclusao = date.today().strftime("%d/%m/%Y"); p.observacao = None
                                    res2 = self.controller.db.inserir_participacao_exposicao(p)
                                    if isinstance(res2, tuple): ok = bool(res2[0])
                                    else: ok = bool(res2)
                            except Exception: pass
                    if ok:
                        self._set_obra_status(id_obra, "Em Exposição"); any_change = True
                    else:
                        messagebox.showerror("Erro", msg or f"Não foi possível adicionar obra ID {id_obra}.")
                except Exception as e: messagebox.showerror("Erro", f"Erro ao adicionar obra ID {id_obra}: {e}")

            if any_change: messagebox.showinfo("Sucesso", "Alterações aplicadas.")
            win.destroy(); self._carregar_lista()

        carregar()
        try:
            win.deiconify()
        except Exception: pass
        win.wait_window()

    def voltar_inicio(self):
        try:
            from src.views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import)."); return
        for w in self.root.winfo_children(): w.destroy()
        TelaInicial(self.root, self.manager)
