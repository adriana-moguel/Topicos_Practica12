import mysql.connector
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Santiago16_",
        database="farmaciasguadalajara"
    )
    print("✅ Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")