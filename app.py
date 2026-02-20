from flask import Flask, jsonify, request, send_from_directory
import yfinance as yf
import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Timeframe configuration - use start/end dates for more data
TIMEFRAME_CONFIG = {
    '1m': {'interval': '1m', 'start': '2024-01-01', 'end': '2025-12-31', 'agg': 1},
    '15m': {'interval': '15m', 'start': '2024-01-01', 'end': '2025-12-31', 'agg': 1},
    '1h': {'interval': '1h', 'start': '2020-01-01', 'end': '2025-12-31', 'agg': 1},
    '4h': {'interval': '1h', 'start': '2020-01-01', 'end': '2025-12-31', 'agg': 4},
    '1d': {'interval': '1d', 'start': '2000-01-01', 'end': '2025-12-31', 'agg': 1},
    '1w': {'interval': '1wk', 'start': '1990-01-01', 'end': '2025-12-31', 'agg': 1},
    '1mo': {'interval': '1mo', 'start': '1990-01-01', 'end': '2025-12-31', 'agg': 1},
}


def fetch_stock_data(symbol, interval, start, end):
    """Fetch stock data from Yahoo Finance using start/end dates"""
    try:
        logger.info(f"Fetching {symbol} from {start} to {end}")
        ticker = yf.Ticker(symbol)
        df = ticker.history(interval=interval, start=start, end=end)
        if df.empty:
            logger.warning(f"No data returned for {symbol}")
            return None
        logger.info(f"Got {len(df)} rows for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None


def aggregate_candles(df, agg_factor):
    """Aggregate multiple candles into one"""
    if agg_factor == 1:
        return df

    aggregated = []
    for i in range(0, len(df), agg_factor):
        chunk = df.iloc[i:i+agg_factor]
        if len(chunk) > 0:
            agg = {
                'Open': chunk['Open'].iloc[0],
                'High': chunk['High'].max(),
                'Low': chunk['Low'].min(),
                'Close': chunk['Close'].iloc[-1],
            }
            aggregated.append(agg)

    result_df = pd.DataFrame(aggregated, index=df.index[::agg_factor][:len(aggregated)])
    return result_df


def calculate_relative_candles(stock_df, benchmark_df):
    """
    Calculate relative OHLC showing excess return over benchmark.
    
    Algorithm:
    1. Calculate cumulative return for both using Close prices
    2. Calculate excess return = stock_cumulative - benchmark_cumulative
    3. Apply excess return to base price to get relative prices
    """
    if stock_df is None or benchmark_df is None:
        logger.warning("stock_df or benchmark_df is None")
        return None

    # Align timestamps using merge
    combined = pd.merge(
        stock_df[['Open', 'High', 'Low', 'Close']], 
        benchmark_df[['Open', 'High', 'Low', 'Close']], 
        left_index=True, 
        right_index=True,
        suffixes=('_stock', '_bm')
    )
    
    logger.info(f"After merge: {len(combined)} rows")
    
    # Drop rows with any NaN values
    combined = combined.dropna()
    logger.info(f"After dropna: {len(combined)} rows")
    
    if combined.empty:
        logger.warning("Combined dataframe is empty after processing")
        return None

    # Get base prices (first row) - use Close for calculations
    base_stock_close = combined['Close_stock'].iloc[0]
    base_bm_close = combined['Close_bm'].iloc[0]
    
    logger.info(f"Base stock close: {base_stock_close}, Base benchmark close: {base_bm_close}")
    
    relative_candles = []

    for i in range(len(combined)):
        row = combined.iloc[i]
        
        # Current stock prices
        stock_open = row['Open_stock']
        stock_close = row['Close_stock']
        stock_high = row['High_stock']
        stock_low = row['Low_stock']
        
        # Current benchmark prices
        bm_open = row['Open_bm']
        bm_close = row['Close_bm']
        bm_high = row['High_bm']
        bm_low = row['Low_bm']
        
        # Calculate stock's cumulative return since start (using Close)
        if base_stock_close != 0:
            stock_cumulative_return = (stock_close - base_stock_close) / base_stock_close
        else:
            stock_cumulative_return = 0
        
        # Calculate benchmark's cumulative return since start (using Close)
        if base_bm_close != 0:
            bm_cumulative_return = (bm_close - base_bm_close) / base_bm_close
        else:
            bm_cumulative_return = 0
        
        # Excess return = stock return - benchmark return
        excess_return = stock_cumulative_return - bm_cumulative_return
        
        # Calculate relative OHLC
        # Relative price = what the stock price would be if benchmark didn't change
        # This shows the pure alpha (excess return)
        
        # For each price, calculate what it would be with only excess return
        rel_close = base_stock_close * (1 + excess_return)
        
        # For Open, High, Low - estimate using proportion of close change
        # If stock moved X% and benchmark moved Y%, relative = X% - Y%
        if stock_close != 0:
            stock_open_ratio = stock_open / stock_close
            stock_high_ratio = stock_high / stock_close
            stock_low_ratio = stock_low / stock_close
        else:
            stock_open_ratio = 1
            stock_high_ratio = 1
            stock_low_ratio = 1
        
        if bm_close != 0:
            bm_open_ratio = bm_open / bm_close
            bm_high_ratio = bm_high / bm_close
            bm_low_ratio = bm_low / bm_close
        else:
            bm_open_ratio = 1
            bm_high_ratio = 1
            bm_low_ratio = 1
        
        # Calculate relative ratios
        rel_open = base_stock_close * (1 + excess_return * stock_open_ratio)
        rel_high = base_stock_close * (1 + excess_return * stock_high_ratio)
        rel_low = base_stock_close * (1 + excess_return * stock_low_ratio)

        # Get timestamp
        timestamp = int(combined.index[i].timestamp())

        relative_candles.append({
            'time': timestamp,
            'open': round(rel_open, 2),
            'high': round(rel_high, 2),
            'low': round(rel_low, 2),
            'close': round(rel_close, 2),
        })

    logger.info(f"Generated {len(relative_candles)} relative candles")
    return relative_candles


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/api/candles/<symbol>/<timeframe>')
def get_candles(symbol, timeframe):
    """Get candle data for a symbol with relative movement"""
    logger.info(f"Request: {symbol} {timeframe}")
    
    # Get benchmark from query params
    benchmark = request.args.get('benchmark', 'QQQ').upper()

    if timeframe not in TIMEFRAME_CONFIG:
        return jsonify({'error': 'Invalid timeframe'}), 400

    config = TIMEFRAME_CONFIG[timeframe]

    # Fetch stock data
    stock_df = fetch_stock_data(symbol, config['interval'], config['start'], config['end'])
    if stock_df is None or stock_df.empty:
        return jsonify({'error': f'Could not fetch data for {symbol}'}), 400

    # Fetch benchmark data
    benchmark_df = fetch_stock_data(benchmark, config['interval'], config['start'], config['end'])
    if benchmark_df is None or benchmark_df.empty:
        return jsonify({'error': f'Could not fetch data for {benchmark}'}), 400

    # Aggregate candles if needed
    stock_df = aggregate_candles(stock_df, config['agg'])
    benchmark_df = aggregate_candles(benchmark_df, config['agg'])

    # Calculate relative candles
    relative_candles = calculate_relative_candles(stock_df, benchmark_df)
    
    if relative_candles is None or len(relative_candles) == 0:
        return jsonify({'error': 'Failed to calculate relative candles - possibly no overlapping data'}), 400

    return jsonify({
        'symbol': symbol,
        'benchmark': benchmark,
        'timeframe': timeframe,
        'candles': relative_candles
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
