let chart = null;
let candleSeries = null;
let currentSymbol = 'AAPL';
let currentBenchmark = 'QQQ';
let currentTimeframe = '1d';

// Initialize chart - returns Promise
function initChart() {
    return new Promise((resolve) => {
        const chartContainer = document.getElementById('chart');
        
        // Wait for container to have size
        if (chartContainer.clientWidth === 0 || chartContainer.clientHeight === 0) {
            console.log('Chart container has no size, waiting...');
            setTimeout(() => {
                initChart().then(resolve);
            }, 200);
            return;
        }

        // If chart already exists, just resize and resolve
        if (chart) {
            chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
            resolve();
            return;
        }

        console.log('Creating chart with size:', chartContainer.clientWidth, 'x', chartContainer.clientHeight);

        chart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight,
            layout: {
                backgroundColor: '#16213e',
                textColor: '#d1d4dc',
            },
            grid: {
                vertLines: {
                    color: 'rgba(255, 255, 255, 0.1)',
                },
                horzLines: {
                    color: 'rgba(255, 255, 255, 0.1)',
                },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.2)',
                timeVisible: true,
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.2)',
                scaleType: 'log',
            },
        });

        // Use addCandlestickSeries for version 3.8.0
        candleSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        });

        console.log('Chart created successfully');

        // Handle resize
        window.addEventListener('resize', () => {
            if (chart) {
                chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
            }
        });

        resolve();
    });
}

// Fetch and render candles
async function loadCandles() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');

    // Show loading
    loading.classList.remove('hidden');
    error.classList.add('hidden');

    console.log('Loading:', currentSymbol, currentTimeframe, currentBenchmark);

    try {
        // Wait for chart to be ready
        await initChart();

        const url = `/api/candles/${currentSymbol}/${currentTimeframe}?benchmark=${currentBenchmark}`;
        console.log('Fetching:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to fetch');
        }

        const data = await response.json();
        console.log('Got candles:', data.candles ? data.candles.length : 0);

        if (!data.candles || data.candles.length === 0) {
            throw new Error('No data available');
        }

        // Format for lightweight-charts
        const candles = data.candles.map(c => ({
            time: c.time,
            open: c.open,
            high: c.high,
            low: c.low,
            close: c.close,
        }));

        console.log('First candle:', candles[0]);

        // Set data
        candleSeries.setData(candles);
        
        // Fit content
        chart.timeScale().fitContent();

        // Update UI
        document.getElementById('chartTitle').textContent = 
            `${data.symbol} vs ${data.benchmark} - ${data.timeframe}`;
        document.getElementById('lastUpdate').textContent = 
            `Last updated: ${new Date().toLocaleTimeString()}`;

        console.log('Chart updated!');

    } catch (err) {
        console.error('Error:', err);
        error.textContent = err.message;
        error.classList.remove('hidden');
    } finally {
        loading.classList.add('hidden');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded');
    
    // Wait for layout then load data
    setTimeout(() => {
        loadCandles();
    }, 500);

    // Load button
    document.getElementById('loadBtn').addEventListener('click', () => {
        const symbolInput = document.getElementById('symbol').value.trim().toUpperCase();
        if (!symbolInput) {
            alert('Please enter a stock symbol');
            return;
        }
        currentSymbol = symbolInput;
        currentBenchmark = document.getElementById('benchmark').value;
        loadCandles();
    });

    // Timeframe buttons
    document.querySelectorAll('.tf-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentTimeframe = e.target.dataset.tf;
            loadCandles();
        });
    });

    // Enter key
    document.getElementById('symbol').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('loadBtn').click();
        }
    });
});
