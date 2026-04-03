from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError, AzureError
from config import settings

_client = BlobServiceClient.from_connection_string(settings.azure_storage_conn_str)
_container = _client.get_container_client(settings.azure_storage_container)


async def upload_file(filename: str, data: bytes, content_type: str = "application/pdf") -> dict:
    """Upload un fichier dans le Blob Storage."""
    try:
        blob_client = _container.get_blob_client(filename)
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        return {
            "success": True,
            "filename": filename,
            "url": blob_client.url,
            "size_bytes": len(data)
        }
    except AzureError as e:
        return {"success": False, "error": str(e)}


async def list_files() -> list:
    """Liste tous les fichiers dans le container."""
    try:
        return [
            {"name": b.name, "size": b.size, "last_modified": str(b.last_modified)}
            for b in _container.list_blobs()
        ]
    except AzureError as e:
        return [{"error": str(e)}]


async def delete_file(filename: str) -> dict:
    """Supprime un fichier du Blob Storage."""
    try:
        _container.get_blob_client(filename).delete_blob()
        return {"success": True, "deleted": filename}
    except AzureError as e:
        return {"success": False, "error": str(e)}
