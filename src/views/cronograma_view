import subprocess
import sys
import math
import hashlib
import colorsys
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from src.controllers.exposicao_controller import ExposicaoController

WEEKDAYS_PT = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# ---------------- Helpers ----------------
def _parse_data_valida(v):
    """Aceita date, datetime, ISO (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) e DD/MM/YYYY. Retorna date ou None."""
    if v is None:
        return None
    if isinstance(v, date) and not isinstance(v, datetime):
        return v
    if isinstance(v, datetime):
        return v.date()
    s = str(v).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return None

def _hsv_para_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02X}{:02X}{:02X}".format(int(r*255), int(g*255), int(b*255))

def _cor_deterministica(titulo: str, inicio: date, fim: date):
    key = f"{titulo}|{inicio.isoformat()}|{fim.isoformat()}"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    n = int(digest[:8], 16)
    hue = (n % 360) / 360.0
    sat = 0.6 + ((n >> 8) % 20) / 100.0
    val = 0.88 + ((n >> 16) % 12) / 100.0
    sat = min(0.85, max(0.45, sat))
    val = min(1.0, max(0.72, val))
    return _hsv_para_hex(hue, sat, val)

def _garantir_cor_visivel(hexcolor):
    c = (hexcolor or "#CFE8FF").lstrip("#")
    if len(c) != 6:
        return "#CFE8FF"
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    lum = (r*299 + g*587 + b*114) / 1000
    if lum > 245:
        r = max(0, int(r * 0.82))
        g = max(0, int(g * 0.82))
        b = max(0, int(b * 0.82))
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

def _cor_texto_contraste(hexcolor: str):
    c = (hexcolor or "#000000").lstrip("#")
    if len(c) != 6:
        return "#000000"
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 125 else "#FFFFFF"

def _truncar_texto(texto: str, fonte: tkfont.Font, largura_max: int):
    if largura_max <= 0:
        return "…"
    if fonte.measure(texto) <= largura_max:
        return texto
    ell = "..."
    low, high = 0, len(texto)
    while low < high:
        mid = (low + high + 1) // 2
        cand = texto[:mid] + ell
        if fonte.measure(cand) <= largura_max:
            low = mid
        else:
            high = mid - 1
    return (texto[:low] + ell) if low > 0 else "…"

# ---------------- View ----------------
class CronogramaView:
    def __init__(self, root, controller=None, manager=None):
        self.root = root
        for w in self.root.winfo_children():
            w.destroy()

        # controller
        self.exposicao_controller = controller if controller is not None else (ExposicaoController() if ExposicaoController else None)
        self.manager = manager

        self.root.title("Cronograma - Galeria")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.bg = "#F3F4F6"
        self.root.configure(bg=self.bg)

        # carregar exposições
        self.eventos = self._obter_eventos_do_db()

        # fontes e meta
        self.fonte_evento = tkfont.Font(family="Segoe UI", size=9)
        self.fonte_dia = tkfont.Font(family="Segoe UI", size=11)
        self.cell_meta = {}

        self.ano_exib = date.today().year
        self.mes_exib = date.today().month

        self.criar_interface()
        self.desenhar_calendario()
        self._bind_redimensionamento()

    def _obter_eventos_do_db(self):
        """Lê exposições do controller e converte para lista de eventos simples."""
        eventos = []
        if not self.exposicao_controller or not hasattr(self.exposicao_controller, "listar"):
            return eventos
        expos = self.exposicao_controller.listar() or []
        for ex in expos:
            nome = getattr(ex, "nome", None) or (ex.get("nome") if isinstance(ex, dict) else None)
            di_raw = getattr(ex, "data_inicio", None) or (ex.get("data_inicio") if isinstance(ex, dict) else None)
            df_raw = getattr(ex, "data_fim", None) or (ex.get("data_fim") if isinstance(ex, dict) else None)
            di = _parse_data_valida(di_raw)
            df = _parse_data_valida(df_raw)
            if di and not df:
                df = di
            if df and not di:
                di = df
            if not nome or not di or not df:
                continue
            cor = _garantir_cor_visivel(_cor_deterministica(nome, di, df))
            eventos.append({"titulo": nome, "inicio": di, "fim": df, "cor": cor})
        return eventos

    # ---------- Interface ----------
    def criar_interface(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TLabel", background=self.bg)
        style.configure("TFrame", background=self.bg)

        topo = ttk.Frame(self.root)
        topo.pack(fill="x", padx=10, pady=(10,6))

        titulo = tk.Label(topo, text="Cronograma", font=("Segoe UI", 16, "bold"), bg=self.bg, fg="#333")
        titulo.pack(side="left", padx=(6,0))

        self.var_mes = tk.StringVar(value=MESES_PT[self.mes_exib-1])
        self.combo_mes = ttk.Combobox(topo, values=MESES_PT, textvariable=self.var_mes, state="readonly", width=18)
        self.combo_mes.pack(side="left", padx=(20,4))
        self.combo_mes.bind("<<ComboboxSelected>>", lambda e: self._on_mes_trocado())

        anos = list(range(2000, 2041))
        self.var_ano = tk.IntVar(value=self.ano_exib)
        self.combo_ano = ttk.Combobox(topo, values=anos, textvariable=self.var_ano, state="readonly", width=6)
        self.combo_ano.pack(side="left", padx=(4,8))
        self.combo_ano.bind("<<ComboboxSelected>>", lambda e: self._on_ano_trocado())

        ttk.Button(topo, text="◀", width=3, command=self._mes_anterior).pack(side="left", padx=(8,2))
        ttk.Button(topo, text="▶", width=3, command=self._mes_seguinte).pack(side="left", padx=(2,6))
        ttk.Button(topo, text="Hoje", command=self.ir_para_hoje).pack(side="left", padx=(6,6))

        frame_home = tk.Frame(topo, bg=self.bg)
        frame_home.pack(side="right", padx=(0,6))
        tk.Button(frame_home, text="❌", font=("Segoe UI Emoji", 10), bd=0, highlightthickness=0,
                  padx=6, pady=2, bg=self.bg, activebackground="#ddd", cursor="hand2",
                  command=self.voltar_inicio).pack()

        # canvas
        card = ttk.Frame(self.root, padding=8)
        card.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.canvas = tk.Canvas(card, bg=self.bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._ao_clicar_canvas)

        rodape = ttk.Label(self.root, text="Clique em um dia para ver exposições.", background=self.bg)
        rodape.pack(fill="x", padx=12, pady=(0,8))

    # ---------- controles mês/ano ----------
    def _on_mes_trocado(self):
        v = self.combo_mes.get()
        if v in MESES_PT:
            self.mes_exib = MESES_PT.index(v) + 1
            self.desenhar_calendario()

    def _on_ano_trocado(self):
        try:
            self.ano_exib = int(self.combo_ano.get())
            self.desenhar_calendario()
        except Exception:
            pass

    def _mes_anterior(self):
        m = self.mes_exib - 1
        a = self.ano_exib
        if m < 1:
            m = 12
            a -= 1
        self.mes_exib, self.ano_exib = m, a
        self.var_mes.set(MESES_PT[self.mes_exib-1])
        self.var_ano.set(self.ano_exib)
        self.desenhar_calendario()

    def _mes_seguinte(self):
        m = self.mes_exib + 1
        a = self.ano_exib
        if m > 12:
            m = 1
            a += 1
        self.mes_exib, self.ano_exib = m, a
        self.var_mes.set(MESES_PT[self.mes_exib-1])
        self.var_ano.set(self.ano_exib)
        self.desenhar_calendario()

    def ir_para_hoje(self):
        t = date.today()
        self.ano_exib, self.mes_exib = t.year, t.month
        self.var_mes.set(MESES_PT[self.mes_exib-1])
        self.var_ano.set(self.ano_exib)
        self.desenhar_calendario()

    # ---------- desenho do calendário ----------
    def _bind_redimensionamento(self):
        self.root.bind("<Configure>", self._debounce_redesenho)
        self._resize_after_id = None

    def _debounce_redesenho(self, _ev):
        if getattr(self, "_resize_after_id", None):
            try:
                self.root.after_cancel(self._resize_after_id)
            except Exception:
                pass
        if getattr(self.root, "winfo_exists", lambda: 1)():
            self._resize_after_id = self.root.after(120, self._ao_redimensionado)

    def _ao_redimensionado(self):
        if not getattr(self.canvas, "winfo_exists", lambda: 0)():
            return
        self.desenhar_calendario()

    def desenhar_calendario(self):
        if not getattr(self.canvas, "winfo_exists", lambda: 0)():
            return
        self.canvas.delete("all")

        largura = max(700, self.canvas.winfo_width())
        altura = max(420, self.canvas.winfo_height())

        altura_header = 60
        altura_weekday = 30
        colunas = 7
        pad_esq, pad_dir, pad_top, pad_bot = 12, 12, 10, 12

        titulo = f"{MESES_PT[self.mes_exib-1]} {self.ano_exib}"
        self.canvas.create_text(int(largura//2), int(pad_top + altura_header//2), text=titulo, font=("Segoe UI", 16, "bold"))

        primeiro = date(self.ano_exib, self.mes_exib, 1)
        _, ndias = __import__("calendar").monthrange(self.ano_exib, self.mes_exib)
        inicio_sem = (primeiro.weekday() + 1) % 7  # domingo=0
        total_celulas = inicio_sem + ndias
        linhas = max(4, min(6, math.ceil(total_celulas / 7)))

        topo_grade = pad_top + altura_header
        altura_grade = altura - topo_grade - pad_bot
        cell_w = (largura - pad_esq - pad_dir) / colunas
        cell_h = (altura_grade - altura_weekday) / linhas

        # cabeçalho dias
        for c in range(colunas):
            x1 = pad_esq + c * cell_w
            y1 = topo_grade
            x2 = x1 + cell_w
            y2 = y1 + altura_weekday
            self.canvas.create_rectangle(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)), fill="#EEEEEE", outline="#D0D0D0")
            self.canvas.create_text(int(round((x1+x2)/2)), int(round((y1+y2)/2)), text=WEEKDAYS_PT[c], font=("Segoe UI", 10, "bold"))

        primeira_celula = primeiro - timedelta(days=inicio_sem)
        self.cell_meta = {}
        cur = primeira_celula
        for r in range(linhas):
            for c in range(colunas):
                x1 = pad_esq + c * cell_w
                y1 = topo_grade + altura_weekday + r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                ix1, iy1, ix2, iy2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
                is_hoje = (cur == date.today())
                fill = "#FFF5CC" if (cur.month == self.mes_exib and is_hoje) else ("white" if cur.month == self.mes_exib else "#F7F7F7")
                self.canvas.create_rectangle(ix1, iy1, ix2, iy2, fill=fill, outline="#DDDDDD")
                cor_dia = "#333333" if cur.month == self.mes_exib else "#B5B5B5"
                self.canvas.create_text(ix1 + 8, iy1 + 10, anchor="nw", text=str(cur.day), font=self.fonte_dia, fill=cor_dia)
                self.cell_meta[cur] = {"bbox": (ix1, iy1, ix2, iy2), "row": r, "col": c}
                cur += timedelta(days=1)

        if not self.eventos:
            self.canvas.create_text(int(largura//2), int(topo_grade + altura_weekday + altura_grade/2), text="Nenhuma exposição cadastrada.", font=("Segoe UI", 12), fill="#666")
            return

        self._desenhar_eventos(cell_w, cell_h)

    def _desenhar_eventos(self, cell_w, cell_h):
        dates_displayed = sorted(self.cell_meta.keys())
        if not dates_displayed:
            return

        data_para_eventos = {d: [] for d in dates_displayed}
        for idx, ev in enumerate(self.eventos):
            s, e = ev["inicio"], ev["fim"]
            if not s or not e:
                continue
            for i in range((e - s).days + 1):
                d = s + timedelta(days=i)
                if d in data_para_eventos:
                    data_para_eventos[d].append(idx)

        # lane assignment global
        lane_por_evento = {}
        usado = {d: set() for d in dates_displayed}
        order = sorted(range(len(self.eventos)), key=lambda i: (self.eventos[i]["inicio"], self.eventos[i]["titulo"]))
        for i in order:
            ev = self.eventos[i]
            s, e = ev["inicio"], ev["fim"]
            cobertos = [d for d in dates_displayed if s <= d <= e]
            if not cobertos:
                continue
            lane = 0
            while any(lane in usado[d] for d in cobertos):
                lane += 1
            for d in cobertos:
                usado[d].add(lane)
            lane_por_evento[i] = lane

        # row -> datas
        rows = {}
        for d, meta in self.cell_meta.items():
            rows.setdefault(meta["row"], []).append(d)
        for r in rows:
            rows[r].sort()

        reservado_top = 28
        gap_padrao = 4
        alturas_por_row = {}
        offsets_por_row = {}

        for r, datas in rows.items():
            necessario = max((len(data_para_eventos.get(d, [])) for d in datas), default=0)
            max_idx = -1
            for d in datas:
                if usado.get(d):
                    max_idx = max(max_idx, max(usado[d]))
            if max_idx >= 0:
                necessario = max(necessario, max_idx + 1)
            if necessario <= 0:
                alturas_por_row[r] = []
                offsets_por_row[r] = []
                continue

            efetivos = max(2, necessario)
            disponivel_vertical = max(0, int(cell_h) - reservado_top - 4)
            gap_lane = gap_padrao if disponivel_vertical / efetivos >= 12 else 2
            disponivel_para_lanes = max(0, disponivel_vertical - (efetivos - 1) * gap_lane)
            altura_fonte = max(10, self.fonte_evento.metrics("linespace"))
            min_lane_h = max(10, altura_fonte + 4)

            if disponivel_para_lanes <= 0:
                base, resto = 1, 0
            else:
                if disponivel_para_lanes >= min_lane_h * efetivos:
                    base = disponivel_para_lanes // efetivos
                    resto = disponivel_para_lanes % efetivos
                else:
                    base = max(1, disponivel_para_lanes // efetivos)
                    resto = disponivel_para_lanes - base * efetivos

            alturas = [(base + (1 if idx < resto else 0)) for idx in range(efetivos)]
            offsets = []
            cum = 0
            for idx, h in enumerate(alturas):
                offsets.append(cum)
                cum += h
                if idx < efetivos - 1:
                    cum += gap_lane
            alturas_por_row[r] = alturas
            offsets_por_row[r] = offsets

        eventos_por_lane = {}
        for i, lane in lane_por_evento.items():
            eventos_por_lane.setdefault(lane, []).append(i)
        for lane in sorted(eventos_por_lane.keys()):
            for i in sorted(eventos_por_lane[lane], key=lambda k: (self.eventos[k]["inicio"], self.eventos[k]["titulo"])):
                ev = self.eventos[i]
                s, e = ev["inicio"], ev["fim"]
                cor = ev.get("cor", "#CFE8FF")
                todas_datas = [s + timedelta(days=d) for d in range((e - s).days + 1)]
                cobertos = [d for d in todas_datas if d in self.cell_meta]
                if not cobertos:
                    continue
                agrup = {}
                for d in cobertos:
                    r = self.cell_meta[d]["row"]
                    agrup.setdefault(r, []).append(d)
                for r in sorted(agrup.keys()):
                    dias = sorted(agrup[r])
                    primeiro, ultimo = dias[0], dias[-1]
                    bbox_p = self.cell_meta[primeiro]["bbox"]
                    bbox_u = self.cell_meta[ultimo]["bbox"]
                    x1, x2 = bbox_p[0], bbox_u[2]
                    rx1, rx2 = int(round(x1)) - 1, int(round(x2)) + 1

                    alturas = alturas_por_row.get(r, [])
                    offsets = offsets_por_row.get(r, [])
                    if not alturas or lane >= len(alturas):
                        topo_cel = self.cell_meta[primeiro]["bbox"][1]
                        ry1 = int(topo_cel + reservado_top + lane * 12)
                        ry2 = ry1 + 10
                    else:
                        topo_cel = self.cell_meta[primeiro]["bbox"][1]
                        ry1 = int(topo_cel + reservado_top + offsets[lane])
                        ry2 = ry1 + int(alturas[lane])

                    cell_bottom = self.cell_meta[primeiro]["bbox"][3]
                    if ry2 > cell_bottom - 2:
                        ry2 = cell_bottom - 2
                        if ry1 >= ry2:
                            ry1 = max(self.cell_meta[primeiro]["bbox"][1] + reservado_top, ry2 - 4)

                    self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill=cor, outline=cor, width=1, tags=(f"evt_ret_{i}_{r}",))
                    padding = 6
                    largura_disp = max(0, (rx2 - rx1) - padding*2)
                    texto = _truncar_texto(ev.get("titulo", ""), self.fonte_evento, largura_disp)
                    cor_txt = _cor_texto_contraste(cor)
                    yc = int((ry1 + ry2) / 2)
                    self.canvas.create_text(int((rx1 + rx2) / 2), yc, text=texto, font=self.fonte_evento, fill=cor_txt, tags=(f"evt_txt_{i}_{r}",))
                    handler = self._criar_handler_evento()
                    self.canvas.tag_bind(f"evt_ret_{i}_{r}", "<Button-1>", handler)
                    self.canvas.tag_bind(f"evt_txt_{i}_{r}", "<Button-1>", handler)

    def _criar_handler_evento(self):
        def handler(tk_event):
            x, y = tk_event.x, tk_event.y
            for d, meta in self.cell_meta.items():
                x1, y1, x2, y2 = meta["bbox"]
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.mostrar_eventos_no_dia(d)
                    return
        return handler

    def _ao_clicar_canvas(self, tk_event):
        x, y = tk_event.x, tk_event.y
        itens = self.canvas.find_overlapping(x, y, x, y)
        for it in itens:
            tags = self.canvas.gettags(it)
            if any(t.startswith("evt_") for t in tags):
                return
        for d, meta in self.cell_meta.items():
            x1,y1,x2,y2 = meta["bbox"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.mostrar_eventos_no_dia(d)
                return

    def mostrar_eventos_no_dia(self, d):
        evs = [ev for ev in self.eventos if ev["inicio"] <= d <= ev["fim"]]
        if not evs:
            messagebox.showinfo(f"Dia {d.strftime('%d/%m/%Y')}", "Nenhuma exposição neste dia.")
            return
        linhas = [f"- {ev['titulo']} ({ev['inicio'].strftime('%d/%m/%Y')} → {ev['fim'].strftime('%d/%m/%Y')})" for ev in evs]
        messagebox.showinfo(f"Exposições em {d.strftime('%d/%m/%Y')}", "\n".join(linhas))

    def voltar_inicio(self):
        try:
            from src.views.tela_inicial_view import TelaInicial
        except Exception:
            messagebox.showerror("Erro", "Não foi possível voltar à tela inicial (import).")
            return
        for w in self.root.winfo_children():
            w.destroy()
        TelaInicial(self.root, self.manager)

if __name__ == "__main__":
    root = tk.Tk()
    CronogramaView(root)
    root.mainloop()
