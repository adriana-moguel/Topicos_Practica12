import flet as ft
import mysql.connector

# Conexión a la base de datos (la misma que usaste para empleados)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Santiago16_",
    database="farmaciasguadalajara"
)
cursor = db.cursor()

# Funciones CRUD para Proveedores
def crear_proveedor(id_proveedor, nombre, telefono, direccion, correo):
    cursor.execute(
        "INSERT INTO proveedores VALUES (%s, %s, %s, %s, %s)",
        (id_proveedor, nombre, telefono, direccion, correo)
    )
    db.commit()

def mostrar_proveedores():
    cursor.execute("SELECT * FROM proveedores")
    return cursor.fetchall()

def editar_proveedor(id_proveedor, nombre, telefono, direccion, correo):
    cursor.execute(
        "UPDATE proveedores SET nombre=%s, telefono=%s, direccion=%s, correoElectronico=%s WHERE idProveedores=%s",
        (nombre, telefono, direccion, correo, id_proveedor)
    )
    db.commit()

def eliminar_proveedor(id_proveedor):
    cursor.execute("DELETE FROM proveedores WHERE idProveedores=%s", (id_proveedor,))
    db.commit()

# Interfaz de Proveedores
def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Proveedores"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F8FF"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Elementos UI
    titulo = ft.Text("Gestión de Proveedores", 
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
        label="ID Proveedor", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    nombre_input = ft.TextField(label="Nombre", border_color="#0066CC", width=400)
    telefono_input = ft.TextField(
        label="Teléfono", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),
        max_length=10
    )
    direccion_input = ft.TextField(label="Dirección", border_color="#0066CC", width=400)
    correo_input = ft.TextField(label="Correo Electrónico", border_color="#0066CC", width=400)
    
    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    inputs = ft.Column([
        id_input,
        nombre_input,
        telefono_input,
        direccion_input,
        correo_input
    ], spacing=10)
    
    # Lista de proveedores con scroll
    proveedores_list = ft.ListView(
        expand=True,
        spacing=10,
        height=400,
        auto_scroll=False
    )
   
    def limpiar_inputs():
        for control in [id_input, nombre_input, telefono_input, direccion_input, correo_input]:
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
    
    def crear_proveedor_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_proveedor(
            int(id_input.value),
            nombre_input.value,
            telefono_input.value,
            direccion_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_proveedores_action(e)
        snackbar.content.value = "Proveedor creado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_proveedores_action(e):
        proveedores_list.controls.clear()
        for prov in mostrar_proveedores():
            proveedores_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(f"🆔 ID: {prov[0]}", weight="bold"),
                            ft.Text(f"🏢 {prov[1]}"),
                            ft.Text(f"📱 {prov[2]}"),
                            ft.Text(f"📍 {prov[3]}"),
                            ft.Text(f"✉️ {prov[4]}"),
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, on_click=lambda e, id=prov[0]: cargar_para_editar(e, id)),
                                ft.IconButton(ft.icons.DELETE, on_click=lambda e, id=prov[0]: eliminar_proveedor_action(e, id))
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=5),
                        padding=15,
                        width=400
                    ),
                    color=ft.colors.BLUE_50
                )
            )
        page.update()
    
    def cargar_para_editar(e, id_proveedor):
        cursor.execute("SELECT * FROM proveedores WHERE idProveedores=%s", (id_proveedor,))
        if prov := cursor.fetchone():
            id_input.value = str(prov[0])
            nombre_input.value = prov[1]
            telefono_input.value = prov[2]
            direccion_input.value = prov[3]
            correo_input.value = prov[4]
            page.update()
    
    def editar_proveedor_action(e):
        error = validar_campos()
        if error:
            snackbar.content.value = error
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        editar_proveedor(
            int(id_input.value),
            nombre_input.value,
            telefono_input.value,
            direccion_input.value,
            correo_input.value
        )
        limpiar_inputs()
        mostrar_proveedores_action(e)
        snackbar.content.value = "Proveedor actualizado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def eliminar_proveedor_action(e, id_proveedor):
        eliminar_proveedor(id_proveedor)
        mostrar_proveedores_action(e)
        snackbar.content.value = "Proveedor eliminado exitosamente"
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
        create_button("Crear", crear_proveedor_action, "#4CAF50"),
        create_button("Guardar", editar_proveedor_action, "#2196F3"),
        create_button("Mostrar", mostrar_proveedores_action, "#FF9800")
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
   
    page.add(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Proveedores Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(
                proveedores_list,
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