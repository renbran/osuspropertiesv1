/** @odoo-module **/

import { rpc } from '@web/core/network/rpc';

/**
 * Dashboard Filter Handler
 * 
 * Manages filter changes and automatic form saving for the Sales & Invoicing Dashboard
 * 
 * Key Features:
 * 1. Listens to filter field changes
 * 2. Automatically saves the form record to database
 * 3. Fetches updated computed field values
 * 4. Updates form display with fresh data
 * 
 * This ensures that when users change filters, the dashboard data updates
 * in real-time by persisting changes and recalculating metrics.
 */

// Define which fields are filters that trigger auto-save
const FILTER_FIELDS = [
    'sales_order_type_id',
    'sales_order_type_ids',
    'booking_date_from',
    'booking_date_to',
    'invoice_status_filter',
    'payment_status_filter',
    'agent_partner_id',
    'partner_id',
];

// Define which fields are computed and should be refreshed
const COMPUTED_FIELDS = [
    'posted_invoice_count',
    'pending_to_invoice_order_count',
    'unpaid_invoice_count',
    'total_booked_sales',
    'total_invoiced_amount',
    'total_pending_amount',
    'amount_to_collect',
    'amount_collected',
    'commission_due',
    'chart_sales_by_type',
    'chart_booking_trend',
    'chart_payment_state',
    'chart_sales_funnel',
    'chart_top_customers',
    'chart_agent_performance',
    'table_order_type_html',
    'table_agent_commission_html',
    'table_detailed_orders_html',
    'table_invoice_aging_html',
];

const DashboardFilterHandler = {
    /**
     * Refresh dashboard data by calling the server API
     * 
     * @param {Object} filterValues - Dictionary of filter field names and their values
     * @returns {Promise<Object>} Updated computed field values
     */
    async refreshDashboardData(filterValues) {
        try {
            const result = await rpc({
                model: 'osus.sales.invoicing.dashboard',
                method: 'update_filters_and_refresh',
                args: [filterValues],
            });
            return result;
        } catch (error) {
            console.error('Dashboard filter refresh error:', error);
            throw error;
        }
    },

    /**
     * Initialize filter change listeners on a form
     * Should be called after form loads
     * 
     * @param {Object} params - Initialization parameters
     * @param {Element} params.formElement - The form DOM element
     * @param {Function} params.getFormValues - Function to get all field values
     * @param {Function} params.updateFormFields - Function to update form fields with values
     */
    initializeFilterListeners(params) {
        const { formElement, getFormValues, updateFormFields } = params;
        
        if (!formElement) {
            console.warn('Dashboard: form element not found');
            return;
        }

        let saveTimeout = null;

        // Find all filter fields in the form
        const filterElements = formElement.querySelectorAll('.o_dashboard_filter');
        
        if (filterElements.length === 0) {
            console.warn('Dashboard: no filter fields found with class o_dashboard_filter');
            return;
        }

        console.debug(`Dashboard: found ${filterElements.length} filter fields`);

        // Attach change listener to each filter field
        filterElements.forEach((element) => {
            element.addEventListener('change', async () => {
                console.debug('Dashboard: filter field changed, preparing to save', element);
                
                // Clear any pending save
                if (saveTimeout) clearTimeout(saveTimeout);

                // Debounce save operation by 500ms to batch rapid changes
                saveTimeout = setTimeout(async () => {
                    try {
                        // Get current form values
                        const filterValues = getFormValues();
                        console.debug('Dashboard: filter values to save', filterValues);

                        // Save to database and get refreshed values
                        const refreshedData = await DashboardFilterHandler.refreshDashboardData(filterValues);
                        console.debug('Dashboard: refreshed data received', refreshedData);

                        // Update form fields with new values
                        if (updateFormFields && typeof updateFormFields === 'function') {
                            updateFormFields(refreshedData);
                            console.debug('Dashboard: form fields updated with refreshed data');
                        }

                    } catch (error) {
                        console.error('Dashboard: failed to refresh data after filter change', error);
                        // Don't throw - allow user to continue using form even if refresh fails
                    }
                }, 500);
            });
        });

        console.debug('Dashboard: filter listeners initialized');
    },
};

export default DashboardFilterHandler;
export { FILTER_FIELDS, COMPUTED_FIELDS };


