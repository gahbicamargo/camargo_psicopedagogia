import mimetypes
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class GoogleDriveService:
    def __init__(self) -> None:
        self.habilitado = os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true"
        self.publico = os.getenv("GOOGLE_DRIVE_PUBLIC_LINKS", "true").lower() == "true"
        self.parent_folder_id = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", "").strip()

        cred_path_raw = os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE", "").strip()
        self.credentials_path = Path(cred_path_raw) if cred_path_raw else None

        self.service = None
        if self.habilitado and self.credentials_path and self.credentials_path.exists():
            creds = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=["https://www.googleapis.com/auth/drive"],
            )
            self.service = build("drive", "v3", credentials=creds)

    def upload_arquivos(self, nome_pasta_atendimento: str, arquivos: list[Path]) -> list[dict[str, str]]:
        if not self.service:
            return []

        folder_id = self._obter_ou_criar_pasta(nome_pasta_atendimento, self.parent_folder_id)
        resultado: list[dict[str, str]] = []

        for arquivo in arquivos:
            file_id, link = self._upload_arquivo(arquivo, folder_id)
            resultado.append(
                {
                    "nome": arquivo.name,
                    "id": file_id,
                    "url": link,
                }
            )

        return resultado

    def _obter_ou_criar_pasta(self, nome: str, parent_id: str | None = None) -> str:
        nome_escapado = nome.replace("'", "\\'")
        query = f"name = '{nome_escapado}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        resp = self.service.files().list(q=query, fields="files(id, name)", pageSize=1).execute()
        files = resp.get("files", [])
        if files:
            return files[0]["id"]

        metadata = {
            "name": nome,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        created = self.service.files().create(body=metadata, fields="id").execute()
        return created["id"]

    def _upload_arquivo(self, caminho: Path, pasta_id: str) -> tuple[str, str]:
        mime_type = mimetypes.guess_type(str(caminho))[0] or "application/octet-stream"
        file_metadata = {"name": caminho.name, "parents": [pasta_id]}
        media = MediaFileUpload(str(caminho), mimetype=mime_type, resumable=False)

        created = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )

        file_id = created["id"]

        if self.publico:
            self.service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()
            created = self.service.files().get(fileId=file_id, fields="id, webViewLink").execute()

        link = created.get("webViewLink", "")
        return file_id, link
