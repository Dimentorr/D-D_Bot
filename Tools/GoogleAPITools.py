import base64
import os
from email.mime.text import MIMEText

from Tools.JsonTools import CatalogJson

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleTools:
    def __init__(self):
        self.env = CatalogJson(name='file/json/environment.json')
        self.SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']
        self.CLIENT_SECRET_FILE = self.env.read_json_data('google_api_client_secret')
        self.sender = self.env.read_json_data('google_mail_sender')
        self.API_KEY = self.env.read_json_data('google_api_service_key')

        self.SCOPES = ['https://www.googleapis.com/auth/drive',
                       'https://www.googleapis.com/auth/documents',
                       'https://www.googleapis.com/auth/drive.file']
        self.SERVICE_ACCOUNT_FILE = 'file/json/credential.json'
        self.creds_gmail = None
        self.creds_drive = None

    def create_remote_folder(self, folder_name, parent_id=None):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        body = {
            'name': folder_name,
            'mimeType': "application/vnd.google-apps.folder"
        }
        if parent_id:
            body['parents'] = [parent_id]
        root_folder = service.files().create(body=body).execute()
        return root_folder['id']

    def get_info(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        return service.files().list(pageSize=10,
                                    fields="nextPageToken, files(id, name, mimeType, webViewLink)").execute()

    def share_file(self, service_drive, file_id, email, role):
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

    def create_item(self, item_name, mail, role):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        service_drive = build('drive', 'v3', credentials=credentials)
        body = {
            'name': item_name,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': '1GyWxpOJDA-i8M64ihoV90LVPn2kNc4YC'
        }
        file = service_drive.files().create(body=body,
                                            fields="id, name, mimeType, webViewLink").execute()
        self.share_file(service_drive, file['id'], email=mail, role=role)
        return file

    def create_message(self, autor, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = autor
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def send_message(self, service, user_id, message):
        try:
            message = service.users().messages().send(userId=user_id, body=message).execute()
            return message
        except Exception as error:
            print('An error occurred: %s' % error)

    def gmail_send(self, to, text_message):
        if os.path.exists('file/json/token.json'):
            self.creds_gmail = Credentials.from_authorized_user_file('file/json/token.json')
        if not self.creds_gmail:
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, self.SCOPES_GMAIL)
            self.creds_gmail = flow.run_local_server()
            # создасть токен подключения, сохранив все предоставленные выбранному аккаунту разрешения,
            # (если его(файла token.json) не было до этого)
            with open("file/json/token.json", "w") as token:
                token.write(self.creds_gmail.to_json())
        with build('gmail', 'v1', credentials=self.creds_gmail) as service_gmail:
            message = self.create_message(self.sender, to, 'Verify', text_message)
            self.send_message(service_gmail, 'me', message)
