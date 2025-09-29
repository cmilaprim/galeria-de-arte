from src.views.artista_view import ArtistaView
from src.views.obra_view import ObraView
import tkinter as tk
from tkinter import ttk

def main_menu():
    root = tk.Tk()
    root.title("Galeria de Arte – Módulos")

    def abre_artistas():
        root.destroy()
        ArtistaView().run()

    def abre_obras():
        root.destroy()
        ObraView().run()

    ttk.Button(root, text="Módulo: Artistas", command=abre_artistas).pack(padx=20,pady=10)
    ttk.Button(root, text="Módulo: Obras", command=abre_obras).pack(padx=20,pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()