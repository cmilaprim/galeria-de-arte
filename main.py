import tkinter as tk
from database.manager import DatabaseManager
from views.tela_inicial_view import TelaInicial

def main():
    db_manager = DatabaseManager()
    root = tk.Tk()
    app = TelaInicial(root, db_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
