import flet as ft
from flet import Colors
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


def detectar_columna_categoria():
    cursor.execute("SHOW COLUMNS FROM articulos LIKE '%categoria%'")
    columna = cursor.fetchone()
    if columna:
        return columna[0]  
    return None

COLUMNA_CATEGORIA = detectar_columna_categoria()

def crear_categoria(nombre):
    try:
        cursor.execute(
            "INSERT INTO categorias (nombre) VALUES (%s)",
            (nombre,)
        )
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error al crear categoría: {err}")
        db.rollback()
        return None

def obtener_categorias():
    try:
        if COLUMNA_CATEGORIA:
            cursor.execute(f"""
                SELECT c.*, COUNT(a.idArticulos) as en_uso 
                FROM categorias c
                LEFT JOIN articulos a ON c.idCategorias = a.{COLUMNA_CATEGORIA}
                GROUP BY c.idCategorias
                ORDER BY c.nombre
            """)
        else:
            cursor.execute("""
                SELECT c.*, 0 as en_uso 
                FROM categorias c
                ORDER BY c.nombre
            """)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error al obtener categorías: {err}")
        return []

def actualizar_categoria(id_categoria, nombre):
    try:
        cursor.execute(
            "UPDATE categorias SET nombre=%s WHERE idCategorias=%s",
            (nombre, id_categoria)
        )
        db.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error al actualizar categoría: {err}")
        db.rollback()
        return False

def eliminar_categoria(id_categoria):
    try:
        if COLUMNA_CATEGORIA:
            cursor.execute(f"SELECT COUNT(*) FROM articulos WHERE {COLUMNA_CATEGORIA}=%s", (id_categoria,))
            if cursor.fetchone()[0] > 0:
                return False, "No se puede eliminar: categoría en uso por artículos"
        
        cursor.execute("DELETE FROM categorias WHERE idCategorias=%s", (id_categoria,))
        db.commit()
        return True, "Categoría eliminada correctamente"
    except mysql.connector.Error as err:
        print(f"Error al eliminar categoría: {err}")
        db.rollback()
        return False, f"Error al eliminar: {err}"

def main(page: ft.Page):
    page.title = "Gestión de Categorías"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    id_input = ft.TextField(label="ID", read_only=True, width=100, border_color=Colors.BLUE_400)
    nombre_input = ft.TextField(label="Nombre", width=300, border_color=Colors.BLUE_400)

    categorias_list = ft.ListView(expand=True, spacing=10)
    
    
    mensaje = ft.SnackBar(
        ft.Text(), 
        bgcolor=Colors.RED_400,
        duration=2000
    )
    page.snack_bar = mensaje

    def mostrar_mensaje(texto, error=True):
        mensaje.content.value = texto
        mensaje.bgcolor = Colors.RED_400 if error else Colors.GREEN_400
        mensaje.open = True
        page.update()

    def limpiar_formulario():
        id_input.value = ""
        nombre_input.value = ""
        page.update()

    def cargar_categorias():
        categorias_list.controls.clear()
        for cat in obtener_categorias():
            id_cat, nombre, en_uso = cat[0], cat[1], cat[2]
            
            categorias_list.controls.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(nombre, weight="bold", size=16),
                            ft.Text(f"ID: {id_cat} | Artículos: {en_uso}", size=12),
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.EDIT,
                                    on_click=lambda e, id=id_cat: cargar_para_editar(id),
                                    icon_color=Colors.BLUE_600,
                                    tooltip="Editar"
                                ),
                                ft.IconButton(
                                    ft.icons.DELETE,
                                    on_click=lambda e, id=id_cat: eliminar_categoria_click(id),
                                    icon_color=Colors.RED_600,
                                    tooltip="Eliminar",
                                    disabled=en_uso > 0 if COLUMNA_CATEGORIA else False
                                )
                            ], alignment="end")
                        ], spacing=5),
                        padding=15,
                        width=400
                    ),
                    elevation=3
                )
            )
        page.update()

    def cargar_para_editar(id_categoria):
        cursor.execute("SELECT * FROM categorias WHERE idCategorias=%s", (id_categoria,))
        categoria = cursor.fetchone()
        if categoria:
            id_input.value = str(categoria[0])
            nombre_input.value = categoria[1]
            page.update()

    def guardar_categoria(e):
        if not nombre_input.value:
            mostrar_mensaje("El nombre es requerido")
            return
            
        if id_input.value:  
            if actualizar_categoria(int(id_input.value), nombre_input.value):
                mostrar_mensaje("Categoría actualizada", False)
        else:  
            if crear_categoria(nombre_input.value):
                mostrar_mensaje("Categoría creada", False)
        
        limpiar_formulario()
        cargar_categorias()

    def eliminar_categoria_click(id_categoria):
        success, msg = eliminar_categoria(id_categoria)
        mostrar_mensaje(msg, not success)
        cargar_categorias()

   
    form = ft.Row(
        controls=[
            id_input,
            nombre_input,
            ft.ElevatedButton("Guardar", on_click=guardar_categoria, 
                            bgcolor=Colors.BLUE_500, color=Colors.WHITE),
            ft.ElevatedButton("Nuevo", on_click=limpiar_formulario,
                            bgcolor=Colors.GREY_300),
            ft.ElevatedButton("Mostrar", on_click=lambda e: cargar_categorias(),
                            bgcolor=Colors.ORANGE_400, color=Colors.WHITE)
        ],
        alignment="center",
        spacing=10
    )

    page.add(
        ft.Column([
            ft.Text("Gestión de Categorías", size=24, weight="bold", color=Colors.BLUE_700),
            ft.Divider(height=10, color=Colors.BLUE_GREY_100),
            form,
            ft.Divider(height=10, color=Colors.BLUE_GREY_100),
            ft.Text("Listado de Categorías", size=18, weight="bold"),
            ft.Container(
                content=categorias_list,
                height=400,
                border=ft.border.all(1, Colors.GREY_300),
                padding=10,
                border_radius=10,
                bgcolor=Colors.GREY_50
            )
        ], spacing=15)
    )

    # Carga inicial
    cargar_categorias()

ft.app(target=main)