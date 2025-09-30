import sqlite3
import os
from datetime import datetime, date
from contextlib import contextmanager
from typing import Optional
from src.models.obra_model import ObraDeArte, StatusObra
from src.models.artista_model import Artista, StatusArtista
from src.models.transacao_model import Transacao


class DatabaseManager:
    def __init__(self, db_file: Optional[str] = None):
        if db_file is None:
            db_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_file = os.path.join(db_dir, "galeria_arte.db")
        else:
            self.db_file = db_file

        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self._criar_tabelas()

    def conectar(self):
        """Cria conexão com row_factory para acesso por nome de coluna."""
        con = sqlite3.connect(self.db_file)
        con.row_factory = sqlite3.Row
        return con

    @contextmanager
    def cursor(self):
        """Context manager que fornece um cursor e commita no final."""
        con = self.conectar()
        cur = con.cursor()
        try:
            yield cur
            con.commit()
        finally:
            con.close()

    # ---------------------- CRIAÇÃO DAS TABELAS ----------------------
    def _criar_tabelas(self):
        with self.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS obras (
                    id_obra INTEGER PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    nome_artista TEXT NOT NULL,
                    ano INTEGER,
                    tipo TEXT NOT NULL,
                    tecnica TEXT,
                    dimensoes TEXT,
                    localizacao TEXT,
                    preco REAL,
                    status TEXT NOT NULL,
                    imagem BLOB,
                    data_cadastro TEXT
                )
            ''')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artistas (
                    id_artista     INTEGER PRIMARY KEY,
                    nome           TEXT NOT NULL,
                    nascimento     TEXT NOT NULL,
                    nacionalidade  TEXT NOT NULL,
                    especialidade  TEXT NOT NULL,
                    status         TEXT NOT NULL,
                    data_cadastro  TEXT NOT NULL,
                    biografia      TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente TEXT NOT NULL,
                    valor REAL NOT NULL,
                    tipo TEXT NOT NULL,
                    data_transacao TEXT NOT NULL,
                    data_cadastro TEXT NOT NULL,
                    observacoes TEXT,
                    obras TEXT
                )
            """)

    # ---------------------- MÉTODOS OBRAS ----------------------
    def get_next_obra_id(self) -> int:
        with self.conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT max(id_obra) FROM obras")
            resultado = cur.fetchone()[0]
        return 1 if resultado is None else resultado + 1

    def inserir_obra(self, obra: ObraDeArte) -> None:
        sql = '''
            INSERT INTO obras (id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        data_cad = obra.data_cadastro.isoformat() if hasattr(obra.data_cadastro, "isoformat") else obra.data_cadastro
        valores = (
            obra.id_obra,
            obra.titulo,
            obra.ano,
            obra.artista,
            obra.tipo,
            obra.tecnica,
            obra.dimensoes,
            obra.localizacao,
            obra.preco,
            obra.status.value,
            obra.imagem,
            data_cad
        )
        with self.cursor() as cursor:
            cursor.execute(sql, valores)

    def listar_todas_obras(self) -> list[ObraDeArte]:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem, data_cadastro
                FROM obras ORDER BY id_obra
            ''')
            rows = cursor.fetchall()
        return [self._criar_objeto_obra(r) for r in rows]

    def buscar_obra_por_id(self, obra_id: int) -> Optional[ObraDeArte]:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem, data_cadastro
                FROM obras WHERE id_obra = ?
            ''', (obra_id,))
            row = cursor.fetchone()
        if row:
            return self._criar_objeto_obra(row)
        return None

    def atualizar_obra(self, obra: ObraDeArte) -> None:
        sql = '''
            UPDATE obras SET
                titulo = ?, ano = ?, nome_artista = ?, tipo = ?, tecnica = ?,
                dimensoes = ?, localizacao = ?, preco = ?, status = ?, imagem = ?
            WHERE id_obra = ?
        '''
        valores = (
            obra.titulo, obra.ano, obra.artista, obra.tipo, obra.tecnica,
            obra.dimensoes, obra.localizacao, obra.preco, obra.status.value,
            obra.imagem, obra.id_obra
        )
        with self.cursor() as cursor:
            cursor.execute(sql, valores)

    def verificar_obra_existe(self, titulo: str, artista: str, ano: int) -> bool:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute('''
                SELECT count(*) FROM obras
                WHERE titulo = ? AND nome_artista = ? AND ano = ?
            ''', (titulo, artista, ano))
            resultado = cursor.fetchone()[0]
        return resultado > 0

    def _criar_objeto_obra(self, row) -> ObraDeArte:
        def _get(k, i):
            if isinstance(row, sqlite3.Row):
                return row[k]
            return row[i]

        id_obra = _get("id_obra", 0)
        titulo = _get("titulo", 1)
        ano = _get("ano", 2)
        nome_artista = _get("nome_artista", 3)
        tipo = _get("tipo", 4)
        tecnica = _get("tecnica", 5)
        dimensoes = _get("dimensoes", 6)
        localizacao = _get("localizacao", 7)
        preco = _get("preco", 8)
        status_str = _get("status", 9)
        imagem = _get("imagem", 10)
        data_cadastro_str = _get("data_cadastro", 11)

        status_enum = next((s for s in StatusObra if s.value == status_str), StatusObra.DISPONIVEL)

        data_cadastro = None
        if data_cadastro_str:
            try:
                data_cadastro = datetime.fromisoformat(data_cadastro_str).date()
            except Exception:
                try:
                    data_cadastro = date.fromisoformat(data_cadastro_str)
                except Exception:
                    data_cadastro = None

        return ObraDeArte(
            id_obra=id_obra,
            titulo=titulo,
            ano=ano,
            artista=nome_artista,
            tipo=tipo,
            tecnica=tecnica,
            dimensoes=dimensoes,
            localizacao=localizacao,
            preco=preco,
            status=status_enum,
            imagem=imagem,
            data_cadastro=data_cadastro
        )

    # ---------------------- MÉTODOS TRANSAÇÕES ----------------------
    def inserir_transacao(self, transacao: Transacao) -> int:
        sql = '''
            INSERT INTO transacoes
            (cliente, valor, tipo, data_transacao, data_cadastro, observacoes, obras)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        data_transacao = transacao.data_transacao.isoformat() if hasattr(transacao.data_transacao, "isoformat") else transacao.data_transacao
        data_cadastro = transacao.data_cadastro.isoformat() if hasattr(transacao.data_cadastro, "isoformat") else transacao.data_cadastro
        obras_csv = ",".join(map(str, transacao.obras)) if transacao.obras is not None else None

        with self.cursor() as cursor:
            cursor.execute(sql, (
                transacao.cliente,
                transacao.valor,
                transacao.tipo,
                data_transacao,
                data_cadastro,
                transacao.observacoes,
                obras_csv
            ))
            return cursor.lastrowid

    def listar_transacoes(self) -> list[Transacao]:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM transacoes ORDER BY id DESC")
            rows = cursor.fetchall()
        return [self._row_to_transacao(r) for r in rows]

    def buscar_transacao_por_id(self, transacao_id: int) -> Optional[Transacao]:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM transacoes WHERE id = ?", (transacao_id,))
            row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_transacao(row)

    def atualizar_transacao(self, transacao: Transacao) -> None:
        sql = """
            UPDATE transacoes
            SET cliente=?, valor=?, tipo=?, data_transacao=?, data_cadastro=?, observacoes=?, obras=?
            WHERE id=?
        """
        data_transacao = transacao.data_transacao.isoformat() if hasattr(transacao.data_transacao, "isoformat") else transacao.data_transacao
        data_cadastro = transacao.data_cadastro.isoformat() if hasattr(transacao.data_cadastro, "isoformat") else transacao.data_cadastro
        obras_csv = ",".join(map(str, transacao.obras)) if transacao.obras is not None else None
        trans_id = getattr(transacao, "id", None) or getattr(transacao, "id_", None)

        with self.cursor() as cursor:
            cursor.execute(sql, (
                transacao.cliente,
                transacao.valor,
                transacao.tipo,
                data_transacao,
                data_cadastro,
                transacao.observacoes,
                obras_csv,
                trans_id
            ))

    def get_next_transacao_id(self) -> int:
        with self.conectar() as con:
            cur = con.cursor()
            cur.execute("SELECT max(id) FROM transacoes")
            resultado = cur.fetchone()[0]
        return 1 if resultado is None else resultado + 1

    def verificar_transacao_existe(self, cliente: str, data_transacao: date, valor: float) -> bool:
        data_iso = data_transacao.isoformat() if hasattr(data_transacao, "isoformat") else data_transacao
        with self.conectar() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT count(*) FROM transacoes
                WHERE cliente = ? AND data_transacao = ? AND valor = ?
            """, (cliente, data_iso, valor))
            resultado = cur.fetchone()[0]
        return resultado > 0

    def buscar_transacoes(self, filtros: dict) -> list[Transacao]:
        where, params = [], []

        if filtros.get("cliente"):
            where.append("cliente LIKE ?")
            params.append(f"%{filtros['cliente']}%")
        if filtros.get("tipo"):
            where.append("tipo = ?")
            params.append(filtros["tipo"])
        if filtros.get("data_transacao_from"):
            dt = filtros["data_transacao_from"]
            dt_iso = dt.isoformat() if hasattr(dt, "isoformat") else dt
            where.append("data_transacao >= ?")
            params.append(dt_iso)
        if filtros.get("data_transacao_to"):
            dt = filtros["data_transacao_to"]
            dt_iso = dt.isoformat() if hasattr(dt, "isoformat") else dt
            where.append("data_transacao <= ?")
            params.append(dt_iso)

        sql = "SELECT * FROM transacoes"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC"

        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        return [self._row_to_transacao(r) for r in rows]

    def _row_to_transacao(self, row) -> Optional[Transacao]:
        if row is None:
            return None

        # Extraindo campos do row (sqlite3.Row ou tupla)
        def get_value(col_name, index):
            if isinstance(row, sqlite3.Row):
                return row[col_name]
            return row[index]

        id_ = get_value("id", 0)
        cliente = get_value("cliente", 1)
        valor = get_value("valor", 2)
        tipo = get_value("tipo", 3)
        data_transacao_str = get_value("data_transacao", 4)
        data_cadastro_str = get_value("data_cadastro", 5)
        observacoes = get_value("observacoes", 6)
        obras_str = get_value("obras", 7)

        # Parse obras CSV -> lista de strings
        obras = []
        if obras_str:
            obras = [x.strip() for x in obras_str.split(",") if x.strip() != ""]

        # Parse datas para datetime
        data_transacao_dt = None
        data_cadastro_dt = None

        if data_transacao_str:
            try:
                data_transacao_dt = datetime.fromisoformat(data_transacao_str)
            except ValueError:
                try:
                    data_transacao_dt = datetime.strptime(data_transacao_str, "%d/%m/%Y")
                except Exception:
                    data_transacao_dt = None

        if data_cadastro_str:
            try:
                data_cadastro_dt = datetime.fromisoformat(data_cadastro_str)
            except ValueError:
                try:
                    data_cadastro_dt = datetime.strptime(data_cadastro_str, "%d/%m/%Y")
                except Exception:
                    data_cadastro_dt = None

        # Converte datas para string DD/MM/YYYY
        data_transacao_fmt = data_transacao_dt.strftime("%d/%m/%Y") if data_transacao_dt else None
        data_cadastro_fmt = data_cadastro_dt.strftime("%d/%m/%Y") if data_cadastro_dt else None

        # Cria objeto Transacao
        trans = Transacao(
            cliente=cliente,
            valor=valor,
            tipo=tipo,
            data_transacao=data_transacao_fmt,
            data_cadastro=data_cadastro_fmt,
            observacoes=observacoes,
            obras=obras
        )

        # Atribui o ID
        trans._Transacao__id = id_

        return trans
    
    def get_status_obra_por_titulo(self, titulo: str) -> str:
        """Retorna o status atual da obra pelo título."""
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT status FROM obras WHERE titulo = ?", (titulo,))
            row = cursor.fetchone()
        return row["status"] if row else None

    def atualizar_status_obra_por_titulo(self, titulo: str, novo_status: str) -> None:
        """Atualiza o status da obra pelo título."""
        with self.cursor() as cursor:
            cursor.execute("UPDATE obras SET status = ? WHERE titulo = ?", (novo_status, titulo))

    # ---------------------- MÉTODOS ARTISTA ----------------------
    def _row_to_artista(self, row) -> Optional[Artista]:
        if not row:
            return None

        if isinstance(row, sqlite3.Row):
            id_artista = row["id_artista"] if "id_artista" in row.keys() else row.get("id")
            nome = row["nome"]
            nascimento = row["nascimento"] if "nascimento" in row.keys() else row.get("nascimento")
            nacionalidade = row["nacionalidade"] if "nacionalidade" in row.keys() else row.get("nacionalidade")
            especialidade = row["especialidade"] if "especialidade" in row.keys() else row.get("especialidade")
            status_str = row["status"] if "status" in row.keys() else row.get("status")
            data_cadastro = row["data_cadastro"] if "data_cadastro" in row.keys() else row.get("datacadastro")
            biografia = row["biografia"] if "biografia" in row.keys() else row.get("biografia")
        else:
            id_artista, nome, nascimento, nacionalidade, especialidade, status_str, data_cadastro, biografia = row

        status_enum = StatusArtista.ATIVO if status_str == "Ativo" else StatusArtista.INATIVO

        return Artista(
            id_artista=id_artista,
            nome=nome,
            nascimento=nascimento,
            nacionalidade=nacionalidade,
            especialidade=especialidade,
            status=status_enum,
            data_cadastro=data_cadastro,
            biografia=biografia
        )

    def inserir_artista(self, artista: Artista) -> int:
        sql = """
            INSERT INTO artistas
                (nome, nascimento, nacionalidade, especialidade, status, data_cadastro, biografia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        status_val = artista.status.value if hasattr(artista.status, "value") else artista.status
        with self.cursor() as cursor:
            cursor.execute(sql, (
                artista.nome,
                artista.nascimento,
                artista.nacionalidade,
                artista.especialidade,
                status_val,
                artista.data_cadastro,
                artista.biografia
            ))
            return cursor.lastrowid

    def atualizar_artista(self, artista: Artista) -> None:
        sql = """
            UPDATE artistas
            SET nome=?, nascimento=?, nacionalidade=?, especialidade=?,
                status=?, data_cadastro=?, biografia=?
            WHERE id_artista=?
        """
        status_val = artista.status.value if hasattr(artista.status, "value") else artista.status
        with self.cursor() as cursor:
            cursor.execute(sql, (
                artista.nome,
                artista.nascimento,
                artista.nacionalidade,
                artista.especialidade,
                status_val,
                artista.data_cadastro,
                artista.biografia,
                artista.id_artista
            ))

    def obter_artista(self, id_artista: int) -> Optional[Artista]:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM artistas WHERE id_artista = ?", (id_artista,))
            row = cursor.fetchone()
        return self._row_to_artista(row)

    def listar_artistas(self) -> list[Artista]:
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM artistas ORDER BY nome")
            rows = cursor.fetchall()
        return [self._row_to_artista(r) for r in rows]

    def buscar_artistas(self, filtros: dict) -> list[Artista]:
        where, params = [], []

        def like(campo, valor):
            if valor:
                where.append(f"{campo} LIKE ?")
                params.append(f"%{valor}%")

        like("nome", filtros.get("nome"))
        like("nascimento", filtros.get("nascimento"))
        like("nacionalidade", filtros.get("nacionalidade"))
        like("especialidade", filtros.get("especialidade"))
        like("data_cadastro", filtros.get("data_cadastro"))

        status = (filtros.get("status") or "").strip()
        if status:
            where.append("status = ?")
            params.append(status)

        sql = "SELECT * FROM artistas"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY nome"

        with self.conectar() as con:
            c = con.cursor()
            c.execute(sql, tuple(params))
            rows = c.fetchall()
        return [self._row_to_artista(r) for r in rows]


db = DatabaseManager()
