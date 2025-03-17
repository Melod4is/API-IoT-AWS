import json
import pymysql
import os
from datetime import date

# Obtener credenciales desde las variables de entorno de AWS Lambda
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Función para conectar a MySQL con manejo de errores
def get_connection():
    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        print(f"Error de conexión a MySQL: {str(e)}")
        return None

# Convertir fecha a string antes de enviarla en JSON
def json_serial(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convierte `YYYY-MM-DD`
    raise TypeError(f"Type {type(obj)} not serializable")

# Consultas generales con manejo de errores
def obtener_registros(query):
    conn = get_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos."}

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        conn.close()

        # Convertir fechas antes de devolver la respuesta
        for row in data:
            for key, value in row.items():
                if isinstance(value, date):
                    row[key] = value.isoformat()

        return data
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {str(e)}")
        return {"error": "Error al ejecutar la consulta SQL."}

# Obtener por ID con validación
def obtener_registro_por_id(tabla, id_column, id_value):
    if not isinstance(id_value, int) or id_value <= 0:
        return {"error": "ID inválido. Debe ser un número entero positivo."}

    conn = get_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos."}

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {tabla} WHERE {id_column} = %s;", (id_value,))
            data = cursor.fetchone()
        conn.close()

        # Convertir fecha si existe en el resultado
        if data:
            for key, value in data.items():
                if isinstance(value, date):
                    data[key] = value.isoformat()

        return data if data else {"error": f"No se encontró el registro con {id_column} = {id_value}"}
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {str(e)}")
        return {"error": "Error al ejecutar la consulta SQL."}

# Contar registros con manejo de errores
def contar_registros(tabla):
    conn = get_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos."}

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) as total FROM {tabla};")
            data = cursor.fetchone()
        conn.close()
        return data["total"] if data else 0
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {str(e)}")
        return {"error": "Error al ejecutar la consulta SQL."}

# Manejador de Lambda con captura de errores generales
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        query = body.get("query", "")

        # Consultas generales
        if "obtenerCiudades" in query:
            response = obtener_registros("SELECT * FROM CIUDADES;")
        elif "obtenerUsuarios" in query:
            response = obtener_registros("SELECT * FROM USUARIOS;")
        elif "obtenerEspecies" in query:
            response = obtener_registros("SELECT * FROM ESPECIES;")
        elif "obtenerPlantas" in query:
            response = obtener_registros("SELECT * FROM PLANTAS;")
        elif "obtenerDispositivos" in query:
            response = obtener_registros("SELECT * FROM DISPOSITIVOS;")

        # Consultas por ID
        elif "obtenerCiudadPorId" in query:
            id_value = int(query.split("cod_ciudad:")[1].split(")")[0].strip())
            response = obtener_registro_por_id("CIUDADES", "cod_ciudad", id_value)
        elif "obtenerUsuarioPorId" in query:
            id_value = int(query.split("id_usuario:")[1].split(")")[0].strip())
            response = obtener_registro_por_id("USUARIOS", "id_usuario", id_value)
        elif "obtenerEspeciePorId" in query:
            id_value = int(query.split("cod_especie:")[1].split(")")[0].strip())
            response = obtener_registro_por_id("ESPECIES", "cod_especie", id_value)
        elif "obtenerPlantaPorId" in query:
            id_value = int(query.split("id_planta:")[1].split(")")[0].strip())
            response = obtener_registro_por_id("PLANTAS", "id_planta", id_value)
        elif "obtenerDispositivoPorId" in query:
            id_value = int(query.split("id_dispositivo:")[1].split(")")[0].strip())
            response = obtener_registro_por_id("DISPOSITIVOS", "id_dispositivo", id_value)

        # Contar registros
        elif "totalCiudades" in query:
            response = contar_registros("CIUDADES")
        elif "totalUsuarios" in query:
            response = contar_registros("USUARIOS")
        elif "totalEspecies" in query:
            response = contar_registros("ESPECIES")
        elif "totalPlantas" in query:
            response = contar_registros("PLANTAS")
        elif "totalDispositivos" in query:
            response = contar_registros("DISPOSITIVOS")

        else:
            response = {"error": "Consulta no soportada"}

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response, default=json_serial)  # Solución para fechas
        }

    except Exception as e:
        print(f"Error general: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error interno del servidor", "details": str(e)})
        }
