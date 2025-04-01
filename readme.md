# Google Workspace Shared Drive RBAC Audit

Thess scripts generate a read-only access audit report for all Shared Drives in your Google Workspace domain. They lists roles, access types, file counts, and external sharing status to help teams enforce RBAC policies.

## 🚀 Usage

1. Create a Google Cloud project and service account with domain-wide delegation.
2. Authorize the following scopes:
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.metadata.readonly`
3. Replace `ADMIN_EMAIL` and `KEY_FILE` in the script with your own values.
4. Run the script in Google Cloud Shell or any Python 3 environment.

## 📄 Output

The script prints a Markdown-formatted table suitable for pasting into Confluence or Google Docs.

