/** @odoo-module **/
import { registry } from '@web/core/registry';
import { loadJS } from '@web/core/assets';
import { Component, onMounted, onWillUpdateProps, onWillUnmount, useRef, useState } from '@odoo/owl';

const fieldRegistry = registry.category('fields');

let chartJsLoaded = false;

async function ensureChartLib() {
    if (chartJsLoaded && window.Chart) {
        return window.Chart;
    }
    try {
        await loadJS('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js');
        chartJsLoaded = true;
        return window.Chart;
    } catch (error) {
        console.error('Failed to load Chart.js:', error);
        try {
            await loadJS('/web/static/lib/Chart/Chart.js');
            chartJsLoaded = true;
            return window.Chart;
        } catch (fallbackError) {
            console.error('Fallback Chart.js load failed:', fallbackError);
            return null;
        }
    }
}

class DashboardChart extends Component {
    setup() {
        this.canvasRef = useRef('canvas');
        this.chart = null;
        this.noDataMessage = useRef('noDataMessage');
        this.loadingMessage = useRef('loadingMessage');
        this.state = useState({
            loading: true,
            hasData: false,
            error: null,
        });

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

        this.state.loading = true;
        this.state.error = null;

        if (!chartData || !chartData.labels || !chartData.labels.length || !chartData.datasets || !chartData.datasets.length) {
            this.state.loading = false;
            this.state.hasData = false;
            this._destroyChart();
            return;
        }

        const Chart = await ensureChartLib();
        if (!Chart) {
            this.state.loading = false;
            this.state.error = 'Chart library failed to load';
            return;
        }

        this._destroyChart();
        try {
            const ctx = this.canvasRef.el.getContext('2d');
            const config = {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 750, easing: 'easeInOutQuart' },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                usePointStyle: true,
                                font: { size: 12, family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" },
                            },
                        },
                        title: {
                            display: Boolean(title),
                            text: title,
                            font: { size: 16, weight: 'bold' },
                            padding: { top: 10, bottom: 20 },
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 4,
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) label += ': ';
                                    const v = context.parsed.y ?? context.parsed;
                                    if (v !== null && v !== undefined) {
                                        label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v);
                                    }
                                    return label;
                                },
                            },
                        },
                    },
                    scales: (chartType === 'bar' || chartType === 'line') ? {
                        x: { ticks: { autoSkip: true, maxRotation: 45, minRotation: 0, font: { size: 11 } }, grid: { display: false } },
                        y: { beginAtZero: true, ticks: { font: { size: 11 }, callback: function(value) { return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(value); } }, grid: { color: 'rgba(0, 0, 0, 0.05)' } },
                    } : {},
                },
            };
            this.chart = new Chart(ctx, config);
            this.state.loading = false;
            this.state.hasData = true;
        } catch (error) {
            console.error('Error rendering chart:', error);
            this.state.loading = false;
            this.state.error = 'Failed to render chart';
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

fieldRegistry.add('osus_dashboard_chart', {
    component: DashboardChart,
    supportedTypes: ['json'],
});
