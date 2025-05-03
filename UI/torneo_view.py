import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image

from fpdf import FPDF
import datetime


class TorneoView:
    def __init__(self, parent, db):
        self.db = db
        self.root = tk.Toplevel(parent)
        self.root.title("Desarrollo del Torneo")
        self.root.geometry("800x700")

        self.resultados_pelea = []
        self.estadisticas_por_frente = {}
        self.indice_pelea_actual = 0
        self.lista_de_peleas_cargada = []
        self.corriendo = False
        self.tiempo_total = 0

        self.rojo_timer_corriendo = False
        self.rojo_tiempo_restante = 60
        self.rojo_timer_id = None

        self.azul_timer_corriendo = False
        self.azul_tiempo_restante = 60
        self.azul_timer_id = None

        self.setup_ui()
        self.cargar_lista_de_peleas()

    def setup_ui(self):
        # Reloj Principal primero
        self.frame_reloj = tk.Frame(self.root)
        self.frame_reloj.pack(pady=10)
        self.reloj_label = tk.Label(
            self.frame_reloj, text="0:00", font=("Arial", 48))
        self.reloj_label.pack()
        self.boton_iniciar = tk.Button(
            self.frame_reloj, text="Iniciar Reloj", command=self.iniciar_reloj, font=("Arial", 16))
        self.boton_iniciar.pack(side=tk.LEFT, padx=5)
        self.boton_detener = tk.Button(self.frame_reloj, text="Detener Reloj",
                                       command=self.detener_reloj, font=("Arial", 16), state=tk.DISABLED)
        self.boton_detener.pack(side=tk.LEFT, padx=5)

        self.frame_gallos = tk.Frame(self.root)
        self.frame_gallos.pack(pady=10)

        tk.Label(self.frame_gallos, text="Cinta Roja:", font=(
            "Arial", 12, "bold"), fg="red").pack(anchor="w")
        self.info_rojo_label = tk.Label(
            self.frame_gallos, text="", font=("Arial", 12), justify="left")
        self.info_rojo_label.pack(anchor="w")

        tk.Label(self.frame_gallos, text="Cinta Azul:", font=(
            "Arial", 12, "bold"), fg="blue").pack(anchor="w")
        self.info_azul_label = tk.Label(
            self.frame_gallos, text="", font=("Arial", 12), justify="left")
        self.info_azul_label.pack(anchor="w")

        self.frame_timers = tk.Frame(self.root)
        self.frame_timers.pack(pady=10)

        self.frame_rojo_timer = tk.Frame(self.frame_timers)
        self.frame_rojo_timer.pack(side=tk.LEFT, padx=20)
        self.rojo_timer_label = tk.Label(
            self.frame_rojo_timer, text="1:00", font=("Arial", 24), fg="red")
        self.rojo_timer_label.pack()
        self.boton_iniciar_rojo = tk.Button(
            self.frame_rojo_timer, text="Iniciar Rojo", command=self.iniciar_rojo_timer, font=("Arial", 10))
        self.boton_iniciar_rojo.pack()
        self.boton_detener_rojo = tk.Button(self.frame_rojo_timer, text="Detener Rojo",
                                            command=self.detener_rojo_timer, font=("Arial", 10), state=tk.DISABLED)
        self.boton_detener_rojo.pack()

        self.frame_azul_timer = tk.Frame(self.frame_timers)
        self.frame_azul_timer.pack(side=tk.RIGHT, padx=20)
        self.azul_timer_label = tk.Label(
            self.frame_azul_timer, text="1:00", font=("Arial", 24), fg="blue")
        self.azul_timer_label.pack()
        self.boton_iniciar_azul = tk.Button(
            self.frame_azul_timer, text="Iniciar Azul", command=self.iniciar_azul_timer, font=("Arial", 10))
        self.boton_iniciar_azul.pack()
        self.boton_detener_azul = tk.Button(self.frame_azul_timer, text="Detener Azul",
                                            command=self.detener_azul_timer, font=("Arial", 10), state=tk.DISABLED)
        self.boton_detener_azul.pack()

        self.frame_resultado = tk.Frame(self.root)
        self.frame_resultado.pack(pady=15)

        self.boton_rojo_gana = tk.Button(self.frame_resultado, text="Ganó Rojo",
                                         command=lambda: self.seleccionar_ganador(colorGanador="rojo"), font=("Arial", 14), fg="red")
        self.boton_rojo_gana.pack(side=tk.LEFT, padx=10)

        self.boton_azul_gana = tk.Button(self.frame_resultado, text="Ganó Azul",
                                         command=lambda: self.seleccionar_ganador(colorGanador="azul"), font=("Arial", 14), fg="blue")
        self.boton_azul_gana.pack(side=tk.LEFT, padx=10)

        self.boton_tabla = tk.Button(self.frame_resultado, text="Tabla (Empate)",
                                     command=lambda: self.seleccionar_ganador(esEmpate=True), font=("Arial", 14))
        self.boton_tabla.pack(side=tk.LEFT, padx=10)

        self.resultado_pelea_label = tk.Label(
            self.root, text="Resultado de la Pelea: Sin definir", font=("Arial", 12, "italic"))
        self.resultado_pelea_label.pack(pady=5)

        self.boton_siguiente_pelea = tk.Button(
            self.root, text="Siguiente Pelea", command=self.cargar_siguiente_pelea, font=("Arial", 16), state=tk.DISABLED)
        self.boton_siguiente_pelea.pack(pady=10)

    def iniciar_reloj(self):
        self.corriendo = True
        self.actualizar_reloj()
        self.boton_iniciar.config(state=tk.DISABLED)
        self.boton_detener.config(state=tk.NORMAL)

    def detener_reloj(self):
        self.corriendo = False
        self.boton_iniciar.config(state=tk.NORMAL)
        self.boton_detener.config(state=tk.DISABLED)

    def actualizar_reloj(self):
        if self.corriendo:
            minutos = self.tiempo_total // 60
            segundos = self.tiempo_total % 60
            self.reloj_label.config(text=f"{minutos}:{segundos:02d}")
            self.tiempo_total += 1
            self.root.after(1000, self.actualizar_reloj)

    def iniciar_rojo_timer(self):
        self.rojo_timer_corriendo = True
        self.actualizar_rojo_timer()
        self.boton_iniciar_rojo.config(state=tk.DISABLED)
        self.boton_detener_rojo.config(state=tk.NORMAL)

    def detener_rojo_timer(self):
        self.rojo_timer_corriendo = False
        if self.rojo_timer_id:
            self.root.after_cancel(self.rojo_timer_id)
            self.rojo_timer_id = None
        self.rojo_tiempo_restante = 60
        self.rojo_timer_label.config(text="1:00")
        self.boton_iniciar_rojo.config(state=tk.NORMAL)
        self.boton_detener_rojo.config(state=tk.DISABLED)

    def actualizar_rojo_timer(self):
        if self.rojo_timer_corriendo:
            minutos = self.rojo_tiempo_restante // 60
            segundos = self.rojo_tiempo_restante % 60
            self.rojo_timer_label.config(text=f"{minutos}:{segundos:02d}")
            if self.rojo_tiempo_restante > 0:
                self.rojo_tiempo_restante -= 1
                self.rojo_timer_id = self.root.after(
                    1000, self.actualizar_rojo_timer)
            else:
                self.detener_rojo_timer()

    def iniciar_azul_timer(self):
        self.azul_timer_corriendo = True
        self.actualizar_azul_timer()
        self.boton_iniciar_azul.config(state=tk.DISABLED)
        self.boton_detener_azul.config(state=tk.NORMAL)

    def detener_azul_timer(self):
        self.azul_timer_corriendo = False
        if self.azul_timer_id:
            self.root.after_cancel(self.azul_timer_id)
            self.azul_timer_id = None
        self.azul_tiempo_restante = 60
        self.azul_timer_label.config(text="1:00")
        self.boton_iniciar_azul.config(state=tk.NORMAL)
        self.boton_detener_azul.config(state=tk.DISABLED)

    def actualizar_azul_timer(self):
        if self.azul_timer_corriendo:
            minutos = self.azul_tiempo_restante // 60
            segundos = self.azul_tiempo_restante % 60
            self.azul_timer_label.config(text=f"{minutos}:{segundos:02d}")
            if self.azul_tiempo_restante > 0:
                self.azul_tiempo_restante -= 1
                self.azul_timer_id = self.root.after(
                    1000, self.actualizar_azul_timer)
            else:
                self.detener_azul_timer()

    def seleccionar_ganador(self, colorGanador: str = "", esEmpate: bool = False):
        duracion = self.tiempo_total
        minutos = duracion // 60
        segundos = duracion % 60
        duracion_formateada = f"{minutos}:{segundos:02d}"

        if esEmpate:
            resultado = {
                "ganador_cuerda": "Empate",
                "ganador_frente": "Empate",
                "perdedor_cuerda": "Empate",
                "perdedor_frente": "Empate",
                "tiempo": duracion_formateada,
                "empate": True
            }
        else:
            ganador = self.gallo_rojo if colorGanador == "rojo" else self.gallo_azul
            perdedor = self.gallo_azul if colorGanador == "rojo" else self.gallo_rojo

            resultado = {
                "ganador_cuerda": ganador["cuerda"],
                "ganador_frente": ganador["frente"],
                "perdedor_cuerda": perdedor["cuerda"],
                "perdedor_frente": perdedor["frente"],
                "tiempo": duracion_formateada,
                "empate": False
            }

        self.resultados_pelea.append(resultado)
        self.actualizar_estadisticas(resultado)

        self.resultado_pelea_label.config(
            text=f"Resultado de la Pelea: Ganador - Frente: {resultado['ganador_frente']}, Cuerda: {resultado['ganador_cuerda']} | Perdedor - Frente: {resultado['perdedor_frente']}, Cuerda: {resultado['perdedor_cuerda']} | Tiempo - {resultado['tiempo']}"
        )

        self.tiempo_total = 0
        self.reloj_label.config(text="0:00")

        self.boton_rojo_gana.config(state=tk.DISABLED)
        self.boton_azul_gana.config(state=tk.DISABLED)
        self.boton_tabla.config(state=tk.DISABLED)
        self.boton_siguiente_pelea.config(state=tk.NORMAL)
        self.mostrar_resultados()

    def mostrar_resultados(self):
        ventana_resultados = tk.Toplevel(self.root)
        ventana_resultados.title("Resultados de la Pelea")
        ventana_resultados.geometry("400x300")

        columnas = ["Ganador Cuerda", "Ganador Frente",
                    "Perdedor Cuerda", "Perdedor Frente", "Duración"]
        tabla_resultados = ttk.Treeview(
            ventana_resultados, columns=columnas, show="headings")
        for col in columnas:
            tabla_resultados.heading(col, text=col)
            tabla_resultados.column(col, width=100)
        tabla_resultados.pack(fill=tk.BOTH, expand=True)
        for resultado in self.resultados_pelea:
            ganador_cuerda = resultado.get(
                "ganador_cuerda", resultado.get("ganador", ""))
            ganador_frente = resultado.get(
                "ganador_frente", resultado.get("ganador", ""))
            perdedor_cuerda = resultado.get(
                "perdedor_cuerda", resultado.get("perdedor", ""))
            perdedor_frente = resultado.get(
                "perdedor_frente", resultado.get("perdedor", ""))
            duracion = resultado.get("tiempo", "")

            tabla_resultados.insert("", "end", values=(
                ganador_cuerda, ganador_frente,
                perdedor_cuerda, perdedor_frente,
                duracion
            ))

        tk.Button(ventana_resultados, text="Cerrar",
                  command=ventana_resultados.destroy).pack(pady=10)

    def cargar_lista_de_peleas(self):
        try:
            with open("lista_de_peleas.txt", "r") as archivo:
                self.lista_de_peleas_cargada = []
                for linea in archivo:
                    gallo1_str, gallo2_str = linea.strip().split("|")
                    campos = ['id', 'cuerda', 'frente', 'anillo',
                              'placa', 'color', 'peso', 'ciudad']
                    g1 = dict(zip(campos, gallo1_str.split(",")))
                    g2 = dict(zip(campos, gallo2_str.split(",")))
                    g1['id'], g1['peso'] = int(g1['id']), float(g1['peso'])
                    g2['id'], g2['peso'] = int(g2['id']), float(g2['peso'])
                    self.lista_de_peleas_cargada.append((g1, g2))
                if self.lista_de_peleas_cargada:
                    self.boton_siguiente_pelea.config(state=tk.NORMAL)
                    self.cargar_siguiente_pelea()
        except FileNotFoundError:
            messagebox.showerror(
                "Error", "No se encontró el archivo lista_de_peleas.txt")
            self.boton_siguiente_pelea.config(state=tk.DISABLED)

    def cargar_siguiente_pelea(self):
        if self.indice_pelea_actual < len(self.lista_de_peleas_cargada):
            self.gallo_rojo, self.gallo_azul = self.lista_de_peleas_cargada[
                self.indice_pelea_actual]
            info_rojo = f"Frente: {self.gallo_rojo.get('frente')}, Cuerda: {self.gallo_rojo.get('cuerda')}, Peso: {self.gallo_rojo.get('peso')}, Color: {self.gallo_rojo.get('color')}, Anillo: {self.gallo_rojo.get('anillo')}, Placa: {self.gallo_rojo.get('placa')}, Ciudad: {self.gallo_rojo.get('ciudad')}"
            info_azul = f"Frente: {self.gallo_azul.get('frente')}, Cuerda: {self.gallo_azul.get('cuerda')}, Peso: {self.gallo_azul.get('peso')}, Color: {self.gallo_azul.get('color')}, Anillo: {self.gallo_azul.get('anillo')}, Placa: {self.gallo_azul.get('placa')}, Ciudad: {self.gallo_azul.get('ciudad')}"

            self.info_rojo_label.config(text=info_rojo)
            self.info_azul_label.config(text=info_azul)

            self.detener_rojo_timer()
            self.detener_azul_timer()

            self.boton_rojo_gana.config(state=tk.NORMAL)
            self.boton_azul_gana.config(state=tk.NORMAL)
            self.boton_tabla.config(state=tk.NORMAL)
            self.resultado_pelea_label.config(
                text="Resultado de la Pelea: Sin definir")
            self.boton_siguiente_pelea.config(state=tk.DISABLED)

            self.indice_pelea_actual += 1
        else:
            self.boton_siguiente_pelea.config(
                state=tk.DISABLED, text="Fin de las Peleas")
            self.mostrar_posiciones_acumuladas()


    def actualizar_estadisticas(self, resultado):
        for rol in ["ganador", "perdedor"]:
            clave = (resultado[f"{rol}_cuerda"], resultado[f"{rol}_frente"])
            tiempo = self.tiempo_total

            if clave not in self.estadisticas_por_frente:
                self.estadisticas_por_frente[clave] = {
                    "puntos": 0,
                    "ganadas": 0,
                    "empatadas": 0,
                    "perdidas": 0,
                    "tiempo_total": 0
                }

            stats = self.estadisticas_por_frente[clave]
            stats["tiempo_total"] += tiempo

            if resultado.get("empate"):
                stats["empatadas"] += 1
                stats["puntos"] += 1
            elif rol == "ganador":
                stats["ganadas"] += 1
                stats["puntos"] += 2  # ✅ correcto
            else:
                stats["perdidas"] += 1  # no se suman puntos

    def mostrar_posiciones_acumuladas(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Tabla Acumulada del Torneo")

        columnas = ["Puesto", "Cuerda", "Frente", "Puntos",
                    "Ganadas", "Empatadas", "Perdidas", "Tiempo Total"]
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=100)
        tabla.pack(fill=tk.BOTH, expand=True)

        ordenados = sorted(self.estadisticas_por_frente.items(),
                           key=lambda x: x[1]["puntos"], reverse=True)

        for i, ((cuerda, frente), stats) in enumerate(ordenados, start=1):
            tiempo_str = f"{stats['tiempo_total'] // 60}:{stats['tiempo_total'] % 60:02d}"
            tabla.insert("", "end", values=(
                i, cuerda, frente, stats["puntos"], stats["ganadas"],
                stats["empatadas"], stats["perdidas"], tiempo_str
            ))

        tk.Button(ventana, text="Generar PDF",
                  command=self.generar_pdf_posiciones).pack(pady=10)

    def generar_pdf_posiciones(self):
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)

        pdf.cell(0, 10, "RESULTADO", ln=True, align="C")
        fecha = datetime.date.today().strftime("%A %d de %B de %Y")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, fecha, ln=True, align="C")
        pdf.ln(10)

        columnas = ["#", "NOMBRE", "FRENTE",
                    "PUNTOS", "PG", "PE", "PP", "MIN", "SEG"]
        anchos = [10, 55, 20, 20, 15, 15, 15, 15, 15]

        pdf.set_font("Arial", "B", 10)
        for i, col in enumerate(columnas):
            pdf.cell(anchos[i], 8, col, border=1, align="C")
        pdf.ln()

        ordenados = sorted(self.estadisticas_por_frente.items(),
                           key=lambda x: x[1]["puntos"], reverse=True)

        pdf.set_font("Arial", "", 10)
        for i, ((cuerda, frente), stats) in enumerate(ordenados, start=1):
            minutos = stats["tiempo_total"] // 60
            segundos = stats["tiempo_total"] % 60

            fila = [
                str(i),
                cuerda.upper(),
                str(frente),
                str(stats["puntos"]),
                str(stats["ganadas"]),
                str(stats["empatadas"]),
                str(stats["perdidas"]),
                str(minutos),
                f"{segundos:02d}"
            ]

            for j, dato in enumerate(fila):
                pdf.cell(anchos[j], 8, dato, border=1, align="C")
            pdf.ln()

        nombre_archivo = "Posiciones_Finales_Torneo.pdf"
        pdf.output(nombre_archivo)
        messagebox.showinfo(
            "PDF generado", f"{nombre_archivo} ha sido creado correctamente.")
