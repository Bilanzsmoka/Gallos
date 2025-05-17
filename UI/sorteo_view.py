import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
from fpdf import FPDF


class SorteoView:
    def __init__(self, parent, gallos_detalles, guardar_callback):
        self.gallos_detalles = gallos_detalles
        self.guardar_callback = guardar_callback
        self.peleas_automaticas = []
        self.peleas_manuales = []
        self.sin_emparejar = []

        self.root = tk.Toplevel(parent)
        self.root.title("Resultado del Sorteo")
        self.root.geometry("800x600")

        self.realizar_sorteo()
        self.mostrar_resultados()

    def realizar_sorteo(self):
        gallos = [
            {
                'id': g['id'], 'cuerda': g['cuerda'], 'frente': g['frente'], 'anillo': g['anillo'],
                'placa': g['placa'], 'color': g['color'], 'peso_int': int(g['peso'] * 10),
                'peso': g['peso'], 'ciudad': g['ciudad'], 'tipo': g['tipo'],'numeroJaula': g['numeroJaula'],
            } for g in self.gallos_detalles
        ]

        gallos.sort(key=lambda x: x['peso_int'])
        usados = [False] * len(gallos)

        for i in range(len(gallos)):
            if not usados[i]:
                g1 = gallos[i]
                usados[i] = True
                match = False
                for j in range(i + 1, len(gallos)):
                    if not usados[j]:
                        g2 = gallos[j]
                        if g1['tipo'] == g2['tipo'] and abs(g1['peso_int'] - g2['peso_int']) <= 1:
                            self.peleas_automaticas.append((g1, g2))
                            usados[j] = True
                            match = True
                            break
                if not match:
                    self.sin_emparejar.append(g1)

    def mostrar_resultados(self):
        # Contenedor con canvas para hacer scroll
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetar el canvas y el scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Desde aquí en adelante, todos los elementos se añaden a scroll_frame
        tk.Label(scroll_frame, text="Peleas Encontradas (Automáticamente):",
                font=("Arial", 12, "bold")).pack(pady=5)

        if self.peleas_automaticas:
            for g1, g2 in self.peleas_automaticas:
                tk.Label(
                    scroll_frame,
                    text=f"Frente: {g1['frente']}, Cuerda: {g1['cuerda']}, Tipo: {g1['tipo']}, Peso: {g1['peso']}, Color: {g1['color']}, Anillo: {g1['anillo']}, Placa: {g1['placa']}, Ciudad: {g1['ciudad']}, # Jaula: {g1['numeroJaula']} vs Frente: {g2['frente']}, Cuerda: {g2['cuerda']}, Tipo: {g2['tipo']}, Peso: {g2['peso']}, Color: {g2['color']}, Anillo: {g2['anillo']}, Placa: {g2['placa']}, Ciudad: {g2['ciudad']}, # Jaula: {g2['numeroJaula']}"
                ).pack(anchor="w")
        else:
            tk.Label(scroll_frame, text="No se encontraron peleas automáticamente.").pack()

        tk.Label(scroll_frame, text="\nGallos sin Emparejar:",
                font=("Arial", 12, "bold")).pack(pady=5)

        if self.sin_emparejar:
            self.listbox = tk.Listbox(scroll_frame, selectmode=tk.MULTIPLE, height=6)
            for g in self.sin_emparejar:
                self.listbox.insert(
                    tk.END, f"Frente: {g['frente']}, Cuerda: {g['cuerda']}, Tipo: {g['tipo']}, Peso: {g['peso']}, Color: {g['color']}, Anillo: {g['anillo']}, Placa: {g['placa']}, Ciudad: {g['ciudad']}, # Jaula: {g['numeroJaula']}"
                )
            self.listbox.pack(fill=tk.BOTH, expand=True)

            tk.Button(scroll_frame, text="Emparejar Seleccionados",
                    command=self.emparejar_manual).pack(pady=5)

        tk.Button(scroll_frame, text="Generar PDF",
                command=self.generar_pdf).pack(pady=10)

    def emparejar_manual(self):
        sel = self.listbox.curselection()
        if len(sel) != 2:
            messagebox.showwarning("Selección inválida",
                                   "Selecciona exactamente dos gallos.")
            return
        g1 = self.sin_emparejar[sel[0]]
        g2 = self.sin_emparejar[sel[1]]
        self.peleas_manuales.append((g1, g2))
        messagebox.showinfo(
            "Emparejamiento", f"{g1['frente']} ({g1['cuerda']}) vs {g2['frente']} ({g2['cuerda']})")

    def generar_pdf(self):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Título
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "RESULTADO DEL SORTEO", ln=True, align="C")

            # Logo (opcional)
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

            # Subtítulo
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Lista de Peleas:", ln=True)
            pdf.ln(3)

            # Encabezados
            col_widths = {
                "orden": 10,
                "frente": 12,
                "cuerda": 22,
                "ciudad": 22,
                "color": 18,
                "peso": 12,
                "anillo": 18,
                "placa": 18,
                "tipo": 18,
                "jaula": 12
            }

            headers = ["Orden", "Frente", "Cuerda", "Ciudad", "Color", "Peso", "Anillo", "Placa", "Tipo", "# Jaula"]
            pdf.set_font("Arial", "B", 8)
            for i, header in enumerate(headers):
                pdf.cell(list(col_widths.values())[i], 6, header, border=1, align="C")
            pdf.ln()

            # Datos de las peleas
            peleas = self.peleas_automaticas + self.peleas_manuales
            pdf.set_font("Arial", "", 8)

            for i, (g1, g2) in enumerate(peleas, 1):
                # Primera fila: gallo 1
                pdf.cell(col_widths["orden"], 5, str(i), align="C")
                pdf.cell(col_widths["frente"], 5, g1.get("frente", ""), align="C")
                pdf.cell(col_widths["cuerda"], 5, g1.get("cuerda", ""), align="C")
                pdf.cell(col_widths["ciudad"], 5, g1.get("ciudad", ""), align="C")
                pdf.cell(col_widths["color"], 5, g1.get("color", ""), align="C")
                pdf.cell(col_widths["peso"], 5, str(g1.get("peso", "")), align="C")
                pdf.cell(col_widths["anillo"], 5, g1.get("anillo", ""), align="C")
                pdf.cell(col_widths["placa"], 5, g1.get("placa", ""), align="C")
                pdf.cell(col_widths["tipo"], 5, g1.get("tipo", ""), align="C")
                pdf.cell(col_widths["jaula"], 5, str(g1.get("numeroJaula", "")), align="C")
                pdf.ln()

                # Segunda fila: gallo 2
                pdf.cell(col_widths["orden"], 5,  str(i), align="C")
                pdf.cell(col_widths["frente"], 5, g2.get("frente", ""), align="C")
                pdf.cell(col_widths["cuerda"], 5, g2.get("cuerda", ""), align="C")
                pdf.cell(col_widths["ciudad"], 5, g2.get("ciudad", ""), align="C")
                pdf.cell(col_widths["color"], 5, g2.get("color", ""), align="C")
                pdf.cell(col_widths["peso"], 5, str(g2.get("peso", "")), align="C")
                pdf.cell(col_widths["anillo"], 5, g2.get("anillo", ""), align="C")
                pdf.cell(col_widths["placa"], 5, g2.get("placa", ""), align="C")
                pdf.cell(col_widths["tipo"], 5, g2.get("tipo", ""), align="C")
                pdf.cell(col_widths["jaula"], 5, str(g2.get("numeroJaula", "")), align="C")
                pdf.ln()
                pdf.ln(1)

            # Total de peleas
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Total de Peleas en el Torneo: {len(peleas)}", ln=True)

            # Guardar PDF
            pdf.output("Resultado_Sorteo.pdf")
            messagebox.showinfo("PDF Generado", "Resultado_Sorteo.pdf ha sido creado.")

            # Guardar y cerrar ventana
            self.guardar_callback(peleas)
            self.root.destroy()