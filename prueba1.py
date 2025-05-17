import sqlite3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from fpdf import FPDF
import pandas as pd
import random
from tkinter import messagebox
import time  

# Crear la ventana principal
root = tk.Tk()
root.title("Gestor de Torneos de Gallos")
root.geometry("900x650")

# Título centrado
titulo = tk.Label(root, text="SOFTWARE\nTORNEO DE GALLOS MYN", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

# Crear un frame principal
frame_principal = tk.Frame(root)
frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Crear un frame para la imagen a la derecha
frame_imagen = tk.Frame(frame_principal)
frame_imagen.pack(side=tk.RIGHT, padx=20, pady=10)

# Cargar y mostrar la imagen del logo
try:
    imagen = Image.open("logo.png")
    imagen = imagen.resize((250, 250))
    logo = ImageTk.PhotoImage(imagen)
    label_logo = tk.Label(frame_imagen, image=logo)
    label_logo.pack()
except FileNotFoundError:
    print("Error: El archivo logo.png no se encontró.")
    label_logo = tk.Label(frame_imagen, text="Logo no encontrado", width=25, height=10, relief="solid")
    label_logo.pack()

# Crear un frame para los inputs y botones
frame_form = tk.Frame(frame_principal)
frame_form.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

# Conectar a la base de datos
db = sqlite3.connect("torneo_gallos.db")
cursor = db.cursor()

# Crear la tabla gallos 
cursor.execute('''CREATE TABLE IF NOT EXISTS gallos (
    id INTEGER PRIMARY KEY,
    cuerda TEXT,
    frente TEXT,
    anillo TEXT,
    placa TEXT,
    color TEXT,
    peso REAL,
    ciudad TEXT
)''')


cursor.execute("PRAGMA table_info(gallos);")
columnas = [col[1] for col in cursor.fetchall()]

if 'tipo' not in columnas:
    cursor.execute("ALTER TABLE gallos ADD COLUMN tipo TEXT;")

db.commit()

# Variables de entrada
entries = {}
fields = ["Cuerda", "Frente", "Anillo", "Placa", "Color", "Peso","Ciudad", "Tipo"]

# Agregar el nuevo campo para el tipo de ave
tipo_frame = tk.Frame(frame_form)
tipo_frame.pack(fill=tk.X, padx=5, pady=2)
tk.Label(tipo_frame, text="Tipo:", width=10, anchor="w").pack(side=tk.LEFT)

tipo_combo = ttk.Combobox(tipo_frame, values=["Gallo", "Pollo"], state="readonly")
tipo_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
entries["Tipo"] = tipo_combo  

for field in fields:
    if field == "Tipo":
        continue  
    frame = tk.Frame(frame_form)
    frame.pack(fill=tk.X, padx=5, pady=2)
    tk.Label(frame, text=f"{field}:", width=10, anchor="w").pack(side=tk.LEFT)
    entry = tk.Entry(frame, width=30)
    entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    entries[field] = entry

# Funciones de CRUD
def limpiar_campos():
    for entry in entries.values():
        entry.delete(0, tk.END)
    entries["Tipo"].set("")  

def registrar_gallo():
   
    datos = [entries[field].get() for field in fields[:-1]]  
    tipo = entries["Tipo"].get() 
    
    # Imprimir los datos para verificar
    print("Datos a registrar:", datos)
    print("Tipo a registrar:", tipo)

 
    if not tipo:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un tipo de ave.")
        return

    
    try:
        cursor.execute("INSERT INTO gallos (cuerda, frente, anillo, placa, color, peso, ciudad, tipo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", datos + [tipo])
        db.commit()
        actualizar_tabla()
        actualizar_lista_cuerdas()
        limpiar_campos()
    except Exception as e:
        print("Error al registrar gallo:", e)
        messagebox.showerror("Error", "Ocurrió un error al registrar el gallo. Verifica la consola para más detalles.")

def modificar_gallo():
    selected = tabla.selection()
    if not selected:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un gallo para modificar.")
        return
    id_gallo = tabla.item(selected)['values'][0]
    
    nuevos_datos = [entries[field].get() for field in fields[:-1]] 
    tipo = entries["Tipo"].get()  
    
    nuevos_datos.append(tipo)  

  
    if len(nuevos_datos) != 8:  
        print(f"Error: Se esperaban 8 elementos, pero se obtuvieron {len(nuevos_datos)}: {nuevos_datos}")
        return  


    cursor.execute("UPDATE gallos SET cuerda=?, frente=?, anillo=?, placa=?, color=?, peso=?, ciudad=?, tipo=? WHERE id=?", nuevos_datos + [id_gallo])
    db.commit()
    actualizar_tabla()
    actualizar_lista_cuerdas()
    limpiar_campos()

def eliminar_gallo():
    selected = tabla.selection()
    if not selected:
        return
    id_gallo = tabla.item(selected)['values'][0]
    cursor.execute("DELETE FROM gallos WHERE id=?", (id_gallo,))
    db.commit()
    actualizar_tabla()
    actualizar_lista_cuerdas()

def eliminar_todos():
    cursor.execute("DELETE FROM gallos")
    db.commit()
    actualizar_tabla()
    actualizar_lista_cuerdas()

def actualizar_tabla():
    for row in tabla.get_children():
        tabla.delete(row)
    cursor.execute("SELECT * FROM gallos")
    for row in cursor.fetchall():
        tabla.insert("", "end", values=row)

# seleccionar cuerda
cuerda_combo = ttk.Combobox(root, state="readonly")
cuerda_combo.pack(pady=10)

def actualizar_lista_cuerdas():
    cursor.execute("SELECT DISTINCT cuerda FROM gallos")
    cuerdas = [row[0] for row in cursor.fetchall()]
    cuerda_combo['values'] = cuerdas

actualizar_lista_cuerdas()

# Función para generar PDF
def generar_pdf():
    cuerda_seleccionada = cuerda_combo.get()
    if not cuerda_seleccionada:
        return
    cursor.execute("SELECT * FROM gallos WHERE cuerda=?", (cuerda_seleccionada,))
    todos_los_gallos = cursor.fetchall()
    if not todos_los_gallos:
        return

    # Agrupar los gallos por frente
    gallos_por_frente = {}
    for gallo in todos_los_gallos:
        frente = gallo[2]  
        if frente not in gallos_por_frente:
            gallos_por_frente[frente] = []
        gallos_por_frente[frente].append(gallo)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "PRIMER TORNEO ORGULLO PEÑONERO", ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Información de la Cuerda", ln=True, align="L")
    pdf.cell(200, 10, f"Cuerda: {cuerda_seleccionada}", ln=True, align="L")

    primer_frente = True
    for frente, lista_gallos in sorted(gallos_por_frente.items()):
        if not primer_frente:
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "PRIMER TORNEO ORGULLO PEÑONERO", ln=True, align="C")
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "Información de la Cuerda", ln=True, align="L")
            pdf.cell(200, 10, f"Cuerda: {cuerda_seleccionada}", ln=True, align="L")

        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, f"Frente: {frente}", ln=True, align="L")
        pdf.ln(2)

        pdf.set_font("Arial", "B", 10)
        col_width = pdf.w / 4
        pdf.cell(col_width, 8, "ANILLO", border=1, align="C")
        pdf.cell(col_width, 8, "PLACA", border=1, align="C")
        pdf.cell(col_width, 8, "COLOR", border=1, align="C")
        pdf.cell(col_width, 8, "PESO", border=1, align="C")
        pdf.ln()

        pdf.set_font("Arial", size=10)
        for gallo in lista_gallos:
            pdf.cell(col_width, 8, str(gallo[3]), border=1, align="C") # Anillo
            pdf.cell(col_width, 8, str(gallo[4]), border=1, align="C") # Placa
            pdf.cell(col_width, 8, gallo[5], border=1, align="C")       # Color
            pdf.cell(col_width, 8, str(gallo[6]), border=1, align="C") # Peso
            pdf.ln()
        pdf.ln(5)

        primer_frente = False

    pdf.output(f"Torneo_{cuerda_seleccionada}.pdf")

def exportar_excel():
    cursor.execute("SELECT * FROM gallos")
    datos = cursor.fetchall()
    df = pd.DataFrame(datos, columns=["ID", "Cuerda", "Frente", "Anillo", "Placa", "Color", "Peso", "Ciudad","Tipo"])
    df.to_excel("Torneo_Gallos.xlsx", index=False)

def obtener_todos_los_gallos_con_detalles():
    cursor.execute("SELECT * FROM gallos")
    column_names = [description[0] for description in cursor.description]
    return [dict(zip(column_names, row)) for row in cursor.fetchall()]

def generar_pdf_sorteo(peleas_automaticas, peleas_manuales):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "RESULTADO PELEAS ORDENADAS 1ER TORNEO  ORGULLO PEÑONERO", ln=True, align="C")

    # Logo debajo del título 
    try:
        img = Image.open("logo.png")
        width, height = img.size
        max_width = 20  
        ratio = max_width / width
        new_height = height * ratio
        x_position = (pdf.w - max_width) / 2
        y_position = 20 
        pdf.image("logo.png", x=x_position, y=y_position, w=max_width, h=new_height)
        pdf.ln(new_height + 5) 
    except FileNotFoundError:
        pdf.set_font("Arial", "", 8)
        pdf.cell(0, 5, "Logo no encontrado", ln=True, align="C")
        pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Lista de Peleas:", ln=True)
    pdf.ln(5)

    todas_las_peleas = peleas_automaticas + peleas_manuales

    if todas_las_peleas:
        pdf.set_font("Arial", "B", 8)
        col_width_orden = 10
        col_width_frente = 15
        col_width_cuerda = 25
        col_width_ciudad = 30
        col_width_color = 20
        col_width_peso = 15
        col_width_anillo = 25
        col_width_placa = 25
        col_width_tipo = 20  

        # Encabezados de columna
        pdf.cell(col_width_orden, 5, "Orden", align="C")
        pdf.cell(col_width_frente, 5, "Frente", align="C")
        pdf.cell(col_width_cuerda, 5, "Cuerda", align="C")
        pdf.cell(col_width_tipo, 5, "Tipo", align="C") 
        pdf.cell(col_width_ciudad, 5, "Ciudad", align="C")
        pdf.cell(col_width_color, 5, "Color", align="C")
        pdf.cell(col_width_peso, 5, "Peso", align="C")
        pdf.cell(col_width_anillo, 5, "Anillo", align="C")
        pdf.cell(col_width_placa, 5, "Placa", align="C")
        pdf.ln()

        pdf.set_font("Arial", "", 8)
        for i, pelea in enumerate(todas_las_peleas, 1):
            gallo1 = pelea[0]
            gallo2 = pelea[1]

            # Imprimir información de gallo 1
            pdf.cell(col_width_orden, 5, str(i), align="C")
            pdf.cell(col_width_frente, 5, gallo1.get('frente', ''), align="C")
            pdf.cell(col_width_cuerda, 5, gallo1.get('cuerda', ''), align="C")
            pdf.cell(col_width_tipo, 5, gallo1.get('tipo', ''), align="C") 
            pdf.cell(col_width_ciudad, 5, gallo1.get('ciudad', ''), align="C")
            pdf.cell(col_width_color, 5, gallo1.get('color', ''), align="C")
            pdf.cell(col_width_peso, 5, str(gallo1.get('peso', '')), align="C")
            pdf.cell(col_width_anillo, 5, gallo1.get('anillo', ''), align="C")
            pdf.cell(col_width_placa, 5, gallo1.get('placa', ''), align="C")
            pdf.ln()

            # Imprimir información de gallo 2
            pdf.cell(col_width_orden, 5, "", align="C")  
            pdf.cell(col_width_frente, 5, gallo2.get('frente', ''), align="C")
            pdf.cell(col_width_cuerda, 5, gallo2.get('cuerda', ''), align="C")
            pdf.cell(col_width_tipo, 5, gallo2.get('tipo', ''), align="C")  
            pdf.cell(col_width_ciudad, 5, gallo2.get('ciudad', ''), align="C")
            pdf.cell(col_width_color, 5, gallo2.get('color', ''), align="C")
            pdf.cell(col_width_peso, 5, str(gallo2.get('peso', '')), align="C")
            pdf.cell(col_width_anillo, 5, gallo2.get('anillo', ''), align="C")
            pdf.cell(col_width_placa, 5, gallo2.get('placa', ''), align="C")
            pdf.ln()

            pdf.ln(2)  

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Total de Peleas en el Torneo: {len(todas_las_peleas)}", ln=True)
    else:
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, "No se encontraron peleas en el sorteo.", ln=True)

    pdf.output("Resultado_Sorteo.pdf")
    messagebox.showinfo("PDF Generado", "El archivo Resultado_Sorteo.pdf ha sido creado.")
def realizar_sorteo():
    gallos_detalles = obtener_todos_los_gallos_con_detalles()
    if not gallos_detalles:
        messagebox.showinfo("Sorteo", "No hay gallos registrados para el sorteo.")
        return

    
    gallos_con_peso_int = []
    for gallo in gallos_detalles:
        gallos_con_peso_int.append({
            'id': gallo['id'],
            'cuerda': gallo['cuerda'],
            'frente': gallo['frente'],
            'anillo': gallo['anillo'],
            'placa': gallo['placa'],
            'color': gallo['color'],
            'peso_int': int(gallo['peso'] * 10),
            'peso': gallo['peso'],
            'ciudad': gallo['ciudad'],
            'tipo': gallo['tipo']  
        })

    gallos_con_peso_int.sort(key=lambda x: x['peso_int'])  # Ordenar por peso

    peleas_automaticas = []
    sin_emparejar = []
    usados = [False] * len(gallos_con_peso_int)
    global peleas_manuales
    if 'peleas_manuales' not in globals():
        peleas_manuales = []

    for i in range(len(gallos_con_peso_int)):
        if not usados[i]:
            gallo1_info = gallos_con_peso_int[i]
            usados[i] = True
            rival_encontrado = False
            for j in range(i + 1, len(gallos_con_peso_int)):
                if not usados[j]:
                    gallo2_info = gallos_con_peso_int[j]
                    # Verificar que sean del mismo tipo y que cumplan con la diferencia de peso
                    if (gallo1_info['tipo'] == gallo2_info['tipo'] and
                        abs(gallo1_info['peso_int'] - gallo2_info['peso_int']) <= 1):
                        peleas_automaticas.append((gallo1_info, gallo2_info))
                        usados[j] = True
                        rival_encontrado = True
                        break
            if not rival_encontrado:
                sin_emparejar.append(gallo1_info)

    # Mostrar resultados del sorteo
    ventana_sorteo = tk.Toplevel(root)
    ventana_sorteo.title("Resultado del Sorteo")
    ventana_sorteo.geometry("800x500")

    lbl_peleas = tk.Label(ventana_sorteo, text="Peleas Encontradas (Automáticamente):", font=("Arial", 12, "bold"))
    lbl_peleas.pack(pady=5)
    if peleas_automaticas:
        for pelea in peleas_automaticas:
            gallo1 = pelea[0]
            gallo2 = pelea[1]
            gallo1_info_str = f"Frente: {gallo1['frente']}, Cuerda: {gallo1['cuerda']}, Tipo: {gallo1['tipo']}, Peso: {gallo1['peso']}, Color: {gallo1['color']}, Anillo: {gallo1['anillo']}, Placa: {gallo1['placa']}, Ciudad: {gallo1['ciudad']}"
            gallo2_info_str = f"Frente: {gallo2['frente']}, Cuerda: {gallo2['cuerda']}, Tipo: {gallo2['tipo']}, Peso: {gallo2['peso']}, Color: {gallo2['color']}, Anillo: {gallo2['anillo']}, Placa: {gallo2['placa']}, Ciudad: {gallo2['ciudad']}"
            lbl_pelea = tk.Label(ventana_sorteo, text=f"{gallo1_info_str} vs {gallo2_info_str}")
            lbl_pelea.pack()
    else:
        lbl_sin_peleas = tk.Label(ventana_sorteo, text="No se encontraron peleas automáticamente con la diferencia de peso requerida.")
        lbl_sin_peleas.pack()

    lbl_sin_emparejar = tk.Label(ventana_sorteo, text="\nGallos sin Emparejar:", font=("Arial", 12, "bold"))
    lbl_sin_emparejar.pack(pady=5)
    gallos_sin_emparejar_lista = []
    if sin_emparejar:
        listbox_sin_emparejar = tk.Listbox(ventana_sorteo, selectmode=tk.MULTIPLE, height=5)
        for gallo in sin_emparejar:
            info_gallo = f"Frente: {gallo['frente']}, Cuerda: {gallo['cuerda']}, Tipo: {gallo['tipo']}, Peso: {gallo['peso']}, Color: {gallo['color']}, Anillo: {gallo['anillo']}, Placa: {gallo['placa']}, Ciudad: {gallo['ciudad']}"
            listbox_sin_emparejar.insert(tk.END, info_gallo)
            gallos_sin_emparejar_lista.append(gallo)
        listbox_sin_emparejar.pack(fill=tk.BOTH, expand=True)

        lbl_manual = tk.Label(ventana_sorteo, text="\nEmparejamiento Manual (Seleccionar dos gallos con diferencia > 0.1 onzas):")
        lbl_manual.pack()

        def emparejar_manual():
            seleccionados_indices = listbox_sin_emparejar.curselection()
            if len(seleccionados_indices) == 2:
                gallo1 = gallos_sin_emparejar_lista[seleccionados_indices[0]]
                gallo2 = gallos_sin_emparejar_lista[seleccionados_indices[1]]
                if gallo1['cuerda'] != gallo2['cuerda']:
                    nueva_pelea = (gallo1, gallo2)
                    messagebox.showinfo("Emparejamiento Manual", f"Se ha emparejado manualmente:\n{gallo1['frente']} ({gallo1['cuerda']}) vs {gallo2['frente']} ({gallo2['cuerda']})")
                    global peleas_manuales
                    if 'peleas_manuales' not in globals():
                        peleas_manuales = []
                    peleas_manuales.append(nueva_pelea)
                    gallo1_info_manual = f"Frente: {gallo1['frente']}, Cuerda: {gallo1['cuerda']}, Tipo: {gallo1['tipo']}, Peso: {gallo1['peso']}, Color: {gallo1['color']}, Anillo: {gallo1['anillo']}, Placa: {gallo1['placa']}, Ciudad: {gallo1['ciudad']}"
                    gallo2_info_manual = f"Frente: {gallo2['frente']}, Cuerda: {gallo2['cuerda']}, Tipo: {gallo2['tipo']}, Peso: {gallo2['peso']}, Color: {gallo2['color']}, Anillo: {gallo2['anillo']}, Placa: {gallo2['placa']}, Ciudad: {gallo2['ciudad']}"
                    lbl_pelea_manual = tk.Label(ventana_sorteo, text=f"{gallo1_info_manual} vs {gallo2_info_manual}")
                    lbl_pelea_manual.pack()
                    indices_a_eliminar = sorted(seleccionados_indices, reverse=True)
                    for indice in indices_a_eliminar:
                        del gallos_sin_emparejar_lista[indice]
                        listbox_sin_emparejar.delete(indice)
                    if not gallos_sin_emparejar_lista:
                        lbl_manual.config(text="No hay gallos para emparejar manualmente.")
                        btn_emparejar_manual.config(state=tk.DISABLED)
                else:
                    messagebox.showerror("Error", "No se pueden emparejar manualmente gallos de la misma cuerda.")
            elif len(seleccionados_indices) != 2:
                messagebox.showerror("Error", "Por favor, selecciona exactamente dos gallos para emparejar manualmente.")

        btn_emparejar_manual = tk.Button(ventana_sorteo, text="Emparejar Seleccionados", command=emparejar_manual)
        btn_emparejar_manual.pack(pady=5)

        lbl_peleas_manuales = tk.Label(ventana_sorteo, text="", font=("Arial", 12, "bold"))
        lbl_peleas_manuales.pack(pady=5)
        for pelea_manual in peleas_manuales:
            gallo1_info_manual = f"Frente: {pelea_manual[0]['frente']}, Cuerda: {pelea_manual[0]['cuerda']}, Tipo: {pelea_manual[0]['tipo']}, Peso: {pelea_manual[0]['peso']}, Color: {pelea_manual[0]['color']}, Anillo: {pelea_manual[0]['anillo']}, Placa: {pelea_manual[0]['placa']}, Ciudad: {pelea_manual[0]['ciudad']}"
            gallo2_info_manual = f"Frente: {pelea_manual[1]['frente']}, Cuerda: {pelea_manual[1]['cuerda']}, Tipo: {pelea_manual[1]['tipo']}, Peso: {pelea_manual[1]['peso']}, Color: {pelea_manual[1]['color']}, Anillo: {pelea_manual[1]['anillo']}, Placa: {pelea_manual[1]['placa']}, Ciudad: {pelea_manual[1]['ciudad']}"
            lbl_pelea_manual_inicial = tk.Label(ventana_sorteo, text=f"{gallo1_info_manual} vs {gallo2_info_manual}")
            lbl_pelea_manual_inicial.pack()

    else:
        lbl_sin_emparejar_msj = tk.Label(ventana_sorteo, text="Todos los gallos han sido emparejados automáticamente.")
        lbl_sin_emparejar_msj.pack()

    def guardar_lista_peleas():
        todas_las_peleas = peleas_automaticas + peleas_manuales
        try:
            with open("lista_de_peleas.txt", "w") as archivo_peleas:
                for pelea in todas_las_peleas:
                    gallo1 = pelea[0]
                    gallo2 = pelea[1]
                    gallo1_str = f"{gallo1['id']},{gallo1['cuerda']},{gallo1['frente']},{gallo1['anillo']},{gallo1['placa']},{gallo1['color']},{gallo1['peso']},{gallo1['ciudad']},{gallo1['tipo']}"  # Agregar tipo aquí
                    gallo2_str = f"{gallo2['id']},{gallo2['cuerda']},{gallo2['frente']},{gallo2['anillo']},{gallo2['placa']},{gallo2['color']},{gallo2['peso']},{gallo2['ciudad']},{gallo2['tipo']}"  # Agregar tipo aquí
                    archivo_peleas.write(f"{gallo1_str}|{gallo2_str}\n")
            messagebox.showinfo("Sorteo", "Lista de peleas guardada.")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"Ocurrió un error al guardar la lista de peleas: {e}")

    btn_generar_pdf_sorteo = tk.Button(ventana_sorteo, text="Generar PDF", command=lambda: [guardar_lista_peleas(), generar_pdf_sorteo(peleas_automaticas, peleas_manuales)])
    btn_generar_pdf_sorteo.pack(pady=10)

# Variables para el torneo
resultados_pelea = []  # Lista para almacenar los resultados de las peleas
tiempo_total = 0  # Variable para el tiempo total de pelea
corriendo = False  # Variable para controlar si el reloj está corriendo

def abrir_ventana_torneo():
    ventana_torneo = tk.Toplevel(root)
    ventana_torneo.title("Desarrollo del Torneo")
    ventana_torneo.geometry("800x700")

    global indice_pelea_actual
    global resultado_pelea_label
    indice_pelea_actual = 0

    # Reloj Principal
    reloj_label = tk.Label(ventana_torneo, text="0:00", font=("Arial", 48))
    reloj_label.pack(pady=10)

    def actualizar_reloj():
        global tiempo_total
        if corriendo:
            minutos = tiempo_total // 60
            segundos = tiempo_total % 60
            reloj_label.config(text=f"{minutos}:{segundos:02d}")
            tiempo_total += 1
            ventana_torneo.after(1000, actualizar_reloj)  

    def iniciar_reloj():
        global corriendo
        corriendo = True
        actualizar_reloj() 
        boton_iniciar.config(state=tk.DISABLED)
        boton_detener.config(state=tk.NORMAL)

    def detener_reloj():
        global corriendo
        corriendo = False
        boton_iniciar.config(state=tk.NORMAL)
        boton_detener.config(state=tk.DISABLED)

        

    boton_iniciar = tk.Button(ventana_torneo, text="Iniciar Reloj", command=iniciar_reloj, font=("Arial", 16))
    boton_iniciar.pack(pady=5)

    boton_detener = tk.Button(ventana_torneo, text="Detener Reloj", command=detener_reloj, font=("Arial", 16), state=tk.DISABLED)
    boton_detener.pack(pady=5)

    # Sección de información de los gallos 
    frame_gallos = tk.Frame(ventana_torneo)
    frame_gallos.pack(pady=10)

    label_rojo_titulo = tk.Label(frame_gallos, text="Cinta Roja:", font=("Arial", 12, "bold"), fg="red")
    label_rojo_titulo.pack(anchor="w")
    info_rojo_label = tk.Label(frame_gallos, text="", font=("Arial", 12), justify="left")
    info_rojo_label.pack(anchor="w")

    label_azul_titulo = tk.Label(frame_gallos, text="Cinta Azul:", font=("Arial", 12, "bold"), fg="blue")
    label_azul_titulo.pack(anchor="w")
    info_azul_label = tk.Label(frame_gallos, text="", font=("Arial", 12), justify="left")
    info_azul_label.pack(anchor="w")

    # Temporizadores Individuales 
    frame_timers = tk.Frame(ventana_torneo)
    frame_timers.pack(pady=5)

    # Temporizador Cinta Roja
    frame_rojo_timer = tk.Frame(frame_timers)
    frame_rojo_timer.pack(side=tk.LEFT, padx=20)
    rojo_timer_label = tk.Label(frame_rojo_timer, text="1:00", font=("Arial", 24), fg="red")
    rojo_timer_label.pack()
    rojo_timer_corriendo = False
    rojo_tiempo_restante = 60
    rojo_timer_id = None

    def actualizar_rojo_timer():
        nonlocal rojo_tiempo_restante
        if rojo_timer_corriendo:
            minutos = rojo_tiempo_restante // 60
            segundos = rojo_tiempo_restante % 60
            rojo_timer_label.config(text=f"{minutos}:{segundos:02d}")
            if rojo_tiempo_restante > 0:
                rojo_tiempo_restante -= 1
                rojo_timer_id = ventana_torneo.after(1000, actualizar_rojo_timer)
            else:
                detener_rojo_timer()

    def iniciar_rojo_timer():
        nonlocal rojo_timer_corriendo, rojo_tiempo_restante
        rojo_timer_corriendo = True
        actualizar_rojo_timer()
        boton_iniciar_rojo.config(state=tk.DISABLED)
        boton_detener_rojo.config(state=tk.NORMAL)

    def detener_rojo_timer():
        nonlocal rojo_timer_corriendo, rojo_timer_id, rojo_tiempo_restante
        rojo_timer_corriendo = False
        if rojo_timer_id:
            ventana_torneo.after_cancel(rojo_timer_id)
            rojo_timer_id = None
        rojo_tiempo_restante = 60  # Reiniciar el tiempo
        rojo_timer_label.config(text="1:00")  
        boton_iniciar_rojo.config(state=tk.NORMAL)
        boton_detener_rojo.config(state=tk.DISABLED)

    boton_iniciar_rojo = tk.Button(frame_rojo_timer, text="Iniciar Rojo", command=iniciar_rojo_timer, font=("Arial", 12))
    boton_iniciar_rojo.pack()
    boton_detener_rojo = tk.Button(frame_rojo_timer, text="Detener Rojo", command=detener_rojo_timer, font=("Arial", 12), state=tk.DISABLED)
    boton_detener_rojo.pack()

    # Temporizador Cinta Azul
    frame_azul_timer = tk.Frame(frame_timers)
    frame_azul_timer.pack(side=tk.RIGHT, padx=20)
    azul_timer_label = tk.Label(frame_azul_timer, text="1:00", font=("Arial", 24), fg="blue")
    azul_timer_label.pack()
    azul_timer_corriendo = False
    azul_tiempo_restante = 60
    azul_timer_id = None

    def actualizar_azul_timer():
        nonlocal azul_tiempo_restante
        if azul_timer_corriendo:
            minutos = azul_tiempo_restante // 60
            segundos = azul_tiempo_restante % 60
            azul_timer_label.config(text=f"{minutos}:{segundos:02d}")
            if azul_tiempo_restante > 0:
                azul_tiempo_restante -= 1
                azul_timer_id = ventana_torneo.after(1000, actualizar_azul_timer)
            else:
                detener_azul_timer()

    def iniciar_azul_timer():
        nonlocal azul_timer_corriendo, azul_tiempo_restante
        azul_timer_corriendo = True
        actualizar_azul_timer()
        boton_iniciar_azul.config(state=tk.DISABLED)
        boton_detener_azul.config(state=tk.NORMAL)

    def detener_azul_timer():
        nonlocal azul_timer_corriendo, azul_timer_id, azul_tiempo_restante
        azul_timer_corriendo = False
        if azul_timer_id:
            ventana_torneo.after_cancel(azul_timer_id)
            azul_timer_id = None
        azul_tiempo_restante = 60  # Reiniciar el tiempo
        azul_timer_label.config(text="1:00")  
        boton_iniciar_azul.config(state=tk.NORMAL)
        boton_detener_azul.config(state=tk.DISABLED)

    boton_iniciar_azul = tk.Button(frame_azul_timer, text="Iniciar Azul", command=iniciar_azul_timer, font=("Arial", 12))
    boton_iniciar_azul.pack()
    boton_detener_azul = tk.Button(frame_azul_timer, text="Detener Azul", command=detener_azul_timer, font=("Arial", 12), state=tk.DISABLED)
    boton_detener_azul.pack()

    # Sección para seleccionar el ganador 
    frame_resultado = tk.Frame(ventana_torneo)
    frame_resultado.pack(pady=15)

    def seleccionar_ganador(ganador):
        global resultado_pelea_label
        global tiempo_total 
        # Calcular la duración de la pelea
        duracion = tiempo_total  # Usar el tiempo total del reloj principal
        minutos = duracion // 60
        segundos = duracion % 60
        duracion_formateada = f"{minutos}:{segundos:02d}"
        if ganador == "Tabla":  # Si es un empate
         resultado = {
            "ganador": "Empate",
            "perdedor": "Empate",
            "tiempo": duracion_formateada
        }
        else:
         resultado = {
            "ganador": ganador,
            "perdedor": "Azul" if ganador == "Rojo" else "Rojo",
            "tiempo": duracion_formateada
        }
        resultados_pelea.append(resultado)  # Agregar el resultado a la lista
        resultado_pelea_label.config(text=f"Resultado de la Pelea: Ganador - {ganador}, Perdedor - {'Azul' if ganador == 'Rojo' else 'Rojo'}, Tiempo - {duracion_formateada} ")
        
        # Reiniciar el tiempo total y la etiqueta del reloj

        tiempo_total = 0
        reloj_label.config(text="0:00")  # Reiniciar el reloj a 0:00


        # Mostrar resultados en una nueva ventana
        mostrar_resultados()
        
        # Deshabilitar botones de resultado
        boton_rojo_gana.config(state=tk.DISABLED)
        boton_azul_gana.config(state=tk.DISABLED)
        boton_tabla.config(state=tk.DISABLED)
        boton_siguiente_pelea.config(state=tk.NORMAL)  # Habilitar para la siguiente pelea

    boton_rojo_gana = tk.Button(frame_resultado, text="Ganó Rojo", command=lambda: seleccionar_ganador("Rojo"), font=("Arial", 14), fg="red")
    boton_rojo_gana.pack(side=tk.LEFT, padx=10)

    boton_azul_gana = tk.Button(frame_resultado, text="Ganó Azul", command=lambda: seleccionar_ganador("Azul"), font=("Arial", 14), fg="blue")
    boton_azul_gana.pack(side=tk.LEFT, padx=10)

    boton_tabla = tk.Button(frame_resultado, text="Tabla (Empate)", command=lambda: seleccionar_ganador("Tabla"), font=("Arial", 14))
    boton_tabla.pack(side=tk.LEFT, padx=10)

    resultado_pelea_label = tk.Label(ventana_torneo, text="Resultado de la Pelea: Sin definir", font=("Arial", 12, "italic"))
    resultado_pelea_label.pack(pady=5)

    def mostrar_resultados():
        ventana_resultados = tk.Toplevel(root)
        ventana_resultados.title("Resultados de la Pelea")
        ventana_resultados.geometry("400x300")

        # Crear tabla
        columnas = ["Ganador", "Perdedor", "Duración"]
        tabla_resultados = ttk.Treeview(ventana_resultados, columns=columnas, show="headings")
        for col in columnas:
            tabla_resultados.heading(col, text=col)
            tabla_resultados.column(col, width=100)
        tabla_resultados.pack(fill=tk.BOTH, expand=True)

        # Insertar resultados en la tabla
        for resultado in resultados_pelea:
            tabla_resultados.insert("", "end", values=(resultado["ganador"], resultado["perdedor"], resultado["tiempo"]))

        # Botón para cerrar la ventana
        tk.Button(ventana_resultados, text="Cerrar", command=ventana_resultados.destroy).pack(pady=10)

    def cargar_lista_de_peleas():
        global lista_de_peleas_cargada
        global indice_pelea_actual
        try:
            with open("lista_de_peleas.txt", "r") as archivo:
                lista_de_peleas_cargada = []
                for linea in archivo:
                    gallo1_str, gallo2_str = linea.strip().split("|")
                    datos_gallo1 = dict(zip(['id', 'cuerda', 'frente', 'anillo', 'placa', 'color', 'peso', 'ciudad'], gallo1_str.split(",")))
                    datos_gallo2 = dict(zip(['id', 'cuerda', 'frente', 'anillo', 'placa', 'color', 'peso', 'ciudad'], gallo2_str.split(",")))
                    # Convertir 'id' y 'peso' a sus tipos originales (int y float)
                    datos_gallo1['id'] = int(datos_gallo1['id'])
                    datos_gallo1['peso'] = float(datos_gallo1['peso'])
                    datos_gallo2['id'] = int(datos_gallo2['id'])
                    datos_gallo2['peso'] = float(datos_gallo2['peso'])
                    lista_de_peleas_cargada.append((datos_gallo1, datos_gallo2))
                boton_siguiente_pelea.config(state=tk.NORMAL)  # Habilitar el botón una vez cargada la lista
                cargar_siguiente_pelea()  # Cargar la primera pelea automáticamente
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el archivo con la lista de peleas (lista_de_peleas.txt). Realice el sorteo primero.")
            boton_siguiente_pelea.config(state=tk.DISABLED)

    def cargar_siguiente_pelea():
        global indice_pelea_actual
        global resultado_pelea_label
        if indice_pelea_actual < len(lista_de_peleas_cargada):
            pelea = lista_de_peleas_cargada[indice_pelea_actual]
            gallo_rojo = pelea[0]
            gallo_azul = pelea[1]

            info_rojo = f"Frente: {gallo_rojo.get('frente', '')}, Cuerda: {gallo_rojo.get('cuerda', '')}, Peso: {gallo_rojo.get('peso', '')}, Color: {gallo_rojo.get('color', '')}, Anillo: {gallo_rojo.get('anillo', '')}, Placa: {gallo_rojo.get('placa', '')}, Ciudad: {gallo_rojo.get('ciudad', '')}"
            info_azul = f"Frente: {gallo_azul.get('frente', '')}, Cuerda: {gallo_azul.get('cuerda', '')}, Peso: {gallo_azul.get('peso', '')}, Color: {gallo_azul.get('color', '')}, Anillo: {gallo_azul.get('anillo', '')}, Placa: {gallo_azul.get('placa', '')}, Ciudad: {gallo_azul.get('ciudad', '')}"

            info_rojo_label.config(text=info_rojo)
            info_azul_label.config(text=info_azul)

            # Reiniciar los temporizadores al cargar una nueva pelea
            detener_rojo_timer()
            detener_azul_timer()

            # Habilitar los botones de resultado para la nueva pelea
            boton_rojo_gana.config(state=tk.NORMAL)
            boton_azul_gana.config(state=tk.NORMAL)
            boton_tabla.config(state=tk.NORMAL)
            resultado_pelea_label.config(text="Resultado de la Pelea: Sin definir")
            boton_siguiente_pelea.config(state=tk.DISABLED)  # Deshabilitar hasta que se seleccione un ganador

            indice_pelea_actual += 1
            if indice_pelea_actual >= len(lista_de_peleas_cargada):
                boton_siguiente_pelea.config(state=tk.DISABLED, text="Fin de las Peleas")
        elif not lista_de_peleas_cargada:
            messagebox.showinfo("Información", "La lista de peleas no ha sido cargada. Realice el sorteo primero.")
        else:
            boton_siguiente_pelea.config(state=tk.DISABLED, text="Fin de las Peleas")

    boton_siguiente_pelea = tk.Button(ventana_torneo, text="Siguiente Pelea", command=cargar_siguiente_pelea, font=("Arial", 16), state=tk.DISABLED)  # Inicialmente deshabilitado
    boton_siguiente_pelea.pack(pady=10)

    # Cargar la lista de peleas al abrir la ventana del torneo
    cargar_lista_de_peleas()

# Crear un frame para los botones
frame_botones = tk.Frame(frame_form)
frame_botones.pack(pady=10)  # Usando pack aquí

# Botones
tk.Button(frame_botones, text="Registrar Gallo", command=registrar_gallo, width=20).grid(row=0, column=0, padx=5, pady=2)
tk.Button(frame_botones, text="Modificar Gallo", command=modificar_gallo, width=20).grid(row=0, column=1, padx=5, pady=2)
tk.Button(frame_botones, text="Eliminar Gallo", command=eliminar_gallo, width=20).grid(row=1, column=0, padx=5, pady=2)
tk.Button(frame_botones, text="Eliminar Todos", command=eliminar_todos, width=20).grid(row=1, column=1, padx=5, pady=2)
tk.Button(frame_botones, text="Generar PDF", command=generar_pdf, width=20).grid(row=2, column=0, padx=5, pady=2)
tk.Button(frame_botones, text="Realizar Sorteo", command=realizar_sorteo, width=20).grid(row=2, column=1, padx=5, pady=2)
tk.Button(frame_botones, text="Exportar a Excel", command=exportar_excel, width=20).grid(row=3, column=0, padx=5, pady=2)
tk.Button(frame_botones, text="Iniciar Torneo", command=abrir_ventana_torneo, width=20).grid(row=3, column=1, padx=5, pady=2)

# Tabla
columnas = ["ID", "Cuerda", "Frente", "Anillo", "Placa", "Color", "Peso", "Ciudad", "Tipo"] 
tabla = ttk.Treeview(root, columns=columnas, show="headings")
for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=100)
tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def actualizar_tabla():
    for row in tabla.get_children():
        tabla.delete(row)
    cursor.execute("SELECT * FROM gallos")
    for row in cursor.fetchall():
        tabla.insert("", "end", values=row)

# Función para llenar campos al seleccionar un gallo
def rellenar_campos(event):
    selected = tabla.selection()
    if not selected:
        return
    datos = tabla.item(selected[0])['values']
    for i, field in enumerate(fields):
        entries[field].delete(0, tk.END)  # Limpiar el campo
        if i < len(datos) - 1:  
            entries[field].insert(0, str(datos[i + 1])) 

tabla.bind("<<TreeviewSelect>>", rellenar_campos)

# Iniciar el bucle principal de la interfaz
actualizar_tabla()
root.mainloop()
