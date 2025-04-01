# Crypto Price Plotter & Analyzer

A comprehensive Python tool for analyzing Bitcoin (BTC) and Ethereum (ETH) prices, with advanced technical indicators and investment insights.

## Features

- Fetches detailed price data for Bitcoin and Ethereum using Yahoo Finance API
- Provides comprehensive technical analysis including:
  - Moving averages (20-day and 50-day)
  - RSI (Relative Strength Index)
  - Volatility metrics
  - Bollinger Bands
  - Price correlation analysis
  - Trend analysis with linear regression
- Generates multiple visualization charts:
  - Price charts with moving averages
  - Volatility comparison
  - Technical analysis with Bollinger Bands
- Produces detailed investment insights with recommendations

## Requirements

- Python 3.6+
- Required packages: pandas, matplotlib, yfinance, numpy, scipy

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line:
```
python plot_crypto.py
```

The script will:
1. Fetch BTC and ETH price data from January 1, 2024 to the current date
2. Generate analysis charts with technical indicators
3. Save multiple visualization files:
   - `crypto_prices_analysis_2024.png`: Price and volatility analysis
   - `crypto_technical_analysis_2024.png`: Technical analysis with Bollinger Bands
4. Create a comprehensive analysis report in `crypto_insights_2024.txt`

## Analysis Output

The script generates multiple insights to aid in decision making:
- Price performance metrics and relative strength
- Technical trend assessment with projected returns
- Volatility and correlation analysis
- Price range analysis with current position in range
- Investment outlook with specific recommendations based on indicators

## Notes

- The script uses Yahoo Finance API which is more reliable for cryptocurrency data
- All analysis is for informational purposes only and should not be considered financial advice 