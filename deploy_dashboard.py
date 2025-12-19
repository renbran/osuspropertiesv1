"""
Dashboard Module Deployment Helper
Deploys osus_sales_invoicing_dashboard to the Odoo server

Usage:
    python deploy_dashboard.py

Requirements:
    - psutil (pip install psutil)
    - or use manual SCP commands
"""

import os
import sys
import subprocess

LOCAL_MODULE_PATH = r"d:\RUNNING APPS\odoo17\osuspropertiesv1\osus_sales_invoicing_dashboard"
SERVER_HOST = "139.84.163.11"
SERVER_USER = "odoo"
SERVER_PATH = "/mnt/odoo17/addons/osus_sales_invoicing_dashboard"

FILES_TO_UPLOAD = [
    ("__manifest__.py", "__manifest__.py"),
    ("models/sales_invoicing_dashboard.py", "models/sales_invoicing_dashboard.py"),
    ("static/src/js/dashboard_filters.js", "static/src/js/dashboard_filters.js"),
    ("views/dashboard_views.xml", "views/dashboard_views.xml"),
]

def upload_file(local_file, remote_file):
    """Upload a single file to the server"""
    local_path = os.path.join(LOCAL_MODULE_PATH, local_file)
    remote_path = f"{SERVER_USER}@{SERVER_HOST}:{SERVER_PATH}/{remote_file}"
    
    if not os.path.exists(local_path):
        print(f"  ✗ File not found: {local_path}")
        return False
    
    try:
        # Using scp command
        cmd = ["scp", "-P", "22", local_path, remote_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Uploaded {local_file}")
            return True
        else:
            print(f"  ✗ Failed to upload {local_file}")
            print(f"    Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"  ! scp not found. Please install OpenSSH or use WinSCP")
        print(f"  ! Manual upload: {local_path} -> {remote_path}")
        return False
    except Exception as e:
        print(f"  ✗ Error uploading {local_file}: {e}")
        return False

def main():
    print("=" * 70)
    print("OSUS Sales & Invoicing Dashboard - Deployment Helper")
    print("=" * 70)
    print(f"\nModule Version: 17.0.1.0.4")
    print(f"Server: {SERVER_HOST}")
    print(f"Target Path: {SERVER_PATH}\n")
    
    # Check if local module exists
    if not os.path.exists(LOCAL_MODULE_PATH):
        print("✗ Error: Local module path not found!")
        print(f"  Expected: {LOCAL_MODULE_PATH}")
        sys.exit(1)
    
    print("Uploading files...\n")
    
    success_count = 0
    for local_file, remote_file in FILES_TO_UPLOAD:
        if upload_file(local_file, remote_file):
            success_count += 1
    
    print(f"\nUpload Summary: {success_count}/{len(FILES_TO_UPLOAD)} files uploaded")
    
    if success_count == len(FILES_TO_UPLOAD):
        print("\n✓ All files uploaded successfully!")
        print("\nNext Steps:")
        print("  1. Log in to Odoo at http://139.84.163.11:8069")
        print("  2. Go to Apps > Update Apps List")
        print("  3. Search for 'OSUS Sales & Invoicing Dashboard'")
        print("  4. Click on the module")
        print("  5. Click the 'Upgrade' button")
        print("  6. Wait for the upgrade to complete")
        print("  7. Go to Dashboards > Sales & Invoicing Dashboard")
        print("  8. Test the filters - they should now work!\n")
    else:
        print("\n✗ Some files failed to upload. Please try again or use WinSCP.")
        print("\nAlternative: Manual Upload via WinSCP")
        print("  1. Open WinSCP")
        print("  2. Connect to 139.84.163.11 as user 'odoo'")
        print("  3. Navigate to /mnt/odoo17/addons/osus_sales_invoicing_dashboard")
        print("  4. Upload files from:")
        for local_file, _ in FILES_TO_UPLOAD:
            print(f"       {os.path.join(LOCAL_MODULE_PATH, local_file)}")

if __name__ == "__main__":
    main()
