# 📈 Stock Index Relative Candle Viewer
# 📈 股票指数相对K线查看器

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-orange.svg)](https://flask.palletsprojects.com/)

[English](#english) | [中文](#中文)

---

## English

### Overview

A web-based tool that visualizes stock performance relative to a benchmark index (like S&P 500 or NASDAQ-100). The chart shows **excess returns** - how much better or worse a stock performs compared to the market.

### Features

- **Relative Performance Chart**: Shows stock price adjusted to remove benchmark movement
- **Multiple Timeframes**: Support for 1 Min, 15 Min, 1 Hour, 4 Hour, Daily, Weekly, Monthly
- **Benchmark Selection**: Compare against VOO, QQQ, SPY, IWM, DIA
- **Historical Data**: Fetch data from 2000 onwards for daily charts
- **Logarithmic Scale**: Optional log scale for better visualization of long-term trends
- **Real-time Data**: Uses Yahoo Finance API

### How It Works

The chart displays candles showing **excess returns** (alpha):
- 🟢 **Green candles**: Stock outperformed the benchmark
- 🔴 **Red candles**: Stock underperformed the benchmark

**Algorithm**:
1. Calculate cumulative return for both stock and benchmark from start date
2. Calculate excess return = stock return - benchmark return
3. Apply excess return to base price to generate relative OHLC data

### Installation

```bash
# Clone the repository
git clone https://github.com/Orangeforce/stock-indexrelative-candle-view.git
cd stock-candle-viewer

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Run the app
python app.py
```

Open your browser and visit: **http://localhost:5000**

### How to Use

1. Enter a stock symbol (e.g., AAPL, MSFT, TSLA)
2. Select a benchmark (default: QQQ)
3. Click "Load Chart" or press Enter
4. Use timeframe buttons to switch between different periods

### File Structure

```
stock-candle-viewer/
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
└── static/
    ├── index.html     # Main page
    ├── app.js         # Frontend JavaScript
    └── styles.css    # Styling
```

### Tech Stack

- **Backend**: Python, Flask, yfinance
- **Frontend**: HTML, CSS, JavaScript
- **Charting**: Lightweight Charts (TradingView)

---

## 中文

### 概述

一个基于网页的工具，用于可视化股票相对于基准指数（如标普500或纳斯达克100）的表现。图表显示的是**超额收益**——股票相对于市场的表现优劣。

### 功能特点

- **相对表现图表**：显示去除基准波动后的股价
- **多种时间周期**：支持1分钟、15分钟、1小时、4小时、日线、周线、月线
- **基准选择**：可对比VOO、QQQ、SPY、IWM、DIA
- **历史数据**：日线数据可追溯至2000年
- **对数坐标**：可选对数坐标，更好地显示长期趋势
- **实时数据**：使用Yahoo Finance API

### 运行原理

图表显示的是**超额收益**（Alpha）：
- 🟢 **绿色K线**：股票跑赢基准
- 🔴 **红色K线**：股票跑输基准

**算法**：
1. 计算股票和基准从起始日期到当前的累计收益率
2. 超额收益率 = 股票收益率 - 基准收益率
3. 将超额收益率应用到基准价格，生成相对OHLC数据

### 安装

```bash
# 克隆仓库
git clone https://github.com/Orangeforce/stock-indexrelative-candle-view.git
cd stock-candle-viewer

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 使用方法

```bash
# 运行应用
python app.py
```

打开浏览器访问：**http://localhost:5000**

### 使用说明

1. 输入股票代码（例如：AAPL、MSFT、TSLA）
2. 选择基准指数（默认：QQQ）
3. 点击"Load Chart"或按回车键
4. 使用时间周期按钮切换不同周期

### 文件结构

```
stock-candle-viewer/
├── app.py              # Flask后端
├── requirements.txt    # Python依赖
└── static/
    ├── index.html     # 主页面
    ├── app.js         # 前端JavaScript
    └── styles.css    # 样式文件
```

### 技术栈

- **后端**：Python、Flask、yfinance
- **前端**：HTML、CSS、JavaScript
- **图表库**：Lightweight Charts (TradingView)

---

## License 许可证

MIT License - feel free to use this project for any purpose.

MIT许可证 - 欢迎将此项目用于任何目的。
