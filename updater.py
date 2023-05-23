from __future__ import print_function
# Import modules
from tkinter import *  # graphical user interface
import os  # pathing and folder operations


from googleapiclient import *
from googleapiclient.http import *
from googleapiclient.discovery import *
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


import io

# from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account


import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo


# region functions section


def default_path():  # generates a path to the default minecraft installation
    print("default_path function")
    path = os.getenv('APPDATA')
    path = path+"\.minecraft\mods"
    print("exiting")
    return path


def path_check(path):  # function to check if the given path exist, if the path cannot be accessed the program goes into errorstate red
    print("path_check function")
    if (path == None):
        root['bg'] = 'dark red'
        errorstate = True
    print("exiting")
    return errorstate


def list_to_txt(list, file_name, path):  # dumps the given list into a txt file
    print("list_to_txt function")
    file_name = file_name+".txt"
    if os.path.exists(path) == TRUE:
        txt = open(file_name, "w")
    else:
        txt = open(file_name, "x")
    for x in list:
       # temp = list+"\n"
        txt.write(list)
    txt.close()
    print("exiting")

# compares the path list with the current manifest and generates a list of files to be downloaded


def delete(local_list, remote_list):
    print("delete function")
    FoundItems = []
    match = False
    count = 0
    for x in range(len(local_list)):
        match = False
        print("looking for file "+str(local_list[x])+" in the cloud manifest")
        for y in range(len(remote_list)):
            if (str(remote_list[y]).find(local_list[x]) != -1):
                print("file found")
                match = True
        if (match == False):
            count = count+1
            print("file not found")
            print(F"items added:", {count})
            FoundItems.append(local_list[x])
    if (range(len(FoundItems)) != 0):
        for items in range(len(FoundItems)):
            os.remove(path+'/'+FoundItems[items])
    print("exiting")
    return FoundItems


def download_files(local_list, list_cloud):
    print("download_files function")
    match = False
    to_be_downloaded = []
    for x in range(len(remote_list)):
        match = False
        print(
            F"looking for file:{str(remote_list[x])[53:-2]}in the local list")
        for y in range(len(local_list)):

            if (str(remote_list[x])[53:-2] == local_list[y]):
                print(F"file found at the position {y}")
                match = True
                break
        if (match == False):
            print(F"file not found, adding to list...")
            to_be_downloaded.append(remote_list[x])
    if (len(to_be_downloaded) != None):
        print("missing files have been found")
        print("calling the api download function")
        for x in range(len(to_be_downloaded)):

            print(F"[{x}]trying to download [{str(to_be_downloaded[x])[53:-2]}] with id: [{str(to_be_downloaded[x])[8:41]}] to path {path}")
            google_get_media(creds, str(to_be_downloaded[x])[
                             8:41], str(to_be_downloaded[x])[53:-2], path)
    print("exiting")


def google_login():  # logs in to google drive api, creates a token.json for the sesion and returns the credentials
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    print("google_login function")
    SCOPES = ['https://www.googleapis.com/auth/drive']  # google api app scope
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    print("exiting")
    return creds

# given a query it returns a list with the name and id of the matches


def google_search_file(creds, query):
    """Search file in drive location

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    print("google_search_file function")
    formated_list = []
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        files = []

        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name)',
                                            pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print(F'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None
    print("exiting")
    return files

# recieves file and path, proceeds to download via get_media
def google_get_media(creds, file_id, file_name, path):
    """Downloads a file
    Args:
        file_id: ID of the file to download
    Returns : IO object with location.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    print("download_file function")
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    completeName = os.path.join(path, file_name)

    if (file != None):
        with open(completeName, "wb") as f:
            file.seek(0)
            f.write(file.read())
    print("exiting")

def gui_update_progress_label():
    return f"Current Progress: {pb['value']}%"

def gui_progress():
    if pb['value'] < 100:
        pb['value'] += 20
        value_label['text'] = gui_update_progress_label()
    else:
        showinfo(message='The progress completed!')

def gui_stop():
    pb.stop()
    value_label['text'] = gui_update_progress_label()

    
    
def download_subrutine():
    path = default_path()
    
    local_list = os.listdir(path)


    for x in range(len(local_list)):
        tx_local.insert(tk.END,str(local_list[x])+'\n')

    creds = google_login()
    remote_list = google_search_file(
        creds, "'1cNCjQiB96YSMDwWpbFRBUw-PzSq5hBIa' in parents")

    #tx_remote.insert (0,remote_list)
    print("remote manifest found is:\n")
    for x in range(len(remote_list)):
        print(remote_list[x])
        print("\n")

    delete_list=delete(local_list, remote_list)
    #google_get_media(creds,'1PEftFTo0bOhZI1uj1aoiX4M9TpAwFB6s','test1.jar',path)
    download_files(local_list,remote_list)
    
# endregion

# region variable initialization
errorstate = False
creds = google_login()  # credentials inizialization for the working session
path = default_path()  # creating default path "c:/users/xxxxx/appdata/roaming"
remote_list=[]
path=""
# endregion

# region gui
root = tk.Tk()
root.title("modpack updater tool")  # window title
root.geometry("670x700")  # window size
# root.resizable(width=0, height=0)  # disable resizeability
# win.overrideredirect(True)
root['bg'] = '#011627'  # set window background

# textbox
tx_local = tk.Text(
    root,
    yscrollcommand=True,
    wrap=NONE,
    #state='disabled',
    width=35,
    height=30,
    bg='#011627',
    fg='white',
)
tx_remote = tk.Text(
    root,
    yscrollcommand=True,
    wrap=NONE,
    #state='disabled',
    width=35,
    height=30,
    bg='#011627',
    fg='white',
)
# progressbar initialization
pb = ttk.Progressbar(
    root,
    orient='horizontal',
    mode='determinate',
    length=500,
    
)
# label progress counter
value_label = tk.Label(root, 
                       text=gui_update_progress_label(),
                       bg='#011627',
                     fg='white',
                     font=15)
#right label
right_label=tk.Label(root,
                     text="Server mods",
                     bg='#011627',
                     fg='white',
                     font=15)
#left label
left_label=tk.Label(root,
                    text="Local mods",
                    bg='#011627',
                    fg='white',
                    font=15)
# start button
start_button = tk.Button(
    root,
    text='Progress',
    command=gui_progress,
    bg='#011627',
    fg='white',
)
# stop button
stop_button = tk.Button(
    root,
    text='Stop',
    command=gui_stop,
    bg='#011627',
    fg='white',
)
start_download_button=tk.Button(
    root,
    text='Start download',
    command=download_subrutine,
    bg='#011627',
    fg='white',
    
)

left_label.grid(column=0,row=1,columnspan=1,pady=10)
#right_label.grid(column=1,row=1,columnspan=1,pady=10)

# place textbox
#tx_local.grid (column=0, row=2, columnspan=2,rowspan=20, padx=25)
#tx_remote.grid(column=1, row=2, columnspan=2,rowspan=20, padx=25)
# place the progressbar
#pb.grid(column=0, row=3, columnspan=2, padx=50, pady=20)
# place grid
#value_label.grid(column=0, row=4, columnspan=2)
# place start button
start_button.grid(column=0, row=5, sticky=tk.E)
# place stop button
stop_button.grid(column=1, row=5,sticky=tk.W)
start_download_button.grid(column=2, row=5, sticky=tk.W)
# padx=10, pady=10, 
# endregion



# region logic

#download_subrutine(path)
root.mainloop()
# endregion
