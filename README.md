# 🚀 AWS Lambda + GraphQL + MySQL (Serverless API)

Este proyecto implementa una API **serverless** usando **AWS Lambda** para manejar **consultas GraphQL** con una base de datos **MySQL en Amazon RDS**.  
La API permite realizar consultas de tipo `GET`, incluyendo búsquedas por ID y conteo de registros.

---

## 📌 Tecnologías Utilizadas
- **AWS Lambda** → Ejecuta el código sin necesidad de servidores.
- **Amazon RDS (MySQL)** → Base de datos relacional en la nube.
- **API Gateway** → Expone el endpoint `/graphql` para recibir consultas.
- **Python 3.9** → Lenguaje de programación.
- **pymysql** → Librería para conectar Python con MySQL.
- **strawberry-graphql** → Framework para manejar GraphQL en Python.
- **AWS Secrets Manager** _(Opcional)_ → Para manejar credenciales de MySQL de forma segura.

---

## 📌 Instalación y Configuración

### 🔹 1. Configurar Variables de Entorno en AWS Lambda
En AWS Lambda, ve a **"Configuration" → "Environment Variables"** y agrega:

| Variable  | Valor |
|-----------|-------------------------------------------|
| `DB_HOST`  | `iot-mysql-db.xxxxxxxx.us-east-1.rds.amazonaws.com` |
| `DB_USER`  | `admin` |
| `DB_PASSWORD`  | `tu_contraseña` |
| `DB_NAME`  | `Plantas` |
| `DB_PORT`  | `3306` |

### 🔹 2. Instalar Dependencias
Ejecuta estos comandos en tu máquina local:
```bash
mkdir lambda_packages
cd lambda_packages
pip install pymysql strawberry-graphql -t .
zip -r lambda_function.zip .
```
Sube **`lambda_function.zip`** a **AWS Lambda**.

---

## 📌 Código Principal (`lambda_function.py`)
A continuación se presenta el código optimizado con manejo de errores y conversión de fechas.

```python
import json
import pymysql
import os
from datetime import date

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

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

def json_serial(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def obtener_registros(query):
    conn = get_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos."}

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        conn.close()

        for row in data:
            for key, value in row.items():
                if isinstance(value, date):
                    row[key] = value.isoformat()

        return data
    except pymysql.MySQLError as e:
        return {"error": f"Error en la consulta SQL: {str(e)}"}

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        query = body.get("query", "")

        if "obtenerUsuarios" in query:
            response = obtener_registros("SELECT * FROM USUARIOS;")
        else:
            response = {"error": "Consulta no soportada"}

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response, default=json_serial)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error interno del servidor", "details": str(e)})
        }
```

---

## 📌 Pruebas

### 🔹 Prueba en AWS Lambda
1. Ve a **AWS Lambda** → **Tu función (`GraphQLLambda`)**.
2. Haz clic en **"Test"** y usa este evento:
```json
{
  "body": "{ "query": "{ obtenerUsuarios { id_usuario nombre correo } }" }"
}
```
3. **Haz clic en "Invoke"**.

✅ **Si todo está bien, recibirás datos de MySQL sin errores.**

### 🔹 Prueba con `curl`
```bash
curl -X POST "https://xyz.execute-api.us-east-1.amazonaws.com/graphql"      -H "Content-Type: application/json"      -d '{"query": "{ obtenerUsuarios { id_usuario nombre correo } }"}'
```
✅ **Si funciona, recibirás los datos de usuarios en formato JSON.**

---

## 📌 Puntos a Mejorar
- **Agregar Paginación** en consultas grandes para mejorar rendimiento.

---

## 📌 Siguientes Pasos
📌 **Optimizar la API con Paginación en GraphQL**  
📌 **Agregar integración con un frontend en Flutter**  
