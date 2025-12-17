# Migration Guide: v1.0 → v2.0

## Overview

Version 2.0 introduces **breaking changes** to eliminate conflicts and leverage standard Odoo UTM tracking. This guide helps you migrate existing data and configurations.

---

## 🔄 What Changed?

### Field Changes

| v1.0 Field | v2.0 Field | Change Type |
|------------|------------|-------------|
| `lead_id` | `opportunity_id` | **RENAMED** |
| `sale_lead_source_id` | `source_id` | **REPLACED** with utm.source |
| `sale_campaign_source_id` | `campaign_id` | **REPLACED** with utm.campaign |
| `deal_stage` | `deal_stage` | ✅ No change |

### Model Changes

| v1.0 Model | v2.0 Model | Status |
|------------|------------|--------|
| `sale.lead.source` | `utm.source` | ⚠️ REMOVED |
| `sale.campaign.source` | `utm.campaign` | ⚠️ REMOVED |

---

## ⚠️ Before Upgrading

### Step 1: Backup Your Database

```bash
# Create database backup
docker-compose exec db pg_dump -U odoo -d your_db > backup_before_v2_$(date +%Y%m%d).sql
```

### Step 2: Export Existing Data

If you were using v1.0, export your custom sources and campaigns:

```python
# Run in Odoo shell: docker-compose exec odoo odoo shell -d your_db
# Export sale.lead.source data
LeadSource = env['sale.lead.source']
sources = LeadSource.search([])
print("Lead Sources to migrate:")
for source in sources:
    print(f"  - {source.name}")

# Export sale.campaign.source data
CampaignSource = env['sale.campaign.source']
campaigns = CampaignSource.search([])
print("\nCampaign Sources to migrate:")
for campaign in campaigns:
    print(f"  - {campaign.name}")
```

---

## 🚀 Migration Steps

### Option A: Fresh Installation (No v1.0 Data)

If you never used v1.0 or have no important data:

```bash
# 1. Uninstall old version (if installed)
docker-compose exec odoo odoo -u sale_deal_tracking --stop-after-init -d your_db

# 2. Update to v2.0 code (this is already done if you're reading this)

# 3. Upgrade module
docker-compose exec odoo odoo -u sale_deal_tracking --stop-after-init -d your_db

# 4. Restart Odoo
docker-compose restart odoo
```

### Option B: Migration with Data Preservation

If you have existing v1.0 data to migrate:

#### Step 1: Create Migration Script

Create file: `migration_v1_to_v2.py`

```python
#!/usr/bin/env python3
"""
Migration script for sale_deal_tracking v1.0 → v2.0
Migrates custom sources/campaigns to standard UTM models
"""

def migrate_to_utm(env):
    """
    Migrate custom sale.lead.source and sale.campaign.source to UTM models
    """
    
    print("=" * 60)
    print("MIGRATION: sale_deal_tracking v1.0 → v2.0")
    print("=" * 60)
    
    # 1. Check if old models exist
    if 'sale.lead.source' not in env:
        print("✓ No sale.lead.source model found (already migrated or v1 not installed)")
    else:
        print("\n[1/4] Migrating Lead Sources...")
        LeadSource = env['sale.lead.source']
        UtmSource = env['utm.source']
        
        old_sources = LeadSource.search([])
        mapping = {}  # Old ID → New ID
        
        for old_source in old_sources:
            # Check if already exists in UTM
            existing = UtmSource.search([('name', '=', old_source.name)], limit=1)
            
            if existing:
                print(f"  ✓ '{old_source.name}' already exists in UTM")
                mapping[old_source.id] = existing.id
            else:
                # Create in UTM
                new_source = UtmSource.create({'name': old_source.name})
                print(f"  ✓ Migrated '{old_source.name}' → utm.source (ID: {new_source.id})")
                mapping[old_source.id] = new_source.id
        
        # 2. Update sale orders
        print("\n[2/4] Updating Sale Orders...")
        SaleOrder = env['sale.order']
        orders = SaleOrder.search([('sale_lead_source_id', '!=', False)])
        
        for order in orders:
            if order.sale_lead_source_id.id in mapping:
                order.write({'source_id': mapping[order.sale_lead_source_id.id]})
                print(f"  ✓ Updated SO/{order.name}")
        
        print(f"  ✓ Migrated {len(orders)} sale orders")
    
    # 3. Migrate Campaign Sources
    if 'sale.campaign.source' not in env:
        print("\n✓ No sale.campaign.source model found")
    else:
        print("\n[3/4] Migrating Campaign Sources...")
        CampaignSource = env['sale.campaign.source']
        UtmCampaign = env['utm.campaign']
        
        old_campaigns = CampaignSource.search([])
        mapping = {}
        
        for old_campaign in old_campaigns:
            existing = UtmCampaign.search([('name', '=', old_campaign.name)], limit=1)
            
            if existing:
                print(f"  ✓ '{old_campaign.name}' already exists in UTM")
                mapping[old_campaign.id] = existing.id
            else:
                new_campaign = UtmCampaign.create({'name': old_campaign.name})
                print(f"  ✓ Migrated '{old_campaign.name}' → utm.campaign (ID: {new_campaign.id})")
                mapping[old_campaign.id] = new_campaign.id
        
        # Update sale orders
        orders = SaleOrder.search([('sale_campaign_source_id', '!=', False)])
        for order in orders:
            if order.sale_campaign_source_id.id in mapping:
                order.write({'campaign_id': mapping[order.sale_campaign_source_id.id]})
        
        print(f"  ✓ Migrated {len(orders)} sale orders")
    
    # 4. Rename lead_id to opportunity_id (field rename in model)
    print("\n[4/4] Renaming lead_id → opportunity_id...")
    print("  ✓ This is handled automatically by Odoo ORM")
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Odoo: docker-compose restart odoo")
    print("2. Test in UI to verify data migrated correctly")
    print("3. Delete old custom models if everything works")
    
    env.cr.commit()

# Run migration
if __name__ == '__main__':
    import odoo
    from odoo import api, SUPERUSER_ID
    
    # Connect to Odoo
    db_name = 'your_db'  # CHANGE THIS
    
    with api.Environment.manage():
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            migrate_to_utm(env)
```

#### Step 2: Run Migration

```bash
# Make script executable
chmod +x migration_v1_to_v2.py

# Run migration
docker-compose exec odoo python3 /mnt/extra-addons/sale_deal_tracking/migration_v1_to_v2.py

# Or run via Odoo shell
docker-compose exec odoo odoo shell -d your_db < migration_v1_to_v2.py
```

#### Step 3: Verify Migration

```bash
# Check migration results in Odoo shell
docker-compose exec odoo odoo shell -d your_db

# In shell:
>>> # Check UTM sources created
>>> env['utm.source'].search([]).mapped('name')
['Direct Sales', 'Referral', 'Website', ...]

>>> # Check sale orders have source_id populated
>>> orders = env['sale.order'].search([('source_id', '!=', False)])
>>> print(f"Orders with UTM source: {len(orders)}")

>>> # Check opportunities have deal_stage
>>> leads = env['crm.lead'].search([('deal_stage', '!=', False)])
>>> print(f"Opportunities with deal stage: {len(leads)}")
```

---

## ✅ Post-Migration Checklist

### 1. Verify Data Integrity

- [ ] All old lead sources migrated to utm.source
- [ ] All old campaign sources migrated to utm.campaign  
- [ ] Sale orders have `opportunity_id` (renamed from lead_id)
- [ ] Sale orders have `source_id` instead of `sale_lead_source_id`
- [ ] Sale orders have `campaign_id` instead of `sale_campaign_source_id`
- [ ] Deal stages preserved on all records

### 2. Test Key Workflows

- [ ] Create new opportunity → Set deal stage → Works?
- [ ] Create quotation from opportunity → Deal stage syncs?
- [ ] Update deal stage on sale order → Syncs to opportunity?
- [ ] Smart button shows linked quotations?
- [ ] Search filters work (New Deals, Hot Deals, etc.)?

### 3. Update Custom Code (If Any)

If you have custom code referencing old fields:

**Python Code:**
```python
# OLD v1.0
order.lead_id
order.sale_lead_source_id
order.sale_campaign_source_id

# NEW v2.0
order.opportunity_id
order.source_id
order.campaign_id
```

**XML Views:**
```xml
<!-- OLD v1.0 -->
<field name="lead_id"/>
<field name="sale_lead_source_id"/>
<field name="sale_campaign_source_id"/>

<!-- NEW v2.0 -->
<field name="opportunity_id"/>
<field name="source_id"/>
<field name="campaign_id"/>
```

**Domains/Filters:**
```python
# OLD v1.0
[('sale_lead_source_id', '=', source.id)]

# NEW v2.0
[('source_id', '=', source.id)]
```

### 4. Clean Up Old Data (Optional)

After verifying everything works:

```python
# Run in Odoo shell
# ONLY RUN THIS IF MIGRATION WAS SUCCESSFUL!

# Drop old models (if they still exist)
env.cr.execute("DROP TABLE IF EXISTS sale_lead_source CASCADE")
env.cr.execute("DROP TABLE IF EXISTS sale_campaign_source CASCADE")
env.cr.commit()
```

---

## 🐛 Troubleshooting Migration

### Issue: "Model 'sale.lead.source' not found"

**Cause:** Already migrated or v1.0 was never installed  
**Solution:** This is fine! Skip to fresh installation method.

### Issue: Data not migrated

**Cause:** Migration script didn't run properly  
**Solution:**
1. Check Odoo logs for errors
2. Verify database connection in script
3. Run script again (it's idempotent)

### Issue: "Field 'lead_id' does not exist"

**Cause:** Odoo hasn't renamed the field yet  
**Solution:**
```bash
# Update module
docker-compose exec odoo odoo -u sale_deal_tracking --stop-after-init -d your_db

# Restart
docker-compose restart odoo
```

### Issue: Custom modules reference old fields

**Cause:** Other custom modules still use v1.0 field names  
**Solution:** Update those modules to use v2.0 field names (see checklist above)

---

## 🔄 Rollback Plan

If migration fails and you need to rollback:

### Option 1: Restore Database Backup

```bash
# Stop Odoo
docker-compose stop odoo

# Restore database
docker-compose exec db psql -U odoo < backup_before_v2_YYYYMMDD.sql

# Revert code to v1.0
git checkout <v1.0_commit_hash>

# Restart
docker-compose up -d
```

### Option 2: Uninstall Module

```bash
# Uninstall via UI
# Apps → Sale Deal Tracking → Uninstall

# Or via CLI
docker-compose exec odoo odoo -u sale_deal_tracking --stop-after-init -d your_db
```

---

## 📊 Migration Comparison

### Before (v1.0)
```
sale.order
  ├── lead_id → crm.lead
  ├── sale_lead_source_id → sale.lead.source ❌
  └── sale_campaign_source_id → sale.campaign.source ❌

Custom Models:
  ├── sale.lead.source
  └── sale.campaign.source
```

### After (v2.0)
```
sale.order
  ├── opportunity_id → crm.lead ✅ (renamed)
  ├── source_id → utm.source ✅ (standard)
  ├── campaign_id → utm.campaign ✅ (standard)
  └── medium_id → utm.medium ✅ (new)

Standard Models:
  ├── utm.source (already exists)
  ├── utm.campaign (already exists)
  └── utm.medium (already exists)
```

---

## 📞 Need Help?

**Migration Issues?**
1. Check logs: `docker-compose logs -f odoo | grep sale_deal_tracking`
2. Verify backup was created before starting
3. Review this guide's troubleshooting section
4. Test in staging environment first

**Questions?**
- Review the main README.md for full v2.0 documentation
- Check compatibility matrix for module interactions
- Test automated sync functionality thoroughly

---

## 📝 Timeline Recommendation

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Preparation** | 1 day | Backup DB, export data, review guide |
| **Testing** | 2-3 days | Test migration in staging environment |
| **Migration** | 1 day | Run migration in production |
| **Validation** | 1-2 days | Verify data, test workflows, monitor |

**Total:** ~5-7 days for safe migration

---

Good luck with your migration! 🚀
