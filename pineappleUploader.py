from __future__ import print_function

import pickle
import os.path
import sys
import getopt
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
auth_flow = "local_server"


def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            if auth_flow == "console":
                creds = flow.run_console()
            else:
                creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def main(filename: str, driveId: str):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    service = build('drive', 'v3', credentials=authenticate())

    # Call the Drive v3 API
    if not os.path.exists(filename):
        print("file not found")
    else:
        file_metadata = {'name': os.path.split(filename)[1], "driveId": driveId, "parents": [driveId]}
        media = MediaFileUpload(filename, chunksize=-1, resumable=True)
        response = None
        request = service.files().create(body=file_metadata, media_body=media, supportsAllDrives=True)
        while response is None:
            status, response = request.next_chunk()
        service.permissions().create(fileId=response['id'], body={"type": "anyone", "role": 'reader',
                                                                  "permissionDetails": {"role": 'reader'}},
                                     supportsAllDrives=True).execute()
        return response['id']


if __name__ == '__main__':
    options, args = getopt.getopt(sys.argv[1:], "", ["token", "console"])
    if ('--console', '') in options or len(args) != 2:
        auth_flow = "console"
        print("authenticating on console")
    if ('--token', '') in options or len(args) != 2:
        generated_creds = authenticate()
        if generated_creds:
            print("succesfully authenticated")
    else:
        print(main(args[0], args[1]))
