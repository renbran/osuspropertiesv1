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
                // Save the current record to persist filter values
                if (this.model.root.isDirty) {
                    await this.model.root.save();
                    console.debug('Dashboard: filter values saved');
                }

                // Force reload to get fresh computed values
                await this.model.root.load();
                console.debug('Dashboard: data reloaded with new filter values');

                // Render the updated form
                this.render();
            } catch (error) {
                console.error('Dashboard: error refreshing after filter change', error);
            }
        }, 300); // 300ms debounce
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
                console.debug('Dashboard: form discarded/reset, reloading data');

                // After discard, reload to ensure we have fresh default values
                setTimeout(async () => {
                    try {
                        await this.model.root.load();
                        this.render();
                    } catch (error) {
                        console.error('Dashboard: error reloading after discard', error);
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
