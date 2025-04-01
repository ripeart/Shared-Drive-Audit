from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

# === CONFIGURATION ===
# Replace these with your actual values or load them from environment variables
ADMIN_EMAIL = 'your-admin@yourdomain.com'
KEY_FILE = 'your-service-account-key.json'
AUDITOR_EMAIL = 'auditor-group@yourdomain.com'  # Google Group used for audit access
SCOPES = ['https://www.googleapis.com/auth/drive']

# === AUTHENTICATION ===
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES, subject=ADMIN_EMAIL
)
service = build('drive', 'v3', credentials=creds)

# === FUNCTIONS ===
def auditor_already_has_access(drive_id):
    try:
        permissions = service.permissions().list(
            fileId=drive_id,
            supportsAllDrives=True,
            useDomainAdminAccess=True,
            fields="permissions(emailAddress,role,type)"
        ).execute().get('permissions', [])

        for perm in permissions:
            if perm.get('emailAddress') == AUDITOR_EMAIL and perm.get('role') == 'reader':
                return True
        return False
    except Exception as e:
        print(f"⚠️  Error checking permissions on {drive_id}: {e}")
        return False

def add_auditor_viewer(drive_id, drive_name):
    try:
        permission = {
            'type': 'group',
            'role': 'reader',
            'emailAddress': AUDITOR_EMAIL
        }

        service.permissions().create(
            fileId=drive_id,
            supportsAllDrives=True,
            useDomainAdminAccess=True,
            body=permission,
            sendNotificationEmail=False
        ).execute()

        print(f"✅ Added '{AUDITOR_EMAIL}' as Viewer to '{drive_name}'")
    except Exception as e:
        print(f"❌ Failed to add Viewer to '{drive_name}': {e}")

# === MAIN ===
page_token = None
while True:
    response = service.drives().list(
        pageSize=100,
        pageToken=page_token,
        useDomainAdminAccess=True
    ).execute()

    for drive in response.get('drives', []):
        drive_id = drive['id']
        drive_name = drive['name']

        if auditor_already_has_access(drive_id):
            print(f"⏩ Already has access: {drive_name}")
        else:
            print(f"➕ Granting Viewer to: {drive_name}")
            add_auditor_viewer(drive_id, drive_name)
            time.sleep(0.5)  # Gentle pacing to avoid quota issues

    page_token = response.get('nextPageToken')
    if not page_token:
        break
