/** @odoo-module **/

import { FormController } from '@web/views/form/form_controller';
import { patch } from '@web/core/utils/patch';
import DashboardFilterHandler, { FILTER_FIELDS, COMPUTED_FIELDS } from './dashboard_filters';

/**
 * Dashboard Form Controller Patch
 *
 * Extends the standard Odoo FormController to add automatic filter refresh
 * functionality for the Sales & Invoicing Dashboard.
 *
 * This patch:
 * 1. Detects when the dashboard form is loaded
 * 2. Initializes filter change listeners
 * 3. Handles automatic form saves and data refresh when filters change
 */

patch(FormController.prototype, {
    /**
     * Extended setup to initialize dashboard filter handlers
     */
    setup() {
        super.setup(...arguments);
        this._dashboardFilterInitialized = false;
    },

    /**
     * Hook into onRecordChanged to detect filter changes
     * This is called whenever a field value changes in the form
     */
    async onRecordChanged(record, changes) {
        const result = await super.onRecordChanged(...arguments);

        // Only apply to dashboard model
        if (this.props.resModel !== 'osus.sales.invoicing.dashboard') {
            return result;
        }

        // Initialize filter listeners on first render
        if (!this._dashboardFilterInitialized && this.model.root) {
            this._initializeDashboardFilters();
            this._dashboardFilterInitialized = true;
        }

        // Check if any filter field changed
        if (changes && this._isFilterFieldChanged(changes)) {
            await this._handleFilterChange();
        }

        return result;
    },

    /**
     * Check if any filter field was changed
     */
    _isFilterFieldChanged(changes) {
        if (!changes || typeof changes !== 'object') {
            return false;
        }

        // Check if any changed field is a filter field
        for (const fieldName of FILTER_FIELDS) {
            if (fieldName in changes) {
                console.debug(`Dashboard: filter field "${fieldName}" changed`);
                return true;
            }
        }
        return false;
    },

    /**
     * Handle filter field changes
     */
    async _handleFilterChange() {
        console.debug('Dashboard: filter changed, refreshing data...');

        // Debounce to avoid excessive refreshes
        if (this._filterChangeTimeout) {
            clearTimeout(this._filterChangeTimeout);
        }

        this._filterChangeTimeout = setTimeout(async () => {
            try {
                // Collect current filter values from the form
                const filterValues = this._getFilterValues();
                console.debug('Dashboard: collected filter values', filterValues);

                // Use the proper DashboardFilterHandler to update filters and refresh data
                const refreshedData = await DashboardFilterHandler.refreshDashboardData(filterValues);
                console.debug('Dashboard: received refreshed data', refreshedData);

                // Update the form with the refreshed computed values
                await this._updateComputedFields(refreshedData);

                // Render the updated form
                this.render();
                console.debug('Dashboard: form rendered with updated data');
            } catch (error) {
                console.error('Dashboard: error refreshing after filter change', error);
            }
        }, 300); // 300ms debounce
    },

    /**
     * Collect current filter field values from the form
     */
    _getFilterValues() {
        const filterValues = {};
        const record = this.model.root;

        if (!record || !record.data) {
            return filterValues;
        }

        // Collect all filter field values
        for (const fieldName of FILTER_FIELDS) {
            const fieldValue = record.data[fieldName];

            // Handle different field types
            if (fieldValue === undefined || fieldValue === null) {
                continue;
            }

            // For Many2one fields, extract the ID
            if (Array.isArray(fieldValue) && fieldValue.length === 2) {
                filterValues[fieldName] = fieldValue[0] || false;
            }
            // For Many2many fields, extract the list of IDs
            else if (fieldValue && fieldValue.records) {
                filterValues[fieldName] = fieldValue.records.map(r => r.resId);
            }
            // For other fields (dates, selection), use the value directly
            else {
                filterValues[fieldName] = fieldValue;
            }
        }

        return filterValues;
    },

    /**
     * Update form fields with refreshed computed values
     */
    async _updateComputedFields(refreshedData) {
        if (!refreshedData || !this.model.root) {
            return;
        }

        const record = this.model.root;

        // Update each computed field with the refreshed value
        for (const [fieldName, fieldValue] of Object.entries(refreshedData)) {
            if (COMPUTED_FIELDS.includes(fieldName) && fieldName in record.data) {
                // Update the field value directly in the record's data
                record.data[fieldName] = fieldValue;
            }
        }

        // Mark the record as not dirty since we're syncing with server state
        if (record._changes) {
            record._changes = {};
        }
    },

    /**
     * Initialize dashboard-specific filter handling
     */
    _initializeDashboardFilters() {
        console.debug('Dashboard: initializing filter listeners');

        // Additional setup for filter fields if needed
        // The main filter handling is now done through onRecordChanged

        // Listen for manual form resets
        if (this.model.root) {
            const originalDiscard = this.model.root.discard.bind(this.model.root);
            this.model.root.discard = async (...args) => {
                const result = await originalDiscard(...args);
                console.debug('Dashboard: form discarded/reset, ensuring filters persist');

                // After discard, collect filter values and refresh
                // This ensures that if filters were changed, they persist properly
                setTimeout(async () => {
                    try {
                        const filterValues = this._getFilterValues();

                        // If there are filter values, ensure they're saved
                        if (Object.keys(filterValues).length > 0) {
                            const refreshedData = await DashboardFilterHandler.refreshDashboardData(filterValues);
                            await this._updateComputedFields(refreshedData);
                        }

                        this.render();
                        console.debug('Dashboard: form re-rendered after discard');
                    } catch (error) {
                        console.error('Dashboard: error handling discard', error);
                    }
                }, 100);

                return result;
            };
        }
    },

    /**
     * Clean up when controller is destroyed
     */
    async beforeUnload() {
        if (this._filterChangeTimeout) {
            clearTimeout(this._filterChangeTimeout);
        }
        return super.beforeUnload(...arguments);
    },
});

console.debug('Dashboard form controller patch applied');
