import flet as ft
import mysql.connector

# Conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)
cursor = db.cursor()

def crear_sucursal(id_sucursal, nombre, direccion, telefono, correo):
    cursor.execute(
        "INSERT INTO sucursales VALUES (%s, %s, %s, %s, %s)",
        (id_sucursal, nombre, direccion, telefono, correo)
    )
    db.commit()

def mostrar_sucursales():
    cursor.execute("SELECT * FROM sucursales ORDER BY nombreSucursal")
    return cursor.fetchall()

def editar_sucursal(id_sucursal, nombre, direccion, telefono, correo):
    cursor.execute(
        "UPDATE sucursales SET nombreSucursal=%s, direccion=%s, telefono=%s, correoElectronico=%s WHERE idSucursales=%s",
        (nombre, direccion, telefono, correo, id_sucursal)
    )
    db.commit()

def eliminar_sucursal(id_sucursal):
    cursor.execute("DELETE FROM sucursales WHERE idSucursales=%s", (id_sucursal,))
    db.commit()

def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Gestión de Sucursales"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F8FF"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Elementos UI
    titulo = ft.Text("Gestión de Sucursales", 
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
    id_input = ft.TextField(
        label="ID Sucursal", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    nombre_input = ft.TextField(
        label="Nombre Sucursal", 
        border_color="#0066CC", 
        width=400
    )
    direccion_input = ft.TextField(
        label="Dirección", 
        border_color="#0066CC", 
        width=400
    )
    telefono_input = ft.TextField(
        label="Teléfono", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=10
    )
    correo_input = ft.TextField(
        label="Correo Electrónico", 
        border_color="#0066CC", 
        width=400
    )
    
    
    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    #  scroll
    sucursales_list = ft.ListView(
        expand=1,
        spacing=10,
        padding=10,
        auto_scroll=False
    )
    
    # Funciones de eventos
    def limpiar_inputs():
        for control in [id_input, nombre_input, direccion_input, telefono_input, correo_input]:
            control.value = ""
        page.update()
    
    def validar_campos():
        if not id_input.value.isdigit():
            return "El ID debe ser un número"
        if not telefono_input.value.isdigit() or len(telefono_input.value) != 10:
            return "El teléfono debe tener 10 dígitos numéricos"
        if "@" not in correo_input.value or "." not in correo_input.value:
            return "Ingrese un correo electrónico válido"
        return None
    
    def crear_sucursal_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_sucursal(
            int(id_input.value),
            nombre_input.value,
            direccion_input.value,
            telefono_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_sucursales_action(e)
        snackbar.content.value = "Sucursal creada exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_sucursales_action(e):
        sucursales_list.controls.clear()
        
        for suc in mostrar_sucursales():
            sucursales_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(f"🏬 {suc[1]}", size=18, weight="bold"),
                            ft.Text(f"🆔 ID: {suc[0]}"),
                            ft.Text(f"📍 {suc[2]}"),
                            ft.Text(f"📞 {suc[3]}"),
                            ft.Text(f"✉️ {suc[4]}"),
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.EDIT,
                                    on_click=lambda e, id=suc[0]: cargar_para_editar(e, id)
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE,
                                    on_click=lambda e, id=suc[0]: eliminar_sucursal_action(e, id)
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
    
    def cargar_para_editar(e, id_sucursal):
        cursor.execute("SELECT * FROM sucursales WHERE idSucursales=%s", (id_sucursal,))
        if suc := cursor.fetchone():
            id_input.value = str(suc[0])
            nombre_input.value = suc[1]
            direccion_input.value = suc[2]
            telefono_input.value = suc[3]
            correo_input.value = suc[4]
            page.update()
    
    def editar_sucursal_action(e):
        if not id_input.value:
            snackbar.content.value = "Seleccione una sucursal para editar"
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
            
        editar_sucursal(
            int(id_input.value),
            nombre_input.value,
            direccion_input.value,
            telefono_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_sucursales_action(e)
        snackbar.content.value = "Sucursal actualizada exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def eliminar_sucursal_action(e, id_sucursal):
        eliminar_sucursal(id_sucursal)
        mostrar_sucursales_action(e)
        snackbar.content.value = "Sucursal eliminada exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    

    buttons = ft.Row([
        ft.ElevatedButton(
            "Crear",
            on_click=crear_sucursal_action,
            bgcolor="#4CAF50",
            color="white",
            height=40,
            width=150
        ),
        ft.ElevatedButton(
            "Guardar",
            on_click=editar_sucursal_action,
            bgcolor="#2196F3",
            color="white",
            height=40,
            width=150
        ),
        ft.ElevatedButton(
            "Mostrar",
            on_click=mostrar_sucursales_action,
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
                    id_input,
                    nombre_input,
                    direccion_input,
                    telefono_input,
                    correo_input
                ], spacing=10),
                padding=20,
                alignment=ft.alignment.center
            ),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Sucursales Registradas", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                sucursales_list,
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