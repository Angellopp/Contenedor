# Usa una imagen oficial de Python
FROM python:3.11.2

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación al contenedor
COPY . .

# Especifica el comando por defecto para ejecutar la app
CMD ["python", "app.py"]
