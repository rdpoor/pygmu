from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

DOH_DRIVE = '1k-GyVIKF2f_nFN6SgUS5J_epCtDoVOC2'

def authorize():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("pygmulib_creds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("pygmulib_creds.txt")
    return GoogleDrive(gauth)

def find_nested_folder_id(drive, folder_path):
    folder_names = folder_path.split('/')
    parent_id = DOH_DRIVE  # Start search from the root

    for folder_name in folder_names:
        query = f"'{parent_id}' in parents and title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        # print(f"Executing query: {query}")  # Debug: Print the query
        folder_list = drive.ListFile({'q': query}).GetList()
        # print(f"folder_list = {folder_list}")
        if folder_list:
            parent_id = folder_list[0]['id']
            print(f"Found '{folder_name}' with ID: {parent_id}")  # Debug: Confirm folder is found
        else:
            print(f"Folder '{folder_name}' not found.")
            return None
    return parent_id

def copy_file_from_folder(drive, folder_id, file_name, destination_folder):
    if folder_id is None:
        return
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and title='{file_name}' and trashed=false"}).GetList()
    for file in file_list:
        print(f"Downloading {file_name} from folder ID {folder_id}...")
        file.GetContentFile(f"{destination_folder}/{file_name}")
        print(f"File downloaded to {destination_folder}/{file_name}")
        break
    else:
        print(f"File {file_name} not found in the specified folder.")

drive = authorize()
print(f'drive = {drive}')
folder_id = find_nested_folder_id(drive, "media/snds")
copy_file_from_folder(drive, folder_id, 'Tamper_ManFrame2.wav', '.')
