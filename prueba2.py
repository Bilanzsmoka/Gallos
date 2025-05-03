import tkinter as tk
from UI.app_gallos import AppGallos
from db.gallos_db import GallosDB

if __name__ == "__main__":
    db = GallosDB()
    root = tk.Tk()
    app = AppGallos(root, db)
    root.mainloop()
