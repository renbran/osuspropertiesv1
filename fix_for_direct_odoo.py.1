#!/usr/bin/env python3
"""
Automated fix for commission.line model field error - DIRECT ODOO INSTALLATION
Adds missing sale_order_line_id field and fixes dependencies for non-Docker setup
"""

import os
import sys
import re

def fix_commission_line_file():
    """Apply all necessary fixes to commission_line.py for direct Odoo installation"""
    
    # Possible paths for direct Odoo installation
    possible_paths = [
        "/var/odoo/osusproperties/mnt/extra-addons/commission_ax/models/commission_line.py",
        "/opt/odoo/addons/commission_ax/models/commission_line.py",
        "/odoo/addons/commission_ax/models/commission_line.py",
        "./commission_ax/models/commission_line.py",
        "commission_ax/models/commission_line.py"
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        print("❌ Could not find commission_line.py in common locations:")
        for path in possible_paths:
            print(f"   - {path}")
        print()
        print("Please provide the correct path to your commission_ax module")
        return False
    
    print(f"📝 Found file: {file_path}")
    
    # Read the current file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    print(f"📄 File size: {len(content)} characters")
    
    # Check if sale_order_line_id already exists
    if 'sale_order_line_id = fields.Many2one' in content:
        print("✅ sale_order_line_id field already exists")
    else:
        print("🔧 Adding missing sale_order_line_id field...")
        
        # Find the position after sale_order_id field definition
        pattern = r'(    sale_order_id = fields\.Many2one\(\s*[\'"]sale\.order[\'"],.*?\n    \))'
        
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print("❌ Could not find sale_order_id field to insert after")
            print("Let me try a different pattern...")
            
            # Try alternative pattern
            alt_pattern = r'(sale_order_id = fields\.Many2one\([^)]+\))'
            alt_match = re.search(alt_pattern, content, re.DOTALL)
            if alt_match:
                match = alt_match
            else:
                print("❌ Could not find sale_order_id field with any pattern")
                return False
        
        # Insert the new field after sale_order_id
        sale_order_line_field = '''
    
    # CRITICAL FIX: Add missing sale_order_line_id field
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        required=True,
        ondelete='cascade',
        index=True,
        help='Specific order line this commission is based on'
    )'''
        
        # Replace with the original field + new field
        content = content.replace(match.group(1), match.group(1) + sale_order_line_field)
        print("✅ Added sale_order_line_id field")
    
    # Fix the @depends decorator
    old_depends_patterns = [
        "@api.depends('commission_qty', 'invoiced_qty', 'sale_order_line_id.qty_invoiced')",
        "@api.depends('commission_qty', 'invoiced_qty', 'sale_order_line_id.qty_invoiced')",  # Different quotes
        r"@api\.depends\([^)]*sale_order_line_id\.qty_invoiced[^)]*\)"  # Regex pattern
    ]
    
    new_depends = "@api.depends('commission_qty', 'invoiced_qty')"
    
    depends_fixed = False
    for pattern in old_depends_patterns:
        if pattern.startswith('@api.depends'):
            if pattern in content:
                content = content.replace(pattern, new_depends)
                print("✅ Fixed @depends decorator")
                depends_fixed = True
                break
        else:
            # Regex pattern
            if re.search(pattern, content):
                content = re.sub(pattern, new_depends, content)
                print("✅ Fixed @depends decorator (regex)")
                depends_fixed = True
                break
    
    if not depends_fixed:
        print("ℹ️  @depends decorator not found or already correct")
    
    # Remove duplicate commission_category field (the long one)
    duplicate_patterns = [
        r'    # Commission categorization for profit analysis\s*commission_category = fields\.Selection\(\s*\[\s*\([\'"]external_broker[\'"].*?\], string=[\'"]Commission Category[\'"], help=[\'"]Category for profit analysis and reporting[\'"]?\)',
        r'commission_category = fields\.Selection\(\s*\[\s*\([\'"]external_broker[\'"].*?\], string=[\'"]Commission Category[\'"], help=[\'"]Category for profit analysis and reporting[\'"]?\)'
    ]
    
    duplicate_removed = False
    for pattern in duplicate_patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            print("✅ Removed duplicate commission_category field")
            duplicate_removed = True
            break
    
    if not duplicate_removed:
        print("ℹ️  Duplicate commission_category field not found or already removed")
    
    # Write the fixed content back to file
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print("✅ File successfully updated!")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        print("You may need to run this script with sudo permissions")
        return False

def main():
    """Main function to apply the fix"""
    print("=== Commission Line Model Fix - Direct Odoo Installation ===")
    print()
    print("This script fixes the missing sale_order_line_id field error")
    print("Designed for direct Odoo installation (non-Docker)")
    print()
    
    # Check if running as root or with proper permissions
    if os.geteuid() != 0:
        print("⚠️  WARNING: Not running as root. You may need sudo permissions to write the file.")
        print()
    
    if fix_commission_line_file():
        print()
        print("🎉 SUCCESS! Commission line model has been fixed.")
        print()
        print("📋 Next steps for DIRECT ODOO INSTALLATION:")
        print()
        print("1. Stop Odoo service:")
        print("   sudo systemctl stop odoo")
        print("   # OR")
        print("   sudo service odoo stop")
        print()
        print("2. Update the commission_ax module:")
        print("   sudo -u odoo /var/odoo/osusproperties/venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init --update commission_ax")
        print("   # OR find your odoo-bin path and run:")
        print("   # sudo -u odoo python3 /path/to/odoo-bin -c /path/to/odoo.conf --update commission_ax --stop-after-init")
        print()
        print("3. Start Odoo service:")
        print("   sudo systemctl start odoo")
        print("   # OR")
        print("   sudo service odoo start")
        print()
        print("4. Check Odoo logs:")
        print("   sudo tail -f /var/log/odoo/odoo.log")
        print("   # OR check your log file location")
        print()
        print("5. Alternative manual restart:")
        print("   sudo -u odoo /var/odoo/osusproperties/venv/bin/python3 src/odoo-bin -c odoo.conf")
        print()
        print("The field dependency error should be resolved!")
    else:
        print()
        print("❌ FAILED to apply fix. Please check the error messages above.")
        print()
        print("Manual fix instructions:")
        print("1. Find your commission_line.py file location")
        print("2. Edit: sudo nano /path/to/commission_ax/models/commission_line.py")
        print("3. Add the missing sale_order_line_id field after the sale_order_id field")
        print("4. Fix the @depends decorator to remove sale_order_line_id.qty_invoiced")
        sys.exit(1)

if __name__ == "__main__":
    main()