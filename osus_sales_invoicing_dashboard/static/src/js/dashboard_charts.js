/** @odoo-module **/
/**
 * Smart dashboard charts: renders JSON datasets from fields into Chart.js.
 */
import { registry } from '@web/core/registry';
import { loadJS } from '@web/core/assets';
import { Component, onMounted, onWillUpdateProps, onWillUnmount, useRef } from '@odoo/owl';

const fieldRegistry = registry.category('fields');

async function ensureChartLib() {
    if (window.Chart) {
        return window.Chart;
    }
    try {
        await loadJS('/web/static/lib/Chart/Chart.js');
        return window.Chart;
    } catch (error) {
        console.error('Failed to load Chart.js:', error);
        return null;
    }
}

class DashboardChart extends Component {
    setup() {
        this.canvasRef = useRef('canvas');
        this.chart = null;
        this.noDataMessage = useRef('noDataMessage');
        onMounted(() => this._renderChart());
        onWillUpdateProps((nextProps) => this._renderChart(nextProps));
        onWillUnmount(() => this._destroyChart());
    }

    async _renderChart(nextProps) {
        const props = nextProps || this.props;
        const chartData = props.value;
        const opts = props.options || {};
        const chartType = opts.chartType || 'bar';
        const title = opts.title || '';

        // Hide no-data message and canvas
        if (this.noDataMessage.el) {
            this.noDataMessage.el.style.display = 'none';
        }
        if (this.canvasRef.el) {
            this.canvasRef.el.style.display = 'block';
        }

        if (!chartData || !chartData.labels || !chartData.labels.length) {
            this._destroyChart();
            // Show no-data message
            if (this.noDataMessage.el) {
                this.noDataMessage.el.style.display = 'flex';
            }
            if (this.canvasRef.el) {
                this.canvasRef.el.style.display = 'none';
            }
            return;
        }

        const Chart = await ensureChartLib();
        if (!Chart) {
            console.error('Chart.js library not available');
            return;
        }

        this._destroyChart();
        
        try {
            const ctx = this.canvasRef.el.getContext('2d');
            this.chart = new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, position: 'bottom' },
                        title: { display: Boolean(title), text: title },
                    },
                    scales: chartType === 'bar' || chartType === 'line' ? {
                        x: { ticks: { autoSkip: true, maxRotation: 45 } },
                        y: { beginAtZero: true },
                    } : {},
                },
            });
        } catch (error) {
            console.error('Error rendering chart:', error);
        }
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

DashboardChart.template = 'osus_sales_invoicing_dashboard.DashboardChart';

fieldRegistry.add('osus_dashboard_chart', DashboardChart);
