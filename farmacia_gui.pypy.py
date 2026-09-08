import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

ARCHIVO_INVENTARIO = "inventario.txt"
ARCHIVO_VENTAS = "ventas.txt"
PORCENTAJE_COMISION = 0.05


class ModeloFarmacia:
    def __init__(self):
        self.inventario = {}
        self.ventas_dia = []
        self.cargar_datos()

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_INVENTARIO):
            self.inventario = {
                "101": {"nombre": "Paracetamol 500mg", "precio": 4.50, "stock": 50},
                "102": {"nombre": "Ibuprofeno 400mg", "precio": 6.20, "stock": 35},
                "103": {"nombre": "Amoxicilina 500mg", "precio": 12.80, "stock": 20},
            }
            return

        with open(ARCHIVO_INVENTARIO, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    partes = linea.split(",")
                    if len(partes) == 4:
                        id_med, nombre, precio, stock = partes
                        self.inventario[id_med] = {
                            "nombre": nombre,
                            "precio": float(precio),
                            "stock": int(stock)
                        }

    def guardar_datos(self):
        with open(ARCHIVO_INVENTARIO, "w", encoding="utf-8") as f:
            for id_med, datos in self.inventario.items():
                f.write(f"{id_med},{datos['nombre']},{datos['precio']:.2f},{datos['stock']}\n")

        if self.ventas_dia:
            with open(ARCHIVO_VENTAS, "a", encoding="utf-8") as f:
                for v in self.ventas_dia:
                    f.write(f"{v['id']},{v['nombre']},{v['cantidad']},{v['total']:.2f},{v['comision']:.2f},{v['fecha']}\n")

    def registrar_venta(self, id_med, cantidad):
        if id_med not in self.inventario:
            return False, "Medicamento no encontrado."

        item = self.inventario[id_med]
        if item["stock"] < cantidad:
            return False, f"Stock insuficiente. Disponible: {item['stock']}"

        item["stock"] -= cantidad
        total = cantidad * item["precio"]
        comision = total * PORCENTAJE_COMISION
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        registro = {
            "id": id_med,
            "nombre": item["nombre"],
            "cantidad": cantidad,
            "total": total,
            "comision": comision,
            "fecha": fecha
        }
        self.ventas_dia.append(registro)
        return True, f"Venta exitosa: ${total:.2f} (Comisión: ${comision:.2f})"

    def agregar_o_actualizar(self, id_med, nombre, precio, cantidad):
        if id_med in self.inventario:
            self.inventario[id_med]["stock"] += cantidad
            self.inventario[id_med]["precio"] = precio
            if nombre:
                self.inventario[id_med]["nombre"] = nombre
        else:
            self.inventario[id_med] = {"nombre": nombre, "precio": precio, "stock": cantidad}


class FarmaciaGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Farmacias")
        self.geometry("800x550")
        self.minsize(700, 450)

        self.modelo = ModeloFarmacia()

        # Configurar guardado automático al cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        self._crear_widgets()
        self.actualizar_tabla_inventario()

    def _crear_widgets(self):
        # Contenedor de pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Pestaña Inventario
        tab_inventario = ttk.Frame(notebook)
        notebook.add(tab_inventario, text="Inventario y Stock")
        self._construir_tab_inventario(tab_inventario)

        # 2. Pestaña Ventas
        tab_ventas = ttk.Frame(notebook)
        notebook.add(tab_ventas, text="Terminal de Ventas")
        self._construir_tab_ventas(tab_ventas)

        # 3. Pestaña Reporte del Día
        tab_reporte = ttk.Frame(notebook)
        notebook.add(tab_reporte, text="Cierre y Comisiones")
        self._construir_tab_reporte(tab_reporte)

    def _construir_tab_inventario(self, parent):
        # Tabla Treeview
        columnas = ("id", "nombre", "precio", "stock")
        self.tree = ttk.Treeview(parent, columns=columnas, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Medicamento")
        self.tree.heading("precio", text="Precio ($)")
        self.tree.heading("stock", text="Stock")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nombre", width=250)
        self.tree.column("precio", width=100, anchor="e")
        self.tree.column("stock", width=80, anchor="center")

        scroll = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="top", fill="both", expand=True, pady=(0, 10))
        scroll.pack(side="right", fill="y")

        # Formulario de alta/reposición
        frame_form = ttk.LabelFrame(parent, text="Agregar o Reponer Medicamento", padding=10)
        frame_form.pack(fill="x", pady=5)

        ttk.Label(frame_form, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_id = ttk.Entry(frame_form, width=10)
        self.entry_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_nombre = ttk.Entry(frame_form, width=20)
        self.entry_nombre.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_form, text="Precio ($):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.entry_precio = ttk.Entry(frame_form, width=10)
        self.entry_precio.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frame_form, text="Cantidad:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.entry_stock = ttk.Entry(frame_form, width=10)
        self.entry_stock.grid(row=0, column=7, padx=5, pady=5)

        btn_guardar_item = ttk.Button(frame_form, text="Guardar / Actualizar", command=self._accion_guardar_stock)
        btn_guardar_item.grid(row=0, column=8, padx=10, pady=5)

    def _construir_tab_ventas(self, parent):
        frame_venta = ttk.LabelFrame(parent, text="Registrar Operación", padding=20)
        frame_venta.pack(fill="x", padx=20, pady=20)

        ttk.Label(frame_venta, text="ID del Medicamento:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_venta_id = ttk.Entry(frame_venta, width=15)
        self.entry_venta_id.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame_venta, text="Cantidad a Vender:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_venta_cantidad = ttk.Entry(frame_venta, width=15)
        self.entry_venta_cantidad.grid(row=1, column=1, padx=10, pady=10)

        btn_vender = ttk.Button(frame_venta, text="Procesar Venta", command=self._accion_vender)
        btn_vender.grid(row=2, column=0, columnspan=2, pady=15)

    def _construir_tab_reporte(self, parent):
        frame_rep = ttk.Frame(parent, padding=20)
        frame_rep.pack(fill="both", expand=True)

        self.lbl_ventas_count = ttk.Label(frame_rep, text="Total Transacciones: 0", font=("Helvetica", 11))
        self.lbl_ventas_count.pack(anchor="w", pady=5)

        self.lbl_ingresos = ttk.Label(frame_rep, text="Ingresos Brutos: $0.00", font=("Helvetica", 11))
        self.lbl_ingresos.pack(anchor="w", pady=5)

        self.lbl_comisiones = ttk.Label(frame_rep, text="Comisiones Generadas (5%): $0.00", font=("Helvetica", 11))
        self.lbl_comisiones.pack(anchor="w", pady=5)

        self.lbl_neto = ttk.Label(frame_rep, text="Ingreso Neto: $0.00", font=("Helvetica", 11, "bold"))
        self.lbl_neto.pack(anchor="w", pady=5)

        ttk.Button(frame_rep, text="Actualizar Métricas", command=self.actualizar_reporte).pack(anchor="w", pady=15)

    # --- Acciones y Controladores ---

    def actualizar_tabla_inventario(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for id_med, d in self.modelo.inventario.items():
            self.tree.insert("", "end", values=(id_med, d["nombre"], f"{d['precio']:.2f}", d["stock"]))

    def _accion_guardar_stock(self):
        id_med = self.entry_id.get().strip()
        nombre = self.entry_nombre.get().strip()
        try:
            precio = float(self.entry_precio.get())
            cantidad = int(self.entry_stock.get())
            if not id_med or not nombre:
                messagebox.showwarning("Atención", "ID y Nombre son obligatorios.")
                return
            if precio <= 0 or cantidad < 0:
                messagebox.showwarning("Atención", "Precio debe ser > 0 y cantidad >= 0.")
                return

            self.modelo.agregar_o_actualizar(id_med, nombre, precio, cantidad)
            self.actualizar_tabla_inventario()
            messagebox.showinfo("Éxito", f"Producto '{nombre}' registrado/actualizado.")

            self.entry_id.delete(0, tk.END)
            self.entry_nombre.delete(0, tk.END)
            self.entry_precio.delete(0, tk.END)
            self.entry_stock.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Precio y Cantidad deben ser valores numéricos válidos.")

    def _accion_vender(self):
        id_med = self.entry_venta_id.get().strip()
        try:
            cantidad = int(self.entry_venta_cantidad.get())
            if cantidad <= 0:
                messagebox.showwarning("Atención", "La cantidad debe ser mayor a 0.")
                return

            exito, msg = self.modelo.registrar_venta(id_med, cantidad)
            if exito:
                messagebox.showinfo("Venta Realizada", msg)
                self.actualizar_tabla_inventario()
                self.actualizar_reporte()
                self.entry_venta_id.delete(0, tk.END)
                self.entry_venta_cantidad.delete(0, tk.END)
            else:
                messagebox.showerror("Error de Venta", msg)
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad entera válida.")

    def actualizar_reporte(self):
        ventas = self.modelo.ventas_dia
        total_ingresos = sum(v["total"] for v in ventas)
        total_comisiones = sum(v["comision"] for v in ventas)
        total_neto = total_ingresos - total_comisiones

        self.lbl_ventas_count.config(text=f"Total Transacciones: {len(ventas)}")
        self.lbl_ingresos.config(text=f"Ingresos Brutos: ${total_ingresos:.2f}")
        self.lbl_comisiones.config(text=f"Comisiones Generadas (5%): ${total_comisiones:.2f}")
        self.lbl_neto.config(text=f"Ingreso Neto: ${total_neto:.2f}")

    def al_cerrar(self):
        self.modelo.guardar_datos()
        self.destroy()


if __name__ == "__main__":
    app = FarmaciaGUI()
    app.mainloop()