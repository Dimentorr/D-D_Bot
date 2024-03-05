from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents',
          'https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = '../file/json/bufferfordndbot-cfe5b9357a3f.json'


def create_remote_folder(folder_name, parent_id=None):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    body = {
        'name': folder_name,
        'mimeType': "application/vnd.google-apps.folder"
    }
    if parent_id:
        body['parents'] = [parent_id]
    root_folder = service.files().create(body=body).execute()
    return root_folder['id']


def get_info():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    return service.files().list(pageSize=10,
                                fields="nextPageToken, files(id, name, mimeType, webViewLink)").execute()


def share_file(service_drive, file_id, email, role):
    # roles: editor
    #        writer
    new_permissions = {
        'type': 'group',
        'role': role,
        'emailAddress': email
    }

    permission_response = service_drive.permissions().create(
        fileId=file_id,
        body=new_permissions,
        sendNotificationEmail=False
    ).execute()


def create_item(item_name, mail, role):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service_drive = build('drive', 'v3', credentials=credentials)
    body = {
        'name': item_name,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': '1GyWxpOJDA-i8M64ihoV90LVPn2kNc4YC'
    }
    file = service_drive.files().create(body=body,
                                        fields="id, name, mimeType, webViewLink").execute()
    share_file(service_drive, file['id'], email=mail, role=role)
    return file
