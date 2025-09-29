import sqlite3

DB_FILE = "src/database/galeria_arte.db"  # ajuste o caminho se o seu manager usa outro

def listar_todos():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM Artistas")
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    artistas = listar_todos()
    print("=== ARTISTAS CADASTRADOS ===")
    for row in artistas:
        print(row)
    print(f"Total: {len(artistas)} registros")
