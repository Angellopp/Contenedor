import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
import psycopg2  # Para conectarse a PostgreSQL
import subprocess  # Para ejecutar comandos del sistema


# Configuración de la base de datos
DB_HOST = "192.168.20.65"  # IP del servidor donde está la base de datos
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


def predecir_imagen(ruta_imagen):
    """Realiza la predicción de la imagen y devuelve la clase predicha."""
    try:
        # Cargar y preprocesar la imagen
        image = Image.open(ruta_imagen)
        image = image.resize((224, 224))  # Redimensionar a 224x224
        image_array = np.asarray(image) / 255.0  # Normalizar
        image_array = np.expand_dims(image_array, axis=0)  # Añadir dimensión para el batch

        # Realizar la predicción
        predictions = modelo_cargado.predict(image_array)
        predicted_class_index = np.argmax(predictions, axis=1)[0]

        #predicted_class_index = 1
        predicted_class_name = inverse_class_indices[predicted_class_index]

        return predicted_class_name
    except Exception as e:
        print(f"Error al predecir: {str(e)}")
        return None


def actualizar_base_datos(codigo_usuario, clase_predicha):
    """Conecta a la base de datos y actualiza el campo correspondiente."""
    try:
        # Conexión a la base de datos
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        # Crear el comando SQL para actualizar
        query = f"""
        UPDATE usuarios
        SET cantidad_{clase_predicha.lower()} = cantidad_{clase_predicha.lower()} + 1
        WHERE codigo = %s;
        """
        cursor.execute(query, (codigo_usuario,))

        # Confirmar los cambios
        connection.commit()

        if cursor.rowcount > 0:
            print(f"Actualización exitosa para el usuario {codigo_usuario}: +1 en {clase_predicha}.")
        else:
            print(f"No se encontró un usuario con el código {codigo_usuario}.")

    except Exception as e:
        print(f"Error al actualizar la base de datos: {str(e)}")
    finally:
        if connection:
            cursor.close()
            connection.close()

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

        # Capturar la imagen
        capturar_imagen(ruta_imagen)

        # Predecir la clase de la imagen
        clase_predicha = predecir_imagen(ruta_imagen)

        if clase_predicha:
            print(f"Clase predicha: {clase_predicha}")
            # Actualizar la base de datos
            actualizar_base_datos(codigo_usuario, clase_predicha)