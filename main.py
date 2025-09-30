import tkinter as tk
from src.database.manager import DatabaseManager
from src.views.tela_inicial_view import TelaInicial

def main():
    db_manager = DatabaseManager()
    root = tk.Tk()
    app = TelaInicial(root, db_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
