import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db.gallos_db import GallosDB
from UI.torneo_view import TorneoView 
from UI.sorteo_view import SorteoView


class AppGallos:
    def __init__(self, root, db: GallosDB):
        self.root = root
        self.db = db
        self.root.title("Gestor de Torneos de Gallos")
        self.root.geometry("900x650")

        self.entries = {}
        self.fields = self.obtener_campos()
        self.resultados_pelea = []
        self.peleas_manuales = []

        self.crear_widgets()
        self.actualizar_tabla()
        self.actualizar_lista_cuerdas()

    def obtener_campos(self):
        self.db.cursor.execute("PRAGMA table_info(gallos);")
        return [col[1] for col in self.db.cursor.fetchall()]

    def crear_widgets(self):
        tk.Label(self.root, text="SOFTWARE\nTORNEO DE GALLOS MYN", font=("Arial", 16, "bold")).pack(pady=10)

        self.frame_principal = tk.Frame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.frame_imagen = tk.Frame(self.frame_principal)
        self.frame_imagen.pack(side=tk.RIGHT, padx=20, pady=10)

        self.cargar_logo()

        self.frame_form = tk.Frame(self.frame_principal)
        self.frame_form.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.crear_formulario()
        self.crear_botones()
        self.crear_tabla()

    def cargar_logo(self):
        try:
            imagen = Image.open("logo.png")
            imagen = imagen.resize((250, 250))
            self.logo = ImageTk.PhotoImage(imagen)
            tk.Label(self.frame_imagen, image=self.logo).pack()
        except FileNotFoundError:
            tk.Label(self.frame_imagen, text="Logo no encontrado", width=25, height=10, relief="solid").pack()

    def crear_formulario(self):
        tipo_frame = tk.Frame(self.frame_form)
        tipo_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(tipo_frame, text="Tipo:", width=10, anchor="w").pack(side=tk.LEFT)
        self.tipo_combo = ttk.Combobox(tipo_frame, values=["Gallo", "Pollo"], state="readonly")
        self.tipo_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.entries["tipo"] = self.tipo_combo
        
        for field in self.fields:
            if field in ["tipo", "id"]:
                continue
            frame = tk.Frame(self.frame_form)
            frame.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(frame, text=f"{field}:", width=10, anchor="w").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            self.entries[field] = entry

        self.cuerda_combo = ttk.Combobox(self.root, state="readonly")
        self.cuerda_combo.pack(pady=10)

    def crear_botones(self):
        frame_botones = tk.Frame(self.frame_form)
        frame_botones.pack(pady=10)

        botones = [
            ("Registrar Gallo", self.registrar_gallo),
            ("Modificar Gallo", self.modificar_gallo),
            ("Eliminar Gallo", self.eliminar_gallo),
            ("Eliminar Todos", self.eliminar_todos),
            ("Generar PDF", self.generar_pdf),
            ("Realizar Sorteo", self.realizar_sorteo),
            ("Exportar a Excel", self.exportar_excel),
            ("Iniciar Torneo", self.abrir_ventana_torneo)
        ]

        for i, (texto, comando) in enumerate(botones):
            tk.Button(frame_botones, text=texto, command=comando, width=20).grid(row=i//2, column=i%2, padx=5, pady=2)

    def crear_tabla(self):
        columnas = self.fields
        self.tabla = ttk.Treeview(self.root, columns=columnas, show="headings")
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100)
        self.tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tabla.bind("<<TreeviewSelect>>", self.rellenar_campos)

    def actualizar_tabla(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        self.db.cursor.execute("SELECT * FROM gallos")
        for row in self.db.cursor.fetchall():
            self.tabla.insert("", "end", values=row)

    def actualizar_lista_cuerdas(self):
        self.db.cursor.execute("SELECT DISTINCT cuerda FROM gallos")
        cuerdas = [row[0] for row in self.db.cursor.fetchall()]
        self.cuerda_combo['values'] = cuerdas

    def limpiar_campos(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)
    def obtener_todos_los_gallos(self):
        self.db.cursor.execute("SELECT * FROM gallos")
        cols = [desc[0] for desc in self.db.cursor.description]
        print(cols)
        return [dict(zip(cols, row)) for row in self.db.cursor.fetchall()]

    def registrar_gallo(self):
        tipo = self.entries["tipo"].get().strip()
        campos_vacios = []

        datos = []
        for field in self.fields:
            if field == "id":
                continue
            valor = self.entries[field].get().strip()
            datos.append(valor)
            if not valor:
                campos_vacios.append(field)

        if not tipo:
            campos_vacios.append("tipo")

        if campos_vacios:
            campos_str = ", ".join(campos_vacios)
            messagebox.showwarning("Advertencia", f"Por favor, completa los siguientes campos: {campos_str}")
            return

        try:
            self.db.create_gallo(*datos)
            self.actualizar_tabla()
            self.actualizar_lista_cuerdas()
            self.limpiar_campos()
        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Error al registrar gallo: {e}")


    def modificar_gallo(self):
        selected = self.tabla.selection()
        if not selected:
            return

        id_gallo = self.tabla.item(selected)['values'][0]
        campos_vacios = []
        datos = []

        for field in self.fields:
            if field == "id":
                continue
            valor = self.entries[field].get().strip()
            datos.append(valor)
            if not valor:
                campos_vacios.append(field)

        if campos_vacios:
            campos_str = ", ".join(campos_vacios)
            messagebox.showwarning("Advertencia", f"Por favor, completa los siguientes campos: {campos_str}")
            return

        try:
            self.db.cursor.execute("""
                UPDATE gallos SET cuerda=?, frente=?, anillo=?, placa=?, color=?, peso=?, ciudad=?, tipo=?, numeroJaula=?
                WHERE id=?
            """, datos + [id_gallo])
            self.db.conn.commit()
            self.actualizar_tabla()
            self.actualizar_lista_cuerdas()
            self.limpiar_campos()
        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Error al modificar gallo: {e}")


    def eliminar_gallo(self):
        selected = self.tabla.selection()
        if not selected:
            return
        id_gallo = self.tabla.item(selected)['values'][0]
        self.db.cursor.execute("DELETE FROM gallos WHERE id=?", (id_gallo,))
        self.db.conn.commit()
        self.actualizar_tabla()
        self.actualizar_lista_cuerdas()
        self.limpiar_campos()

    def eliminar_todos(self):
        self.db.cursor.execute("DELETE FROM gallos")
        self.db.conn.commit()
        self.actualizar_tabla()
        self.actualizar_lista_cuerdas()
        self.limpiar_campos()

    def rellenar_campos(self, event):
        selected = self.tabla.selection()
        if not selected:
            return
        datos = self.tabla.item(selected[0])['values']

        for i, field in enumerate(self.fields):
            if field == "id":
                continue
            if field == "tipo":
                self.entries[field].set(datos[i])
            else:
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, str(datos[i]))


    def generar_pdf(self):
        # Lógica delegada a otro módulo utils/pdf_generator.py (a crear)
        pass

    def exportar_excel(self):
        # Lógica delegada a otro módulo utils/export_excel.py (a crear)
        pass

    def realizar_sorteo(self):
        gallos = self.obtener_todos_los_gallos()
        if not gallos:
            messagebox.showwarning("Sorteo", "No hay gallos registrados.")
            return

        def guardar_lista(peleas):
            try:
                with open("lista_de_peleas.txt", "w") as f:
                    for g1, g2 in peleas:
                        l1 = f"{g1['id']},{g1['cuerda']},{g1['frente']},{g1['anillo']},{g1['placa']},{g1['color']},{g1['peso']},{g1['ciudad']},{g1['tipo']}"
                        l2 = f"{g2['id']},{g2['cuerda']},{g2['frente']},{g2['anillo']},{g2['placa']},{g2['color']},{g2['peso']},{g2['ciudad']},{g2['tipo']}"
                        f.write(f"{l1}|{l2}\n")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

        SorteoView(self.root, gallos, guardar_lista)


    def abrir_ventana_torneo(self):
        TorneoView(self.root, self.db)  # A implementar
