import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# === CONFIGURATION ===
# Replace these with your actual values or use environment variables
ADMIN_EMAIL = 'your-admin@yourdomain.com'
KEY_FILE = 'your-service-account-key.json'

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

# === AUTHENTICATION ===
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE,
    scopes=SCOPES,
    subject=ADMIN_EMAIL
)

service = build('drive', 'v3', credentials=creds)

# === FUNCTIONS ===
def get_permissions(drive_id):
    try:
        return service.permissions().list(
            fileId=drive_id,
            supportsAllDrives=True,
            useDomainAdminAccess=True,
            fields="permissions(emailAddress,role,type,domain)"
        ).execute().get('permissions', [])
    except:
        return []

def analyze_permissions(perms):
    role_map = {
        'organizer': [],
        'fileOrganizer': [],
        'writer': [],
        'commenter': [],
        'reader': []
    }
    uses_groups = False
    external_access = False

    for perm in perms:
        role = perm.get('role')
        if role not in role_map:
            continue

        identity = perm.get('emailAddress') or perm.get('domain') or perm.get('id')
        role_map[role].append(identity)

        if perm.get('type') == 'group':
            uses_groups = True
        if perm.get('type') == 'anyone' or (perm.get('emailAddress') and not perm['emailAddress'].endswith('@yourdomain.com')):
            external_access = True

    return role_map, uses_groups, external_access

def count_files(drive_id):
    try:
        file_count = 0
        page_token = None
        while True:
            response = service.files().list(
                corpora='drive',
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                q="trashed = false",
                fields="nextPageToken, files(id)",
                pageSize=1000,
                pageToken=page_token
            ).execute()

            file_count += len(response.get('files', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        return file_count
    except:
        return "Restricted"

# === MAIN REPORT ===
print("| Name | Description | Files | Organizers | File Organizers | Writers | Commenters | Viewers | Groups? | External? |")
print("|------|-------------|--------|------------|------------------|---------|-------------|---------|---------|------------|")

page_token = None
while True:
    response = service.drives().list(
        pageSize=100,
        pageToken=page_token,
        useDomainAdminAccess=True
    ).execute()

    for drive in response.get('drives', []):
        drive_id = drive['id']
        name = drive['name']
        desc = drive.get('description', '-') or '-'
        perms = get_permissions(drive_id)
        roles, uses_groups, external_access = analyze_permissions(perms)
        file_count = count_files(drive_id)

        print(f"| {name} | {desc} | {file_count} | "
              f"{', '.join(roles['organizer'])} | "
              f"{', '.join(roles['fileOrganizer'])} | "
              f"{', '.join(roles['writer'])} | "
              f"{', '.join(roles['commenter'])} | "
              f"{', '.join(roles['reader'])} | "
              f"{'✅' if uses_groups else '❌'} | "
              f"{'⚠️' if external_access else '✅'} |")

    page_token = response.get('nextPageToken')
    if not page_token:
        break
