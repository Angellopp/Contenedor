# Configuracion y conexión de RaspberryPi

<aside>
💡

IP fija RaspberryPi    →   192.268.20.15

IP fija Servidor           →   192.168.20.65

Contraseña               →    123456

</aside>

### Conexión mediante ssh a la RaspberryPi

```bash
ssh contenedor1@192.168.20.15
```

### Creacion de un entorno virtual

```bash
python -m venv env_contenedor
source env_contenedor/bin/activate 
```

```bash
deactivate # Para salir del entorno virtual
```

### Archivo donde estan los archivos necesarios para el modelo RNN:

https://drive.google.com/drive/folders/1Dup2oUZAv2fMKwZVdu-baa8zx85IWhOP?hl=es

### Mover los archivos a la RaspberryPi mediante ssh:

```bash
scp ruta/archivo/para/mover pi@192.168.20.15:/home/contenedor/ruta/destino
scp /Desktop/image.jpg pi@192.168.20.65:/Desktop
```

### Base de datos

```sql
# Cambiar a usuario postgres
sudo -i -u postgres
# Acceder a la consola de PostgreSQL
psql
# Crear la base de datos
CREATE DATABASE contenedor_db;
# Crear un usuario con contraseña
CREATE USER admin WITH PASSWORD '123456';
# Asignar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE contenedor_db TO admin;
GRANT CREATE ON SCHEMA public TO admin;
```

```sql
psql -U admin -d contenedor_db -h localhost

```

```sql
CREATE TABLE usuarios (
    codigo VARCHAR(10) PRIMARY KEY, -- Código único del usuario (por ejemplo, '20210035J')
    cantidad_carton NUMERIC DEFAULT 0, -- Cantidad reciclada de cartón
    cantidad_vidrio NUMERIC DEFAULT 0, -- Cantidad reciclada de vidrio
    cantidad_metal NUMERIC DEFAULT 0, -- Cantidad reciclada de metal
    cantidad_papel NUMERIC DEFAULT 0, -- Cantidad reciclada de papel
    cantidad_plastico NUMERIC DEFAULT 0, -- Cantidad reciclada de plástico
    cantidad_basura NUMERIC DEFAULT 0 -- Cantidad de basura no reciclable
);
```

```sql
INSERT INTO usuarios (codigo, cantidad_carton, cantidad_vidrio, cantidad_metal, cantidad_papel, cantidad_plastico, cantidad_basura)
VALUES
('20210035J', 5, 10, 3, 7, 15, 2),
('20220012K', 8, 6, 4, 5, 10, 1);

```

## **Rol de lectura y escritura**

El proceso de agregar un rol de lectura/escritura es muy similar al proceso de rol de solo lectura que se trató anteriormente. El primer paso es crear un rol:

`CREATE ROLE readwrite;`

Conceda permiso a este rol para conectarse a la base de datos de destino:

`GRANT CONNECT ON DATABASE contenedor_db TO readwrite;`

Conceda privilegio de uso de esquemas:

`GRANT USAGE ON SCHEMA public TO readwrite;`

Si desea permitir que este rol cree nuevos objetos como tablas de este esquema, utilice el siguiente SQL en lugar del anterior:

`GRANT USAGE, CREATE ON SCHEMA public TO readwrite;`

El siguiente paso es conceder acceso a las tablas. Como se mencionó en la sección anterior, la concesión puede realizarse en tablas individuales o en todas las tablas del esquema. Para tablas individuales, utilice el siguiente SQL:

`GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE mytable1, mytable2 TO readwrite;`

Para todas las tablas y vistas del esquema, utilice el siguiente SQL:

`GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite;`

Para conceder automáticamente permisos sobre tablas y vistas añadidas en el futuro:

`ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite;`

Para los roles de lectura y escritura, normalmente existe el requisito de utilizar secuencias también. Puede dar acceso selectivo de la siguiente manera:

`GRANT USAGE ON SEQUENCE myseq1, myseq2 TO readwrite;`

También puede conceder permiso a todas las secuencias mediante la siguiente instrucción SQL:

`GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO readwrite;`

Para conceder permisos automáticamente a las secuencias añadidas en el futuro:

`ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO readwrite;`

```
CREATE USER myuser1 WITH PASSWORD '123456';
GRANT readwrite TO myuser1;
```

Si quieres conectarte mediante ssh al servidor desde la raspeberry, tienes que :

```bash
sudo apt update
sudo apt install openssh-server -y
```

```bash
systemctl status ssh
sudo systemctl enable ssh
```

Esto principalmente lo hice para verificar las imagenes tomadas por la raspberry:
En la raspeberry:

```bash
scp ~/Desktop/image.jpg angello@192.168.20.65:~/Desktop/
scp /home/contenedor1/Desktop/env_contenedor/Imagenes/captura.jpg  angello@192.168.20.65:~/Desktop/
```

### Usando un **Servicio de systemd**

 script `cam.py` se ejecute automáticamente cuando la Raspberry Pi se inicie

Este es el método más limpio y eficiente. Un servicio systemd permite controlar el script, reiniciarlo si falla, entre otras ventajas.

### Pasos:

1. **Crea un archivo de servicio para tu script:**
    
    En la terminal, crea un nuevo archivo de servicio para systemd:
    
    ```bash
    sudo nano /etc/systemd/system/cam.service
    ```
    
2. **Agrega la siguiente configuración:**
    
    En este archivo, define cómo debe ejecutarse tu script `cam.py`:
    
    ```bash
    [Unit]
    Description=Servicio de captura de cámara con entorno virtual
    After=network.target
    
    [Service]
    Type=simple
    WorkingDirectory=/home/contenedor1/Desktop
    ExecStart=/bin/bash -c 'source /home/contenedor1/Desktop/env_contenedor/bin/activate && /usr/bin/python3 /home/contenedor1/Desktop/env_contenedor/cam.py'
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=contenedor1
    Group=contenedor1
    
    [Install]
    WantedBy=multi-user.target
    ```
    
3. **Recarga los servicios de systemd:**
    
    Después de crear el archivo de servicio, recarga systemd para que detecte tu nuevo servicio.
    
    ```bash
    sudo systemctl daemon-reload
    ```
    
4. **Habilita el servicio para que se inicie automáticamente:**
    
    Activa el servicio para que se ejecute al inicio:
    
    ```bash
    sudo systemctl enable cam.service
    ```
    
5. **Inicia el servicio manualmente para probarlo:**
    
    Puedes iniciar el servicio de inmediato con el siguiente comando:
    
    ```bash
    sudo systemctl start cam.service
    ```
    
6. **Verifica que el servicio esté funcionando:**
    
    Puedes comprobar el estado del servicio con:
    
    ```bash
    sudo systemctl status cam.service
    ```
    
    Si todo está bien, debería aparecer como **active (running)**.
    

1. Primero que se verifique la conexion como servicio

1. se lee el codigo del carnet
2. se busca en la tabla de datos
3. se verifica una vez que el codigo este en labla
4. agrgar columna de saldo

```python
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
```