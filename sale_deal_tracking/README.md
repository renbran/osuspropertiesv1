# Sale Deal Tracking Module v2.0

## 🎯 Overview

The **Sale Deal Tracking** module provides unified deal stage tracking across CRM and Sales with automatic synchronization, leveraging Odoo's standard UTM (Urchin Tracking Module) system for marketing attribution.

### Key Features

✅ **Unified Deal Stages** - Track deals with 9 standardized stages across CRM and Sales  
✅ **Automatic Synchronization** - Deal stages sync bidirectionally between opportunities and quotations  
✅ **Standard UTM Integration** - Uses native Odoo utm.source, utm.campaign, and utm.medium models  
✅ **No Conflicts** - Designed to coexist with rental_management, marina_living_zapier_integration, and other modules  
✅ **Smart Buttons** - Quick navigation between linked opportunities and quotations  
✅ **Enhanced Filters** - Pre-configured search filters for deal stages and sources  

---

## 📋 Deal Stages

| Stage | Description | Use Case |
|-------|-------------|----------|
| **New** | Initial contact | Lead just came in, not yet contacted |
| **Attempt** | Outreach in progress | Trying to reach the prospect |
| **Contacted** | Successfully reached | Had initial conversation |
| **Option Sent** | Proposal/quote provided | Formal offer has been sent |
| **Hot** | High interest, likely to close | Strong buying signals |
| **Idle** | Low activity, needs follow-up | Deal went cold, requires nurturing |
| **Junk** | Not qualified, completely lost | Not a valid opportunity |
| **Unsuccessful** | Lost but follow up after 60 days | May have future potential |
| **Customer (Won)** | Deal closed successfully | Converted to customer |

---

## 🔧 Installation

### Prerequisites

Ensure these modules are installed:
- `sale_management` - Core Sales module
- `crm` - CRM/Leads module
- `utm` - Standard Odoo UTM tracking
- `le_sale_type` - Required for proper view inheritance

### Install Steps

1. **Update Apps List**
   ```bash
   docker-compose exec odoo odoo -u all --stop-after-init -d your_db
   ```

2. **Install Module**
   - Via UI: Apps → Search "Sale Deal Tracking" → Install
   - Via CLI:
   ```bash
   docker-compose exec odoo odoo -i sale_deal_tracking --stop-after-init -d your_db
   ```

3. **Verify Installation**
   - Open a Sale Order → Check for "Deal Tracking" and "Marketing Source" groups
   - Open a CRM Opportunity → Check for deal_stage field in header

---

## 💡 Usage Guide

### For Sales Team

#### Creating a Quotation from Opportunity

1. Open CRM → Opportunities
2. Set the **Deal Stage** (e.g., "Hot")
3. Click "New Quotation" button
4. The quotation automatically inherits:
   - Deal Stage
   - Lead Source (UTM Source)
   - Campaign
   - Medium

#### Linking Existing Quotation to Opportunity

1. Open Sales Order
2. In "Deal Tracking" section, select **Opportunity/Lead**
3. Deal stage and UTM fields populate automatically
4. Changes to deal stage sync back to the opportunity

#### Tracking Deal Progress

**In Sale Order:**
- Use the **Deal Stage** dropdown to update progress
- Changes automatically sync to linked opportunity
- View "Deal Stage Last Updated" timestamp

**Quick Filters:**
- Sales → Orders → Filter by:
  - "New Deals"
  - "Hot Deals"
  - "Options Sent"
  - "Won Deals"

### For CRM Team

#### Managing Opportunities with Deal Stages

1. Open CRM → Opportunities
2. Use the **Deal Stage** statusbar in header for quick updates
3. Click on stage to change (visual, clickable statusbar)
4. View linked quotations via smart button

#### Viewing Linked Quotations

- Click the **Quotations** smart button (top right)
- Shows count of all quotations linked to this opportunity
- Filtered view of related sales orders

#### Setting Marketing Attribution

**UTM Fields Available:**
- **Lead Source** - Where the lead came from (Website, Referral, Cold Call, etc.)
- **Campaign** - Which marketing campaign (Q4 2025 Campaign, Product Launch, etc.)
- **Medium** - How they found you (Email, Phone, Social, etc.)

Configure sources/campaigns:
- Sales → Configuration → Marketing → Sources
- Sales → Configuration → Marketing → Campaigns

---

## 🔄 Automatic Synchronization

### How It Works

#### Scenario 1: Create Quotation from Opportunity
```
CRM Opportunity (deal_stage: "Hot")
         ↓ [Click "New Quotation"]
Sale Order (deal_stage: "Hot") ✓ Auto-populated
```

#### Scenario 2: Link Opportunity to Existing Order
```
Sale Order → Select Opportunity
         ↓ [Automatic sync]
Sale Order inherits:
  - deal_stage
  - source_id (UTM)
  - campaign_id (UTM)
  - medium_id (UTM)
```

#### Scenario 3: Update Deal Stage in Sales
```
Sale Order: Change deal_stage "Hot" → "Customer (Won)"
         ↓ [Automatic bi-directional sync]
CRM Opportunity: deal_stage updated to "Customer (Won)" ✓
```

#### Scenario 4: Update Deal Stage in CRM
```
CRM Opportunity: Change deal_stage "Contacted" → "Option Sent"
         ↓ [Automatic sync]
All linked Sale Orders: deal_stage updated to "Option Sent" ✓
```

### Sync Control

**Default Behavior:** Automatic sync is **enabled**

**Disable Sync Temporarily (Code):**
```python
# When updating sale order without syncing to CRM
sale_order.with_context(sync_deal_stage_to_crm=False).write({
    'deal_stage': 'hot'
})

# When updating opportunity without syncing to sales
opportunity.with_context(sync_deal_stage_to_sale=False).write({
    'deal_stage': 'contacted'
})
```

---

## 🆚 Why Use This vs Custom Models?

### Decision: Standard UTM vs Custom Models

We chose **Standard Odoo UTM** because:

| Standard UTM ✅ | Custom Models ❌ |
|----------------|------------------|
| Already integrated with CRM | Need custom integration |
| Compatible with existing modules | Potential conflicts |
| Used by: tk_portal_partner_leads, marina_living_zapier_integration, auto_lead_capture | Data fragmentation |
| One source of truth | Multiple tracking systems |
| Standard reports work | Custom reports needed |
| No additional maintenance | Need ongoing updates |

### UTM Models Used

- `utm.source` - Lead/customer source tracking
- `utm.campaign` - Marketing campaign attribution
- `utm.medium` - Marketing medium/channel

Configure via: **Sales → Configuration → Marketing**

---

## 🔍 Field Reference

### Sale Order Fields

| Field | Type | Description |
|-------|------|-------------|
| `opportunity_id` | Many2one(crm.lead) | Linked CRM opportunity (renamed from lead_id) |
| `source_id` | Many2one(utm.source) | Lead source (Website, Referral, etc.) |
| `campaign_id` | Many2one(utm.campaign) | Marketing campaign |
| `medium_id` | Many2one(utm.medium) | Marketing medium (Email, Phone, etc.) |
| `deal_stage` | Selection | Current deal stage (9 options) |
| `deal_stage_updated` | Datetime | Timestamp of last stage change |

### CRM Lead Fields

| Field | Type | Description |
|-------|------|-------------|
| `deal_stage` | Selection | Current deal stage (syncs with sale orders) |
| `deal_stage_updated` | Datetime | Timestamp of last stage change |
| `sale_order_count` | Integer (computed) | Number of linked quotations |

---

## 🎨 UI Enhancements

### Sale Order Form View

**Location:** After "Sale Type" field

**Sections Added:**
1. **Deal Tracking** group
   - Opportunity/Lead (with domain filter)
   - Deal Stage (statusbar widget, clickable)
   - Deal Stage Last Updated (readonly timestamp)

2. **Marketing Source** group
   - Lead Source (UTM)
   - Campaign (UTM)
   - Medium (UTM)

### CRM Opportunity Form View

**Enhancements:**
- Deal Stage statusbar in header (next to Kanban stage)
- Deal Stage Updated timestamp in info section
- Smart button showing count of linked quotations
- Click smart button to view/create quotations

### List/Tree Views

**Color Coding:**
- 🟢 Green: Customer (Won)
- 🟡 Yellow: Hot, Option Sent
- 🔴 Red: Junk
- ⚪ Gray: Idle, Unsuccessful

---

## 🔌 Compatibility

### Confirmed Compatible With

✅ **rental_management** - No field conflicts (their `lead_id` is on different models)  
✅ **marina_living_zapier_integration** - Uses same UTM system  
✅ **auto_lead_capture** - Uses same UTM sources  
✅ **tk_portal_partner_leads** - Uses same UTM tracking  
✅ **le_sale_type** - Proper view inheritance priority  
✅ **enhanced_status** - No statusbar conflicts  
✅ **commission_ax** - No field overlaps  
✅ **custom_sales** - Compatible field additions  

### Module Dependencies

```python
"depends": [
    "sale_management",  # Core Sales
    "crm",              # CRM/Opportunities
    "utm",              # Standard UTM tracking
    "le_sale_type",     # For view positioning
]
```

---

## 🐛 Troubleshooting

### Issue: Deal stage not syncing

**Cause:** Sync context disabled  
**Fix:** Ensure you're not manually disabling sync context

### Issue: "Field 'sale_order_type_id' not found"

**Cause:** `le_sale_type` module not installed  
**Fix:** Install `le_sale_type` module first

### Issue: UTM Source/Campaign dropdown empty

**Cause:** No UTM records created  
**Fix:** Sales → Configuration → Marketing → Create sources/campaigns

### Issue: Opportunity smart button not showing quotations

**Cause:** Sale orders not linked via `opportunity_id` field  
**Fix:** Edit sale order → Set "Opportunity/Lead" field

---

## 📊 Reports & Analytics

### Group By Options

**In Sales Orders:**
- Deal Stage
- Lead Source
- Campaign

**In CRM Opportunities:**
- Deal Stage

### Pre-configured Filters

**Sales:**
- New Deals
- Hot Deals
- Options Sent
- Won Deals
- Has Opportunity

**CRM:**
- New Deals
- Hot Deals
- Options Sent
- Won Deals

---

## 🚀 Advanced Customization

### Adding Custom Deal Stages

Edit: `sale_deal_tracking/models/sale_order.py` and `crm_lead.py`

```python
DEAL_STAGE_SELECTION = [
    ('new', 'New'),
    ('custom_stage', 'My Custom Stage'),  # Add here
    # ... rest of stages
]
```

### Customizing Sync Logic

Override `write()` method in `sale_order.py` or `crm_lead.py`:

```python
def write(self, vals):
    if 'deal_stage' in vals:
        # Add custom logic here
        pass
    return super().write(vals)
```

### Creating Workflow Automations

Use Odoo's Automated Actions:
1. Settings → Technical → Automation → Automated Actions
2. Create action on `sale.order` or `crm.lead`
3. Trigger: "On Update" → Field: `deal_stage`
4. Add custom Python code or server actions

---

## 🎓 Best Practices

### 1. Consistent Stage Naming
- Always use the same deal stage for similar situations
- Train team on when to use each stage

### 2. Link Opportunities Early
- Link quotations to opportunities as soon as possible
- Enables automatic sync and better reporting

### 3. Use UTM Consistently
- Set source/campaign on all opportunities
- Enables marketing ROI tracking

### 4. Regular Stage Updates
- Update deal stage as conversations progress
- Provides accurate pipeline visibility

### 5. Review Unsuccessful Deals
- Set reminders for "Unsuccessful" deals (60-day follow-up)
- Move "Junk" deals to lost status to clean pipeline

---

## 📈 Version History

### v2.0.0 (Current)
- ✅ Refactored to use standard UTM models
- ✅ Renamed `lead_id` to `opportunity_id` (avoid conflicts)
- ✅ Added automatic bi-directional sync
- ✅ Added smart buttons and enhanced filters
- ✅ Added view priorities for proper inheritance
- ✅ Full compatibility with existing modules

### v1.0.0 (Deprecated)
- ❌ Used custom `sale.lead.source` and `sale.campaign.source` models
- ❌ Had potential conflicts with rental_management
- ❌ No automatic synchronization

---

## 📞 Support

**Issues or Questions?**
- Check logs: `docker-compose logs -f odoo | grep sale_deal_tracking`
- Review this README's Troubleshooting section
- Verify dependencies are installed

**Testing Checklist:**
```bash
# 1. Install module
docker-compose exec odoo odoo -i sale_deal_tracking --stop-after-init -d odoo

# 2. Verify no errors
docker-compose logs odoo | grep -i "error\|warning" | grep sale_deal_tracking

# 3. Test in UI
# - Create opportunity → Set deal stage → Create quotation
# - Verify stage copied to quotation
# - Update quotation stage → Verify opportunity updates
# - Check smart buttons work
```

---

## 📝 License

LGPL-3

---

## 👥 Credits

**Author:** OSUSAPPS  
**Version:** 2.0.0  
**Compatible:** Odoo 17.0  
