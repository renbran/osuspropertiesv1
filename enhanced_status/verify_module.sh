#!/bin/bash

# 🔍 Enhanced Status Module - Server Verification Script
# Run this on the server to verify module is ready for update

echo "======================================"
echo "🔍 Enhanced Status Module Verification"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
passed=0
failed=0

# Test 1: Check we're in correct directory
echo "📂 Test 1: Checking directory structure..."
if [ -f "enhanced_status/__manifest__.py" ]; then
    echo -e "${GREEN}✅ Found enhanced_status module${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Not in correct directory. Please run from OSUSAPPS root${NC}"
    ((failed++))
    exit 1
fi
echo ""

# Test 2: Verify commission report line count
echo "📄 Test 2: Checking commission_report_template.xml..."
report_lines=$(wc -l < enhanced_status/reports/commission_report_template.xml)
if [ "$report_lines" -eq 507 ]; then
    echo -e "${GREEN}✅ Commission report has correct line count: 507${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Commission report has WRONG line count: $report_lines (expected 507)${NC}"
    echo -e "${YELLOW}⚠️  Run: git pull origin main${NC}"
    ((failed++))
fi
echo ""

# Test 3: Verify sale order view has required fields
echo "🔧 Test 3: Checking sale_order_simple_view.xml..."
field_count=$(grep -c "field name=" enhanced_status/views/sale_order_simple_view.xml)
if [ "$field_count" -ge 50 ]; then
    echo -e "${GREEN}✅ Sale order view has sufficient fields: $field_count${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Sale order view missing fields: $field_count (expected 50+)${NC}"
    echo -e "${YELLOW}⚠️  Run: git pull origin main${NC}"
    ((failed++))
fi
echo ""

# Test 4: Check for duplicate content after </odoo>
echo "🔍 Test 4: Checking for XML syntax issues..."
odoo_tag_count=$(grep -c "^</odoo>" enhanced_status/reports/commission_report_template.xml)
if [ "$odoo_tag_count" -eq 1 ]; then
    echo -e "${GREEN}✅ Commission report has single </odoo> tag${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Commission report has multiple </odoo> tags: $odoo_tag_count${NC}"
    ((failed++))
fi
echo ""

# Test 5: Check last line of commission report
echo "📝 Test 5: Checking file ends correctly..."
last_line=$(tail -n 1 enhanced_status/reports/commission_report_template.xml | tr -d '\n\r ')
if [ "$last_line" = "</odoo>" ]; then
    echo -e "${GREEN}✅ Commission report ends correctly with </odoo>${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Commission report doesn't end with </odoo>${NC}"
    echo -e "${YELLOW}   Last line: '$last_line'${NC}"
    ((failed++))
fi
echo ""

# Test 6: Verify model file exists and is valid Python
echo "🐍 Test 6: Checking sale_order_simple.py..."
if [ -f "enhanced_status/models/sale_order_simple.py" ]; then
    if python3 -m py_compile enhanced_status/models/sale_order_simple.py 2>/dev/null; then
        echo -e "${GREEN}✅ sale_order_simple.py is valid Python${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ sale_order_simple.py has syntax errors${NC}"
        ((failed++))
    fi
else
    echo -e "${RED}❌ sale_order_simple.py not found${NC}"
    ((failed++))
fi
echo ""

# Test 7: Check for required custom fields in model
echo "🔍 Test 7: Checking custom fields in model..."
custom_fields=("is_locked" "can_unlock" "has_due" "is_warning")
missing_fields=()
for field in "${custom_fields[@]}"; do
    if grep -q "$field = fields\." enhanced_status/models/sale_order_simple.py; then
        :
    else
        missing_fields+=("$field")
    fi
done

if [ ${#missing_fields[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All custom fields found in model${NC}"
    ((passed++))
else
    echo -e "${RED}❌ Missing fields in model: ${missing_fields[*]}${NC}"
    ((failed++))
fi
echo ""

# Test 8: Check git status
echo "📦 Test 8: Checking git status..."
git_status=$(git status --porcelain enhanced_status/)
if [ -z "$git_status" ]; then
    echo -e "${GREEN}✅ No uncommitted changes in enhanced_status${NC}"
    ((passed++))
else
    echo -e "${YELLOW}⚠️  Uncommitted changes detected:${NC}"
    echo "$git_status"
    echo -e "${YELLOW}⚠️  Run: git pull origin main${NC}"
    ((failed++))
fi
echo ""

# Test 9: Check current git commit
echo "🏷️  Test 9: Checking git commit..."
current_commit=$(git rev-parse --short HEAD)
echo "   Current commit: $current_commit"
if git log --oneline -1 | grep -q "deployment guide"; then
    echo -e "${GREEN}✅ Latest commit includes deployment guide${NC}"
    ((passed++))
else
    echo -e "${YELLOW}⚠️  Not on latest commit. Run: git pull origin main${NC}"
fi
echo ""

# Summary
echo "======================================"
echo "📊 VERIFICATION SUMMARY"
echo "======================================"
echo -e "${GREEN}✅ Passed: $passed${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}❌ Failed: $failed${NC}"
else
    echo -e "${GREEN}❌ Failed: $failed${NC}"
fi
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🚀 Module is ready for update. Run:"
    echo ""
    echo "   python3 odoo-bin -d osusproperties -u enhanced_status --stop-after-init"
    echo ""
    echo "   OR"
    echo ""
    echo "   sudo systemctl restart odoo"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ ISSUES DETECTED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "⚠️  Please fix issues before updating module:"
    echo ""
    echo "1. Pull latest code:"
    echo "   git pull origin main"
    echo ""
    echo "2. Re-run this verification script"
    echo ""
fi

exit $failed
