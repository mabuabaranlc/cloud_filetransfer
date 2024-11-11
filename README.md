
# Cloud File Transfer - Azure Function

Este proyecto implementa una Azure Function para transferir archivos entre diferentes servicios de almacenamiento en la nube (Azure Storage, Google Cloud Storage, y Amazon S3) sin descargar los archivos a un servidor local. La función utiliza flujos de datos (`stream`) para realizar las transferencias de forma eficiente.

## Descripción

La función `file_transfer` recibe una solicitud HTTP con los detalles de la transferencia, como el proveedor de almacenamiento de origen, la ruta del archivo y el proveedor de destino. A partir de estos datos, la función:
1. Recupera el archivo del almacenamiento de origen como un flujo.
2. Lo transfiere al almacenamiento de destino en el formato especificado.

### Proveedores soportados:
- **Azure Storage (ASA)**
- **Google Cloud Storage (GCS)**
- **Amazon S3 (S3)**

## Requisitos

- **Azure Functions Core Tools** para desarrollo local
- **Python 3.8+**
- **Paquetes de Python**: `azure-functions`, `azure-storage-blob`, `google-cloud-storage`, `boto3`

## Configuración del Entorno

1. **Clonar el repositorio**:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>
   ```

2. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno** en `local.settings.json`:

   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "ASA_CONNECTION_STRING": "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=...;BlobEndpoint=http://<URL_AZURE_STORAGE>:10000/devstoreaccount1;",
       "S3_ENDPOINT": "http://<URL_S3>",
       "S3_ACCESS_KEY": "<S3_ACCESS_KEY>",
       "S3_SECRET_KEY": "<S3_SECRET_KEY>",
       "S3_REGION": "us-east-1",
       "GOOGLE_APPLICATION_CREDENTIALS": "./gcp_credentials.json"
     }
   }
   ```

   - Reemplaza `<URL_AZURE_STORAGE>`, `<S3_ACCESS_KEY>`, `<S3_SECRET_KEY>`, `<ID_PROYECTO>`, y otros valores con los datos específicos de tu entorno.
   - `GOOGLE_APPLICATION_CREDENTIALS` es un archivo JSON con las credenciales de servicio de GCS.

## Ejecución

Inicia la Azure Function localmente con:

```bash
func start
```

## Ejemplos de Uso

Realiza una solicitud HTTP `POST` a la función `file_transfer` con los siguientes parámetros:

### Ejemplo de Transferencia de S3 a Azure Storage

```json
POST /api/file_transfer
{
  "source": "s3",
  "source_path": "bucket_name/path/to/source_file.txt",
  "sink": "asa",
  "sink_path": "container_name/path/to/destination_file.txt"
}
```

### Ejemplo de Transferencia de Azure Storage a Google Cloud Storage

```json
POST /api/file_transfer
{
  "source": "asa",
  "source_path": "container_name/path/to/source_file.txt",
  "sink": "gcs",
  "sink_path": "bucket_name/path/to/destination_file.txt"
}
```

## Estructura del Código

- `file_transfer`: Función principal que maneja las solicitudes HTTP y valida los parámetros de entrada.
- `stream_from_source`: Función para obtener un flujo de datos del almacenamiento de origen sin descargarlo localmente.
- `write_to_sink`: Función para escribir el flujo de datos en el almacenamiento de destino.

## Mejoras Sugeridas

1. **Manejo de Errores Detallado**: Actualmente, el código maneja errores de forma general. Podrías agregar un manejo de errores específico para cada proveedor de almacenamiento para proporcionar mensajes más detallados.

2. **Configuración de Credenciales Seguras**: Aunque el archivo `gcp_credentials.json` está en la ruta indicada, sería ideal proteger este archivo con permisos adecuados en entornos de producción.

3. **Optimización de Flujos**: Considerar la implementación de chunks para la transferencia de archivos de gran tamaño para reducir el uso de memoria en archivos extremadamente grandes.

4. **Compatibilidad con Más Servicios**: Este framework podría ampliarse para soportar más proveedores de almacenamiento en la nube.

## Licencia

Este proyecto está bajo la licencia MIT.
