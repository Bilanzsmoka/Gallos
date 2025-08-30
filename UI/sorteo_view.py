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
        self.debug = True
        self._debug_lines = []
        self.realizar_sorteo()
        self.mostrar_resultados()
    
    # 👇 helper de depuración
    def _dbg(self, msg: str):
        if getattr(self, "debug", False):
            print(msg)
            # guarda para mostrarlos luego en una ventanita si quieres
            self._debug_lines.append(str(msg))


    # ---- Helpers ----
    @staticmethod
    def _peso_a_centesimas(valor):
        """
        Convierte un valor de peso (str/float) a centésimas (int).
        Maneja comas/puntos y múltiples separadores. 3.01 -> 301
        """
        if valor is None:
            return None
        s = str(valor).strip().replace(',', '.')
        if not s:
            return None
        # Si hay varios '.', deja el último como decimal (los anteriores son miles)
        if s.count('.') > 1:
            head, _, tail = s.rpartition('.')
            s = head.replace('.', '') + '.' + tail
        try:
            return int(round(float(s) * 100))
        except Exception:
            return None
    @staticmethod
    def cuerda_base(c):
            if c is None:
                return ""
            s = str(c).strip()
            base = s.split("_", 1)[0]      # toma solo lo que va antes del primer "_"
            return base.casefold()  
    # ---- Lógica del sorteo ----
    def realizar_sorteo(self):
        UMBRAL = 1  # 1 centésima = 0.01 kg

        gallos = []
        for g in self.gallos_detalles:
            pc = self._peso_a_centesimas(g.get('peso'))
            gallos.append({
                'id': g['id'],
                'cuerda': g['cuerda'],
                'frente': g['frente'],
                'anillo': g['anillo'],
                'placa': g['placa'],
                'color': g['color'],
                'peso_int': pc,                                   # int (centésimas)
                'peso_fmt': f"{pc/100:.2f}" if pc is not None else "",
                'peso': g.get('peso', ''),
                'ciudad': g['ciudad'],
                'tipo': g['tipo'],
                'numeroJaula': g.get('numeroJaula', '')
            })

        # Ordena por peso (los None al final)
        gallos.sort(key=lambda x: (x['peso_int'] is None, x['peso_int'] or 0))
        usados = [False] * len(gallos)

        for i in range(len(gallos)):
            if usados[i] or gallos[i]['peso_int'] is None:
                continue

            g1 = gallos[i]
            usados[i] = True
            match = False

            for j in range(i + 1, len(gallos)):
                if usados[j] or gallos[j]['peso_int'] is None:
                    continue
                
                g2 = gallos[j]
                p1 = g1.get('peso_int')
                p2 = g2.get('peso_int')
                diff = None if (p1 is None or p2 is None) else abs(p1 - p2)
                
                #breakpoint()
                if (
                    g1['tipo'] == g2['tipo'] and
                    self.cuerda_base(g1['cuerda']) != self.cuerda_base(g2['cuerda'])  and
                    diff is not None and diff <= UMBRAL 
                ):
                    self.peleas_automaticas.append((g1, g2))
                    usados[j] = True
                    match = True
                    break

            if not match:
                self.sin_emparejar.append(g1)

    # ---- UI ----
    def mostrar_resultados(self):
        # Contenedor con canvas para scroll
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scroll_frame, text="Peleas Encontradas (Automáticamente):",
                 font=("Arial", 12, "bold")).pack(pady=5)

        if self.peleas_automaticas:
            for g1, g2 in self.peleas_automaticas:
                tk.Label(
                    scroll_frame,
                    text=(
                        f"Frente: {g1['frente']}, Cuerda: {g1['cuerda']}, Tipo: {g1['tipo']}, "
                        f"Peso: {g1['peso_fmt']}, Color: {g1['color']}, Anillo: {g1['anillo']}, "
                        f"Placa: {g1['placa']}, Ciudad: {g1['ciudad']}, # Jaula: {g1['numeroJaula']} "
                        f"vs "
                        f"Frente: {g2['frente']}, Cuerda: {g2['cuerda']}, Tipo: {g2['tipo']}, "
                        f"Peso: {g2['peso_fmt']}, Color: {g2['color']}, Anillo: {g2['anillo']}, "
                        f"Placa: {g2['placa']}, Ciudad: {g2['ciudad']}, # Jaula: {g2['numeroJaula']}"
                    )
                ).pack(anchor="w")
        else:
            tk.Label(scroll_frame, text="No se encontraron peleas automáticamente.").pack()

        tk.Label(scroll_frame, text="\nGallos sin Emparejar:",
                 font=("Arial", 12, "bold")).pack(pady=5)

        if self.sin_emparejar:
            self.listbox = tk.Listbox(
                scroll_frame,
                selectmode=tk.MULTIPLE,
                height=12,
                font=("Arial", 11),
                width=150
            )
            for g in self.sin_emparejar:
                self.listbox.insert(
                    tk.END,
                    f"Frente: {g['frente']}, Cuerda: {g['cuerda']}, Tipo: {g['tipo']}, "
                    f"Peso: {g['peso_fmt']}, Color: {g['color']}, Anillo: {g['anillo']}, "
                    f"Placa: {g['placa']}, Ciudad: {g['ciudad']}, # Jaula: {g['numeroJaula']}"
                )
            self.listbox.pack(fill=tk.BOTH, expand=True)

            tk.Button(scroll_frame, text="Emparejar Seleccionados",
                      command=self.emparejar_manual).pack(pady=5)

        tk.Button(scroll_frame, text="Generar PDF",
                  command=self.generar_pdf).pack(pady=10)

    def emparejar_manual(self):
        sel = self.listbox.curselection()
        if len(sel) != 2:
            messagebox.showwarning("Selección inválida", "Selecciona exactamente dos gallos.")
            return
        g1 = self.sin_emparejar[sel[0]]
        g2 = self.sin_emparejar[sel[1]]
        if g1['cuerda'] == g2['cuerda']:
            messagebox.showwarning("Emparejamiento inválido", "No puedes emparejar gallos de la misma cuerda.")
            return
        self.peleas_manuales.append((g1, g2))
        messagebox.showinfo("Emparejamiento", f"{g1['frente']} ({g1['cuerda']}) vs {g2['frente']} ({g2['cuerda']})")
           # ignora mayúsculas/minúsculas
    # ---- PDF ----
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
            # Fila: gallo 1
            pdf.cell(col_widths["orden"], 5, str(i), align="C")
            pdf.cell(col_widths["frente"], 5, g1.get("frente", ""), align="C")
            pdf.cell(col_widths["cuerda"], 5, g1.get("cuerda", ""), align="C")
            pdf.cell(col_widths["ciudad"], 5, g1.get("ciudad", ""), align="C")
            pdf.cell(col_widths["color"], 5, g1.get("color", ""), align="C")
            pdf.cell(col_widths["peso"], 5, g1.get("peso_fmt", ""), align="C")
            pdf.cell(col_widths["anillo"], 5, g1.get("anillo", ""), align="C")
            pdf.cell(col_widths["placa"], 5, g1.get("placa", ""), align="C")
            pdf.cell(col_widths["tipo"], 5, g1.get("tipo", ""), align="C")
            pdf.cell(col_widths["jaula"], 5, str(g1.get("numeroJaula", "")), align="C")
            pdf.ln()

            # Fila: gallo 2
            pdf.cell(col_widths["orden"], 5, str(i), align="C")
            pdf.cell(col_widths["frente"], 5, g2.get("frente", ""), align="C")
            pdf.cell(col_widths["cuerda"], 5, g2.get("cuerda", ""), align="C")
            pdf.cell(col_widths["ciudad"], 5, g2.get("ciudad", ""), align="C")
            pdf.cell(col_widths["color"], 5, g2.get("color", ""), align="C")
            pdf.cell(col_widths["peso"], 5, g2.get("peso_fmt", ""), align="C")
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
