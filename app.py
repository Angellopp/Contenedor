import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import psycopg2
import subprocess

# Configuración de la base de datos
DB_HOST = "192.168.20.31"
DB_NAME = "contenedor_db"
DB_USER = "user_admin"
DB_PASSWORD = "123456"

# Configuración del modelo
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Cargar el modelo
modelo_cargado = load_model('mi_modelo.h5')

# Diccionario de clases
class_indices = {
    'Carton': 0,
    'Vidrio': 1,
    'Metal': 2,
    'Papel': 3,
    'Plastico': 4,
    'Basura': 5
}

# Invertir el diccionario
inverse_class_indices = {v: k for k, v in class_indices.items()}

def conectar_base_datos():
    """Establece conexión con la base de datos y retorna el objeto conexión."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        print(f"Error al conectar con la base de datos: {str(e)}")
        return None

def existe_codigo_usuario(codigo_usuario):
    """Verifica si un código de usuario es válido y existe en la base de datos."""
    
    # Validar formato del código antes de consultar la base de datos
    if not codigo_usuario[:-1].isdigit() or not codigo_usuario[-1].isalpha() or len(codigo_usuario) != 9:
        print(f"Formato de código inválido: {codigo_usuario}")
        return False
    
    # Intentar conectar con la base de datos
    connection = conectar_base_datos()
    if not connection:
        print("No se pudo establecer conexión con la base de datos.")
        return False
    
    try:
        cursor = connection.cursor()
        query = "SELECT 1 FROM usuarios WHERE codigo = %s;"
        cursor.execute(query, (codigo_usuario,))
        existe = cursor.fetchone() is not None
        if not existe:
            print(f"El código {codigo_usuario} no existe en la base de datos.")
        return existe
    except Exception as e:
        print(f"Error al verificar el código del usuario: {str(e)}")
        return False
    finally:
        connection.close()


def actualizar_base_datos(codigo_usuario, clase_predicha):
    """Actualiza la base de datos si el usuario existe."""
    if not existe_codigo_usuario(codigo_usuario):
        print(f"El código {codigo_usuario} no existe en la base de datos.")
        return
    
    connection = conectar_base_datos()
    if not connection:
        return
    try:
        cursor = connection.cursor()
        query = f"""
        UPDATE usuarios
        SET cantidad_{clase_predicha.lower()} = cantidad_{clase_predicha.lower()} + 1
        WHERE codigo = %s;
        """
        cursor.execute(query, (codigo_usuario,))
        connection.commit()
        print(f"Actualización exitosa para el usuario {codigo_usuario}: +1 en {clase_predicha}.")
    except Exception as e:
        print(f"Error al actualizar la base de datos: {str(e)}")
    finally:
        cursor.close()
        connection.close()

def predecir_imagen(ruta_imagen):
    """Realiza la predicción de la imagen y devuelve la clase predicha."""
    try:
        image = Image.open(ruta_imagen)
        image = image.resize((224, 224))
        image_array = np.asarray(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        predictions = modelo_cargado.predict(image_array)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        return inverse_class_indices[predicted_class_index]
    except Exception as e:
        print(f"Error al predecir: {str(e)}")
        return None

def capturar_imagen(ruta_imagen):
    """Captura una imagen usando libcamera y la guarda en la ruta especificada."""
    try:
        subprocess.run(["libcamera-still", "-o", ruta_imagen], check=True)
        print(f"Imagen capturada y guardada en {ruta_imagen}")
    except subprocess.CalledProcessError as e:
        print(f"Error al capturar la imagen: {e}")

if __name__ == "__main__":
    while True:
        ruta_imagen = "Imagenes/captura.jpg"
        codigo_usuario = input("Ingresa el código del usuario: ")
        if existe_codigo_usuario(codigo_usuario):
            capturar_imagen(ruta_imagen)
            clase_predicha = predecir_imagen(ruta_imagen)
            print(f"Clase predicha: {clase_predicha}")
            actualizar_base_datos(codigo_usuario, clase_predicha)