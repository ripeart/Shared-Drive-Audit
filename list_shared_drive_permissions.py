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

# === AUTHENTICATION WITH DOMAIN-WIDE DELEGATION ===
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE,
    scopes=SCOPES,
    subject=ADMIN_EMAIL
)

# === BUILD DRIVE API CLIENT ===
service = build('drive', 'v3', credentials=creds)

# === LIST SHARED DRIVES AND THEIR PERMISSIONS ===
page_token = None
print("Shared Drives and Permissions:\n")

while True:
    response = service.drives().list(
        pageSize=100,
        pageToken=page_token,
        useDomainAdminAccess=True
    ).execute()

    for drive in response.get('drives', []):
        drive_id = drive['id']
        drive_name = drive['name']
        print(f"📁 {drive_name} ({drive_id})")

        try:
            permissions = service.permissions().list(
                fileId=drive_id,
                supportsAllDrives=True,
                useDomainAdminAccess=True,
                fields="permissions(id,emailAddress,displayName,role,type,domain)"
            ).execute()

            for perm in permissions.get('permissions', []):
                identity = (
                    perm.get('emailAddress')
                    or perm.get('domain')
                    or perm.get('displayName')
                    or perm.get('id')
                )
                role = perm.get('role')
                access_type = perm.get('type')  # user / group / domain / anyone
                print(f"  👤 {identity} | Role: {role} | Type: {access_type}")

        except Exception as e:
            print(f"  ⚠️  Could not fetch permissions: {e}")

        print("")  # Blank line between drives

    page_token = response.get('nextPageToken')
    if not page_token:
        break
