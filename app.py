# pip install google-api-python-client
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import subprocess

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = '<google drive folder id>'

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds);

# Function to download file from Google Drive
def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    fh = open('/tmp/' + file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.close()

# Function to upload file to Google Drive
def upload_file(file_name, modified_file_name):
    file_metadata = {'name': modified_file_name}
    media = MediaFileUpload('/tmp/' + modified_file_name, mimetype='video/mp4')
    drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Function to process video file with ffmpeg
def process_video(file_name):
    input_file = '/tmp/' + file_name
    output_file = '/tmp/shortened_' + file_name
    subprocess.run(['ffmpeg', '-i', input_file, '-an', '-filter:v', 'setpts=0.05*PTS', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', output_file])
    print('Video processed successfully.')

# List files from Google Drive
results = drive_service.files().list(q="mimeType='video/mp4'").execute()
items = results.get('files', [])

for item in items:
    file_id = item['id']
    file_name = item['name']
    if 'fast' not in file_name.lower():
        print('Processing file: ' + file_name);
        download_file(file_id, file_name)
        process_video(file_name)
        modified_file_name = 'shortened_' + file_name
        #upload_file(modified_file_name)
        continue
    print('File already processed.')

print('Files processed successfully.')