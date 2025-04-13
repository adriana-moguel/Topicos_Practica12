import flet as ft
import mysql.connector

# Conexion a la base de datos
db = mysql.connector.connect(
    host="localhost", 
    user="root",        
    password="Santiago16_", 
    database="farmaciasguadalajara"  
)
cursor = db.cursor()

# Funciones CRUD
def crear_cliente(telefono, nombre, correo):
    cursor.execute("INSERT INTO clientes VALUES (%s, %s, %s)", (telefono, nombre, correo))
    db.commit()

def mostrar_clientes():
    cursor.execute("SELECT * FROM clientes")
    return cursor.fetchall()

def editar_cliente(telefono, nombre, correo):
    cursor.execute("UPDATE clientes SET nombre=%s, correo=%s WHERE telefono=%s", (nombre, correo, telefono))
    db.commit()

def eliminar_cliente(telefono):
    cursor.execute("DELETE FROM clientes WHERE telefono=%s", (telefono,))
    db.commit()


def main(page: ft.Page):
    page.title = "Farmacias Guadalajara - Clientes"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F0F8FF"  
    page.padding = 20
    
    # Elementos UI
    titulo = ft.Text("Gestión de Clientes", 
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
    
    telefono_input = ft.TextField(
        label="Teléfono", 
        border_color="#0066CC", 
        width=400,
        input_filter=ft.NumbersOnlyInputFilter(),  # Solo permite numeros
        max_length=10  # max 10 caracteres
    )
    nombre_input = ft.TextField(label="Nombre", border_color="#0066CC", width=400)
    correo_input = ft.TextField(label="Correo", border_color="#0066CC", width=400)
    

    snackbar = ft.SnackBar(
        content=ft.Text("", color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_400,
        duration=2000
    )
    page.snack_bar = snackbar
    
    inputs = ft.Column([telefono_input, nombre_input, correo_input], spacing=10)
    clientes_list = ft.ListView(expand=True, spacing=10)
    
    # Funciones de eventos
    def limpiar_inputs():
        telefono_input.value = ""
        nombre_input.value = ""
        correo_input.value = ""
        page.update()
    
    def validar_telefono(telefono):
        # Verifica que tenga exactamente 10 digitos y sean numeros
        return telefono.isdigit() and len(telefono) == 10
    
    def crear_cliente_action(e):
        if not validar_telefono(telefono_input.value):
            snackbar.content.value = "El teléfono debe tener 10 dígitos numéricos"
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
        
        crear_cliente(telefono_input.value, nombre_input.value, correo_input.value)
        limpiar_inputs()
        mostrar_clientes_action(e)
        snackbar.content.value = "Cliente creado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def mostrar_clientes_action(e):
        clientes_list.controls.clear()
        for cliente in mostrar_clientes():
            clientes_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(f"📱 {cliente[0]}", weight="bold"),
                            ft.Text(f"👤 {cliente[1]}"),
                            ft.Text(f"✉️ {cliente[2]}"),
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, on_click=lambda e, tel=cliente[0]: cargar_para_editar(e, tel)),
                                ft.IconButton(ft.icons.DELETE, on_click=lambda e, tel=cliente[0]: eliminar_cliente_action(e, tel))
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
        cursor.execute("SELECT * FROM clientes WHERE telefono=%s", (telefono,))
        if cliente := cursor.fetchone():
            telefono_input.value = cliente[0]
            nombre_input.value = cliente[1]
            correo_input.value = cliente[2]
            page.update()
    
    def editar_cliente_action(e):
        if not validar_telefono(telefono_input.value):
            snackbar.content.value = "El teléfono debe tener 10 dígitos numéricos"
            snackbar.bgcolor = ft.colors.RED_400
            snackbar.open = True
            page.update()
            return
            
        editar_cliente(telefono_input.value, nombre_input.value, correo_input.value)
        limpiar_inputs()
        mostrar_clientes_action(e)
        snackbar.content.value = "Cliente actualizado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    def eliminar_cliente_action(e, telefono):
        eliminar_cliente(telefono)
        mostrar_clientes_action(e)
        snackbar.content.value = "Cliente eliminado exitosamente"
        snackbar.bgcolor = ft.colors.GREEN_400
        snackbar.open = True
        page.update()
    
    # Botones
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
        create_button("Crear", crear_cliente_action, "#4CAF50"),
        create_button("Guardar", editar_cliente_action, "#2196F3"),
        create_button("Mostrar", mostrar_clientes_action, "#FF9800")
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    
    
    page.add(
        ft.Column([
            header,
            ft.Container(inputs, padding=20, alignment=ft.alignment.center),
            buttons,
            ft.Divider(height=20, color="transparent"),
            ft.Text("Clientes Registrados", size=18, weight="bold", color="#0066CC"),
            ft.Container(clientes_list, padding=10, border_radius=10, bgcolor="#F5F5F5")
        ], spacing=20)
    )

ft.app(target=main)