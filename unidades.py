import flet as ft
from flet import colors
import mysql.connector

# Conexión a la base de datos
def conectar_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Santiago16_",
            database="farmaciasguadalajara"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

db = conectar_db()
cursor = db.cursor()

# Verificar estructura de la tabla
cursor.execute("SHOW COLUMNS FROM articulos LIKE '%unidad%'")
columna_unidad = cursor.fetchone()
COLUMNA_UNIDADES = columna_unidad[0] if columna_unidad else "idUnidades"

# Funciones CRUD
def crear_unidad(nombre):
    try:
        cursor.execute("INSERT INTO unidades (nombreUnidad) VALUES (%s)", (nombre,))
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error al crear unidad: {err}")
        db.rollback()
        return None

def obtener_unidades():
    try:
        cursor.execute(f"""
            SELECT u.*, COUNT(a.idArticulos) as en_uso 
            FROM unidades u
            LEFT JOIN articulos a ON u.idUnidades = a.{COLUMNA_UNIDADES}
            GROUP BY u.idUnidades
            ORDER BY u.nombreUnidad
        """)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error al obtener unidades: {err}")
        return []

def actualizar_unidad(id_unidad, nombre):
    try:
        cursor.execute(
            "UPDATE unidades SET nombreUnidad=%s WHERE idUnidades=%s",
            (nombre, id_unidad)
        )
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar unidad: {err}")
        db.rollback()
        return False

def eliminar_unidad(id_unidad):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM articulos WHERE {COLUMNA_UNIDADES}=%s", (id_unidad,))
        if cursor.fetchone()[0] > 0:
            return False, "Unidad en uso por artículos"
        
        cursor.execute("DELETE FROM unidades WHERE idUnidades=%s", (id_unidad,))
        db.commit()
        return True, "Unidad eliminada"
    except mysql.connector.Error as err:
        print(f"Error al eliminar unidad: {err}")
        db.rollback()
        return False, f"Error: {err}"

# Interfaz principal
def main(page: ft.Page):
    page.title = "Gestión de Unidades"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Controles
    id_input = ft.TextField(label="ID", read_only=True, width=100)
    nombre_input = ft.TextField(label="Nombre", width=300)
    
    # Lista de unidades
    unidades_list = ft.ListView(expand=True, spacing=10)
    
    # Barra de mensajes
    mensaje = ft.SnackBar(
        ft.Text(), 
        bgcolor=colors.RED_400,
        duration=2000
    )
    page.snack_bar = mensaje

    def mostrar_mensaje(texto, error=True):
        mensaje.content.value = texto
        mensaje.bgcolor = colors.RED_400 if error else colors.GREEN_400
        mensaje.open = True
        page.update()

    def limpiar_formulario():
        id_input.value = ""
        nombre_input.value = ""
        page.update()

    def cargar_unidades():
        unidades_list.controls.clear()
        for unidad in obtener_unidades():
            id_u, nombre, en_uso = unidad[0], unidad[1], unidad[2]
            
            unidades_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(nombre, weight="bold"),
                            ft.Text(f"ID: {id_u} | Artículos: {en_uso}", size=12),
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.EDIT,
                                    on_click=lambda e, id=id_u: cargar_para_editar(id),
                                    tooltip="Editar"
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE,
                                    on_click=lambda e, id=id_u: eliminar_unidad_click(id),
                                    tooltip="Eliminar",
                                    disabled=en_uso > 0
                                )
                            ], alignment="end")
                        ], spacing=5),
                        padding=15,
                        width=400
                    )
                )
            )
        page.update()

    def cargar_para_editar(id_unidad):
        cursor.execute("SELECT * FROM unidades WHERE idUnidades=%s", (id_unidad,))
        unidad = cursor.fetchone()
        if unidad:
            id_input.value = str(unidad[0])
            nombre_input.value = unidad[1]
            page.update()

    def guardar_unidad(e):
        if not nombre_input.value:
            mostrar_mensaje("Nombre es requerido")
            return
            
        if id_input.value:  # Edicion
            if actualizar_unidad(int(id_input.value), nombre_input.value):
                mostrar_mensaje("Unidad actualizada", False)
        else:  # Creacion
            if crear_unidad(nombre_input.value):
                mostrar_mensaje("Unidad creada", False)
        
        limpiar_formulario()
        cargar_unidades()

    def eliminar_unidad_click(id_unidad):
        success, msg = eliminar_unidad(id_unidad)
        mostrar_mensaje(msg, not success)
        cargar_unidades()

    form = ft.Row(
        controls=[
            id_input,
            nombre_input,
            ft.ElevatedButton("Guardar", on_click=guardar_unidad),
            ft.ElevatedButton("Nuevo", on_click=limpiar_formulario)
        ],
        alignment="center",
        spacing=10
    )

    page.add(
        ft.Column([
            ft.Text("Gestión de Unidades", size=24, weight="bold"),
            ft.Divider(),
            form,
            ft.Divider(),
            ft.Text("Listado de Unidades", size=18),
            ft.Container(
                content=unidades_list,
                height=400,
                border=ft.border.all(1),
                padding=10
            )
        ], spacing=15)
    )

    # Carga inicial
    cargar_unidades()

ft.app(target=main)