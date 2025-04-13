import flet as ft
import mysql.connector
from datetime import datetime

# Conexion a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)
cursor = db.cursor()

# Funciones CRUD para Pagos
def crear_pago(monto, fecha, metodo, estado):
    cursor.execute(
        "INSERT INTO pagos (montoPago, fechaPago, metodoPago, estadoPago) VALUES (%s, %s, %s, %s)",
        (monto, fecha, metodo, estado)
    )
    db.commit()

def mostrar_pagos():
    cursor.execute("SELECT * FROM pagos ORDER BY fechaPago DESC")
    return cursor.fetchall()

def editar_pago(id_pago, monto, fecha, metodo, estado):
    cursor.execute(
        "UPDATE pagos SET montoPago=%s, fechaPago=%s, metodoPago=%s, estadoPago=%s WHERE idPagos=%s",
        (monto, fecha, metodo, estado, id_pago)
    )
    db.commit()

def eliminar_pago(id_pago):
    cursor.execute("DELETE FROM pagos WHERE idPagos=%s", (id_pago,))
    db.commit()

# Interfaz de Pagos
def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Gestión de Pagos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F8FF"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Elementos UI
    titulo = ft.Text("Gestión de Pagos", 
                   size=28, 
                   weight="bold", 
                   color="#0066CC",
                   text_align=ft.TextAlign.CENTER)
    
    header = ft.Container(
        ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
        padding=10,
        bgcolor="#E6F2FF",
        border_radius=10
    )
    
    # Campos del formulario
    id_input = ft.TextField(label="ID Pago", border_color="#0066CC", width=400, read_only=True)
    monto_input = ft.TextField(
        label="Monto", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        suffix_text="MXN"
    )
    
    fecha_input = ft.TextField(
        label="Fecha y Hora",
        border_color="#0066CC",
        width=400,
        value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    metodo_input = ft.Dropdown(
        label="Método de Pago",
        border_color="#0066CC",
        width=400,
        options=[
            ft.dropdown.Option("Efectivo"),
            ft.dropdown.Option("Tarjeta de Crédito"),
            ft.dropdown.Option("Tarjeta de Débito"),
            ft.dropdown.Option("Transferencia Bancaria"),
            ft.dropdown.Option("Cheque")
        ]
    )
    
    estado_input = ft.Dropdown(
        label="Estado del Pago",
        border_color="#0066CC",
        width=400,
        options=[
            ft.dropdown.Option("Completado"),
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("Rechazado"),
            ft.dropdown.Option("Cancelado")
        ],
        value="Completado"
    )
    
    # Snackbar para mensajes
    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    # Lista de pagos con scroll
    pagos_list = ft.ListView(
        expand=1,
        spacing=10,
        padding=10,
        auto_scroll=False
    )
    
    # Funciones de eventos
    def limpiar_inputs():
        id_input.value = ""
        monto_input.value = ""
        fecha_input.value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metodo_input.value = None
        estado_input.value = "Completado"
        page.update()
    
    def validar_campos():
        if not monto_input.value.replace('.', '', 1).isdigit():
            return "El monto debe ser un número válido"
        try:
            datetime.strptime(fecha_input.value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "Formato de fecha inválido (YYYY-MM-DD HH:MM:SS)"
        if not metodo_input.value:
            return "Seleccione un método de pago"
        if not estado_input.value:
            return "Seleccione un estado de pago"
        return None
    
    def crear_pago_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_pago(
            float(monto_input.value),
            fecha_input.value,
            metodo_input.value,
            estado_input.value
        )
        limpiar_inputs()
        mostrar_pagos_action(e)
        snackbar.content.value = "Pago registrado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_pagos_action(e):
        pagos_list.controls.clear()
        
        for pago in mostrar_pagos():
            # Determinar color segun estado
            color = {
                "Completado": ft.colors.GREEN,
                "Pendiente": ft.colors.ORANGE,
                "Rechazado": ft.colors.RED,
                "Cancelado": ft.colors.GREY
            }.get(pago[4], ft.colors.BLUE)
            
            pagos_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(f"🆔 ID: {pago[0]}", weight="bold"),
                            ft.Text(f"💰 ${float(pago[1]):,.2f} MXN", size=16),
                            ft.Text(f"📅 {pago[2].strftime('%Y-%m-%d %H:%M:%S') if pago[2] else 'Sin fecha'}"),
                            ft.Text(f"💳 Método: {pago[3]}"),
                            ft.Text(f"🔄 Estado: {pago[4]}", color=color),
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.EDIT,
                                    on_click=lambda e, id=pago[0]: cargar_para_editar(e, id)
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE,
                                    on_click=lambda e, id=pago[0]: eliminar_pago_action(e, id)
                                )
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=5),
                        padding=15,
                        width=400
                    ),
                    color=ft.colors.BLUE_50
                )
            )
        page.update()
    
    def cargar_para_editar(e, id_pago):
        cursor.execute("SELECT * FROM pagos WHERE idPagos=%s", (id_pago,))
        if pago := cursor.fetchone():
            id_input.value = str(pago[0])
            monto_input.value = str(pago[1])
            fecha_input.value = pago[2].strftime("%Y-%m-%d %H:%M:%S") if pago[2] else ""
            metodo_input.value = pago[3]
            estado_input.value = pago[4]
            page.update()
    
    def editar_pago_action(e):
        if not id_input.value:
            snackbar.content.value = "Seleccione un pago para editar"
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        editar_pago(
            int(id_input.value),
            float(monto_input.value),
            fecha_input.value,
            metodo_input.value,
            estado_input.value
        )
        limpiar_inputs()
        mostrar_pagos_action(e)
        snackbar.content.value = "Pago actualizado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def eliminar_pago_action(e, id_pago):
        eliminar_pago(id_pago)
        mostrar_pagos_action(e)
        snackbar.content.value = "Pago eliminado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    

    buttons = ft.Row([
        ft.ElevatedButton(
            "Crear",
            on_click=crear_pago_action,
            bgcolor="#4CAF50",
            color="white",
            height=40,
            width=150
        ),
        ft.ElevatedButton(
            "Guardar",
            on_click=editar_pago_action,
            bgcolor="#2196F3",
            color="white",
            height=40,
            width=150
        ),
        ft.ElevatedButton(
            "Mostrar",
            on_click=mostrar_pagos_action,
            bgcolor="#FF9800",
            color="white",
            height=40,
            width=150
        )
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
    
    page.add(
        ft.Column([
            header,
            ft.Container(
                ft.Column([
                    monto_input,
                    fecha_input,
                    metodo_input,
                    estado_input
                ], spacing=10),
                padding=20,
                alignment=ft.alignment.center
            ),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Registro de Pagos", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                pagos_list,
                padding=10,
                border_radius=10,
                bgcolor="#F5F5F5",
                height=500,
                border=ft.border.all(1, "#E0E0E0"),
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    )

ft.app(target=main)
