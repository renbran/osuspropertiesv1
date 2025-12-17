# -*- coding: utf-8 -*-
"""
Migration script to add sequence field to property.payment.plan models
This will be executed automatically when updating the rental_management module
"""

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Add sequence field to property payment plan tables if missing"""
    
    _logger.info("Running migration to add sequence field to property payment plan tables")
    
    try:
        # Add sequence field to property_payment_plan if not exists
        cr.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'property_payment_plan' 
                    AND column_name = 'sequence'
                ) THEN
                    ALTER TABLE property_payment_plan ADD COLUMN sequence INTEGER DEFAULT 10;
                    RAISE NOTICE 'Added sequence field to property_payment_plan';
                END IF;
            END $$;
        """)
        
        # Add sequence field to property_payment_plan_line if not exists
        cr.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'property_payment_plan_line' 
                    AND column_name = 'sequence'
                ) THEN
                    ALTER TABLE property_payment_plan_line ADD COLUMN sequence INTEGER DEFAULT 10;
                    RAISE NOTICE 'Added sequence field to property_payment_plan_line';
                END IF;
            END $$;
        """)
        
        _logger.info("✅ Migration completed successfully")
        
    except Exception as e:
        _logger.error("❌ Migration failed: %s", str(e))
        raise
