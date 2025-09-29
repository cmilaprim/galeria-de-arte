import sqlite3
import os
from datetime import datetime
from ..models.obra_model import ObraDeArte, StatusObra
from ..models.artista_model import Artista, StatusArtista

class DatabaseManager:
    def __init__(self, db_file=None):
        if db_file is None:
            db_dir = os.path.dirname(os.path.abspath(__file__))  # Pasta atual (database)
            self.db_file = os.path.join(db_dir, 'galeria_arte.db')
        else:
            self.db_file = db_file
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        # criando as tabelas
        self.criar_tabela_obras()
        self.criar_tabela_artistas()
    
    # ---------------- OBRAS ---------------- #
    def criar_tabela_obras(self):
        """Cria a tabela"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        create table if not exists Obras (
            id_obra integer primary key,
            titulo text not null,
            ano integer,
            nome_artista text not null,
            tipo text not null,
            tecnica text,
            dimensoes text,
            localizacao text,
            preco real,
            status text not null,
            imagem blob,
            data_cadastro text
        )
        ''')
        conn.commit()
        conn.close()
    
    def get_next_obra_id(self):
        """retorna o próximo ID disponível"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("select max(id_obra) from obras")
        resultado = cursor.fetchone()[0]
        
        conn.close()
        return 1 if resultado is None else resultado + 1
    
    def inserir_obra(self, obra):
        """insere uma nova obra no banco"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        insert into obras (id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem, data_cadastro)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', 
        (obra.id_obra, obra.titulo, obra.ano, obra.artista, obra.tipo, 
        obra.tecnica, obra.dimensoes, obra.localizacao, obra.preco, 
        obra.status.value, obra.imagem, obra.data_cadastro.isoformat()))
        
        conn.commit()
        conn.close()
    
    def listar_todas_obras(self):
        """lista todas as obras"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        select id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem, data_cadastro
        from obras order by id_obra
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        
        obras = []
        for resultado in resultados:
            obra = self._criar_objeto_obra(resultado)
            obras.append(obra)
        
        return obras
    
    def buscar_obra_por_id(self, obra_id):
        """busca uma obra pelo ID"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        select id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, localizacao, preco, status, imagem, data_cadastro 
        from obras where id_obra = ?
        ''', (obra_id,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            return self._criar_objeto_obra(resultado)
        return None
    
    def atualizar_obra(self, obra):
        """atualiza uma obra existente"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        update obras set 
            titulo = ?, ano = ?, nome_artista = ?, tipo = ?, tecnica = ?, 
            dimensoes = ?, localizacao = ?, preco = ?, status = ?, imagem = ?
        where id_obra = ?
        ''', (obra.titulo, obra.ano, obra.artista, obra.tipo, obra.tecnica, 
              obra.dimensoes, obra.localizacao, obra.preco, obra.status.value, 
              obra.imagem, obra.id_obra))
        
        conn.commit()
        conn.close()
    
    def verificar_obra_existe(self, titulo, artista, ano):
        """verifica se obra já existe (previne duplicatas)"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        select count(*) from obras 
        where titulo = ? and nome_artista = ? and ano = ?
        ''', (titulo, artista, ano))
        
        resultado = cursor.fetchone()[0]
        conn.close()
        
        return resultado > 0
    
    
    def _criar_objeto_obra(self, resultado):
        """cria objeto ObraDeArte a partir do resultado SQL"""
        id_obra, titulo, ano, nome_artista, tipo, tecnica, dimensoes, \
        localizacao, preco, status_str, imagem, data_cadastro_str = resultado
        
        status_enum = next((s for s in StatusObra if s.value == status_str), StatusObra.DISPONIVEL)
        data_cadastro = datetime.fromisoformat(data_cadastro_str).date() if data_cadastro_str else None
        
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

    # ========== BEGIN ARTISTAS ========== #
    def criar_tabela_artistas(self):
        """Cria a tabela de Artistas uma única vez (idempotente)."""
        import sqlite3
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS Artistas (
                id_artista     INTEGER PRIMARY KEY,
                nome           TEXT NOT NULL,
                nascimento     TEXT NOT NULL,        -- DD/MM/YYYY
                nacionalidade  TEXT NOT NULL,
                especialidade  TEXT NOT NULL,
                status         TEXT NOT NULL,        -- 'Ativo' | 'Inativo'
                data_cadastro  TEXT NOT NULL,        -- DD/MM/YYYY
                biografia      TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def _row_to_artista(self, row):
        """Converte uma tupla do SQLite em objeto Artista."""
        if not row:
            return None
        (id_artista, nome, nasc, nac, esp, status_str, data_cad, bio) = row
        status_enum = StatusArtista.ATIVO if status_str == "Ativo" else StatusArtista.INATIVO
        return Artista(
            id_artista=id_artista,
            nome=nome,
            nascimento=nasc,
            nacionalidade=nac,
            especialidade=esp,
            status=status_enum,
            data_cadastro=data_cad,
            biografia=bio
        )

    def inserir_artista(self, artista: Artista) -> int:
        """Insere e retorna o ID gerado."""
        import sqlite3
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""
            INSERT INTO Artistas
                (nome, nascimento, nacionalidade, especialidade, status, data_cadastro, biografia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            artista.nome,
            artista.nascimento,
            artista.nacionalidade,
            artista.especialidade,
            artista.status.value,
            artista.data_cadastro,
            artista.biografia
        ))
        conn.commit()
        new_id = c.lastrowid
        conn.close()
        return new_id

    def atualizar_artista(self, artista: Artista) -> None:
        """Atualiza todos os campos (exceto PK)."""
        import sqlite3
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""
            UPDATE Artistas
            SET nome=?, nascimento=?, nacionalidade=?, especialidade=?,
                status=?, data_cadastro=?, biografia=?
            WHERE id_artista=?
        """, (
            artista.nome,
            artista.nascimento,
            artista.nacionalidade,
            artista.especialidade,
            artista.status.value,
            artista.data_cadastro,
            artista.biografia,
            artista.id_artista
        ))
        conn.commit()
        conn.close()

    def obter_artista(self, id_artista: int):
        """Busca 1 artista pelo ID."""
        import sqlite3
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM Artistas WHERE id_artista=?", (id_artista,))
        row = c.fetchone()
        conn.close()
        return self._row_to_artista(row)

    def listar_artistas(self):
        """Lista TODOS os artistas (ativos e inativos)."""
        import sqlite3
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM Artistas ORDER BY nome")
        rows = c.fetchall()
        conn.close()
        return [self._row_to_artista(r) for r in rows]

    def buscar_artistas(self, filtros: dict):
        """
        Busca por múltiplos campos. Só filtra pelos campos preenchidos:
        nome, nascimento, nacionalidade, especialidade, status, data_cadastro.
        Usa LIKE para textos e igualdade para status.
        """
        import sqlite3
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

        sql = "SELECT * FROM Artistas"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY nome"

        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute(sql, tuple(params))
        rows = c.fetchall()
        conn.close()
        return [self._row_to_artista(r) for r in rows]

    # ========== END ARTISTAS ========== #
