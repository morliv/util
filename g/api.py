from pathlib import Path
from typing import Callable, Optional

import google.auth
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

from util import obj

# If modifying these scopes, delete token.json
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
DIR = Path(__file__).resolve().parent
CREDENTIALS = DIR / "credentials.json"
TOKEN = DIR / "token.json"

def service(service_name, version):
    return build(service_name, "v" + str(version), credentials=creds())

def creds():
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, "w") as token:
            token.write(creds.to_json())
    return creds

def establish(obj: type, f: Callable, anew=False) -> type: 
    return obj.set(obj, request(f), anew)

def request(f: Callable) -> dict:
    try:
        return f.execute()
    except HttpError as e:
        handle_response(e)

def handle_response(e: HttpError):
    if e.resp.status == 404:
        return None
    raise

