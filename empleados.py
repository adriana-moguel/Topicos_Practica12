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

# Funciones CRUD para Empleados
def crear_empleado(telefono, nombre, puesto, usuario, salario, sucursal, contra):
    cursor.execute(
        "INSERT INTO empleados VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (telefono, nombre, puesto, usuario, salario, sucursal, contra)
    )
    db.commit()

def mostrar_empleados():
    cursor.execute("SELECT * FROM empleados")
    return cursor.fetchall()

def editar_empleado(telefono, nombre, puesto, usuario, salario, sucursal, contra):
    cursor.execute(
        "UPDATE empleados SET nombre=%s, puesto=%s, usuario=%s, salario=%s, sucursales=%s, contra=%s WHERE telefono=%s",
        (nombre, puesto, usuario, salario, sucursal, contra, telefono)
    )
    db.commit()

def eliminar_empleado(telefono):
    cursor.execute("DELETE FROM empleados WHERE telefono=%s", (telefono,))
    db.commit()

# Interfaz de Empleados
def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Empleados"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F8FF"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO  # Habilita scroll en la página principal
    
    # Elementos UI
    titulo = ft.Text("Gestión de Empleados", 
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
    telefono_input = ft.TextField(
        label="Teléfono", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=10
    )
    nombre_input = ft.TextField(label="Nombre", border_color="#0066CC", width=400)
    puesto_input = ft.TextField(label="Puesto", border_color="#0066CC", width=400)
    usuario_input = ft.TextField(label="Usuario", border_color="#0066CC", width=400)
    salario_input = ft.TextField(
        label="Salario", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    sucursal_input = ft.TextField(
        label="Sucursal (ID)", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    contra_input = ft.TextField(
        label="Contraseña", 
        border_color="#0066CC", 
        width=400,
        password=True,
        can_reveal_password=True
    )
    
    # Snackbar para mensajes
    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    inputs = ft.Column([
        telefono_input, 
        nombre_input, 
        puesto_input, 
        usuario_input,
        salario_input,
        sucursal_input,
        contra_input
    ], spacing=10)
    
    # Lista de empleados con scroll
    empleados_list = ft.ListView(
        expand=True, 
        spacing=10,
        height=400,
        auto_scroll=False
    )
    
    # Funciones de eventos
    def limpiar_inputs():
        for control in [telefono_input, nombre_input, puesto_input, 
                       usuario_input, salario_input, sucursal_input, contra_input]:
            control.value = ""
        page.update()
    
    def validar_telefono(telefono):
        return telefono.isdigit() and len(telefono) == 10
    
    def validar_campos():
        if not validar_telefono(telefono_input.value):
            return "El teléfono debe tener 10 dígitos numéricos"
        if not salario_input.value.replace('.', '', 1).isdigit():
            return "El salario debe ser un número válido"
        if not sucursal_input.value.isdigit():
            return "La sucursal debe ser un ID numérico"
        return None
    
    def crear_empleado_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_empleado(
            telefono_input.value,
            nombre_input.value,
            puesto_input.value,
            usuario_input.value,
            float(salario_input.value),
            int(sucursal_input.value),
            contra_input.value
        )
        limpiar_inputs()
        mostrar_empleados_action(e)
        snackbar.content.value = "Empleado creado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_empleados_action(e):
        empleados_list.controls.clear()
        for emp in mostrar_empleados():
            empleados_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(f"📱 {emp[0]}", weight="bold"),
                            ft.Text(f"👤 {emp[1]}"),
                            ft.Text(f"💼 {emp[2]}"),
                            ft.Text(f"👤 Usuario: {emp[3]}"),
                            ft.Text(f"💰 Salario: ${emp[4]:,.2f}"),
                            ft.Text(f"🏬 Sucursal ID: {emp[5]}"),
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, on_click=lambda e, tel=emp[0]: cargar_para_editar(e, tel)),
                                ft.IconButton(ft.icons.DELETE, on_click=lambda e, tel=emp[0]: eliminar_empleado_action(e, tel))
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=5),
                        padding=15,
                        width=400
                    ),
                    color=ft.colors.BLUE_50
                )
            )
        page.update()
    
    def cargar_para_editar(e, telefono):
        cursor.execute("SELECT * FROM empleados WHERE telefono=%s", (telefono,))
        if emp := cursor.fetchone():
            telefono_input.value = emp[0]
            nombre_input.value = emp[1]
            puesto_input.value = emp[2]
            usuario_input.value = emp[3]
            salario_input.value = str(emp[4])
            sucursal_input.value = str(emp[5])
            contra_input.value = emp[6]
            page.update()
    
    def editar_empleado_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        editar_empleado(
            telefono_input.value,
            nombre_input.value,
            puesto_input.value,
            usuario_input.value,
            float(salario_input.value),
            int(sucursal_input.value),
            contra_input.value
        )
        limpiar_inputs()
        mostrar_empleados_action(e)
        snackbar.content.value = "Empleado actualizado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def eliminar_empleado_action(e, telefono):
        eliminar_empleado(telefono)
        mostrar_empleados_action(e)
        snackbar.content.value = "Empleado eliminado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
  
    def create_button(text, action, color):
        return ft.ElevatedButton(
            text,
            on_click=action,
            bgcolor=color,
            color="white",
            height=40,
            width=150
        )
    
    buttons = ft.Row([
        create_button("Crear", crear_empleado_action, "#4CAF50"),
        create_button("Guardar", editar_empleado_action, "#2196F3"),
        create_button("Mostrar", mostrar_empleados_action, "#FF9800")
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
  
    page.add(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Empleados Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                empleados_list, 
                padding=10, 
                border_radius=10, 
                bgcolor="#F5F5F5",
                height=450,
                border=ft.border.all(1, "#E0E0E0"),
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO) 
    )

ft.app(target=main)