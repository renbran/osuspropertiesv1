/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import DashboardFilterHandler from './dashboard_filters';

/**
 * Dashboard Form Controller
 *
 * Extends the standard Odoo form controller to add automatic filter
 * change listeners for the Sales & Invoicing Dashboard.
 *
 * This controller:
 * 1. Waits for the form to be fully rendered
 * 2. Initializes filter change listeners on fields with class 'o_dashboard_filter'
 * 3. Provides helper functions to get/set form values
 * 4. Ensures filters are persisted and data refreshed on every change
 */

patch(FormController.prototype, {
    /**
     * Called after the form view is set up
     * This is where we initialize our custom filter listeners
     */
    setup() {
        super.setup(...arguments);

        // Only initialize for the dashboard model
        if (this.props.resModel === 'osus.sales.invoicing.dashboard') {
            console.debug('Dashboard: FormController setup for dashboard model');

            // Use onMounted to ensure DOM is ready
            const { onMounted } = owl;
            onMounted(() => {
                console.debug('Dashboard: FormController mounted, initializing filters');
                this._initializeDashboardFilters();
            });
        }
    },

    /**
     * Initialize the dashboard filter listeners
     */
    _initializeDashboardFilters() {
        try {
            const formElement = this.rootRef?.el;

            if (!formElement) {
                console.warn('Dashboard: form element not found in rootRef');
                return;
            }

            console.debug('Dashboard: form element found, setting up filter listeners');

            // Initialize filter listeners with helper functions
            DashboardFilterHandler.initializeFilterListeners({
                formElement: formElement,
                getFormValues: () => this._getDashboardFilterValues(),
                updateFormFields: (data) => this._updateDashboardFields(data),
            });

            console.info('Dashboard: filter listeners initialized successfully');
        } catch (error) {
            console.error('Dashboard: failed to initialize filter listeners', error);
        }
    },

    /**
     * Extract current filter values from the form
     * @returns {Object} Dictionary of filter field names and their current values
     */
    _getDashboardFilterValues() {
        const model = this.model;
        const record = model.root;

        if (!record) {
            console.warn('Dashboard: no record found in model');
            return {};
        }

        // Extract all filter field values
        const filterValues = {
            sales_order_type_ids: record.data.sales_order_type_ids?.records?.map(r => r.resId) || [],
            booking_date_from: record.data.booking_date_from || false,
            booking_date_to: record.data.booking_date_to || false,
            invoice_status_filter: record.data.invoice_status_filter || 'all',
            payment_status_filter: record.data.payment_status_filter || 'all',
            agent_partner_id: record.data.agent_partner_id?.[0] || false,
            partner_id: record.data.partner_id?.[0] || false,
        };

        console.debug('Dashboard: extracted filter values', filterValues);
        return filterValues;
    },

    /**
     * Update form fields with new computed data from backend
     * @param {Object} data - Dictionary of field names and their new values
     */
    _updateDashboardFields(data) {
        const model = this.model;
        const record = model.root;

        if (!record) {
            console.warn('Dashboard: no record found in model for update');
            return;
        }

        try {
            // Update each field in the record data
            for (const [fieldName, fieldValue] of Object.entries(data)) {
                if (fieldName in record.data) {
                    record.data[fieldName] = fieldValue;
                    console.debug(`Dashboard: updated field ${fieldName}`);
                }
            }

            // Force the view to re-render with updated values
            model.notify();
            console.debug('Dashboard: fields updated and view notified');
        } catch (error) {
            console.error('Dashboard: error updating fields', error);
        }
    },
});

console.info('Dashboard: FormController patch registered');
