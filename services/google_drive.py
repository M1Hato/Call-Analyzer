import io
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from config import settings

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]


def get_user_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_drive_service():
    return build('drive', 'v3', credentials=get_user_credentials())


def list_audio_files_in_source():
    service = get_drive_service()
    query = f"'{settings.CLIENT_AUDIO}' in parents and (mimeType contains 'audio/' or name contains '.mp3' or name contains '.wav') and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])


def download_file(file_id: str, local_path: str):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    with open(local_path, 'wb') as f:
        f.write(fh.getvalue())


def save_transcription_to_drive(filename: str, text: str):
    service = get_drive_service()

    fh = io.BytesIO(text.encode('utf-8'))

    file_metadata = {
        'name': f"{os.path.splitext(filename)[0]}_transcription.txt",
        'parents': [settings.CLIENT_PROCESSED]
    }
    media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=True)

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"Транскрибацію успішно збережено на Google Drive. ID: {uploaded_file.get('id')}")
    return uploaded_file.get('id')