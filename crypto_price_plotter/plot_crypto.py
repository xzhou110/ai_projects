import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os
from scipy import stats

# Set matplotlib to non-interactive mode to prevent GUI popup
plt.ioff()

def get_crypto_price_data(symbol, start_date, end_date):
    # Yahoo Finance ticker format for crypto
    ticker = f"{symbol}-USD"
    
    # Download data from Yahoo Finance
    data = yf.download(ticker, start=start_date, end=end_date)
    
    # Reset index to make Date a column
    data = data.reset_index()
    
    # Include all available price data
    return data

def format_date(timestamp):
    """Helper function to format pandas timestamp"""
    if hasattr(timestamp, 'to_pydatetime'):
        return timestamp.to_pydatetime().strftime('%Y-%m-%d')
    return str(timestamp)[:10]  # Fallback to string slicing

def add_technical_indicators(df):
    """Add technical indicators to the dataframe"""
    # Calculate daily returns
    df['daily_return'] = df['Close'].pct_change() * 100
    
    # Calculate moving averages
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    
    # Calculate Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    # Avoid division by zero
    avg_loss = avg_loss.replace(0, 0.00001)
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Calculate volatility (standard deviation of returns)
    df['volatility_20d'] = df['daily_return'].rolling(window=20).std()
    
    # Calculate Bollinger Bands
    df['bollinger_mid'] = df['Close'].rolling(window=20).mean()
    df['bollinger_std'] = df['Close'].rolling(window=20).std()
    df['bollinger_upper'] = df['bollinger_mid'] + 2 * df['bollinger_std']
    df['bollinger_lower'] = df['bollinger_mid'] - 2 * df['bollinger_std']
    
    return df

def analyze_price_trend(prices, window=30):
    """Analyze the recent price trend using linear regression"""
    try:
        if len(prices) < window:
            return "Insufficient data"
        
        # Get the last 'window' days of data
        recent_prices = prices[-window:].astype(float)
        
        # Create an array of x values (0, 1, 2, ...)
        x = np.arange(len(recent_prices))
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, recent_prices)
        
        # Annualize the slope (rough estimate of annual return if trend continues)
        annual_rate = (slope * 365 / window) * (100 / recent_prices[0])
        
        # Determine trend strength and direction
        if p_value > 0.05:
            trend = "No clear trend"
        elif slope > 0:
            if r_value > 0.8:
                trend = f"Strong uptrend (projected annual return: {annual_rate:.1f}%)"
            else:
                trend = f"Moderate uptrend (projected annual return: {annual_rate:.1f}%)"
        else:
            if r_value > 0.8:
                trend = f"Strong downtrend (projected annual return: {annual_rate:.1f}%)"
            else:
                trend = f"Moderate downtrend (projected annual return: {annual_rate:.1f}%)"
        
        return trend
    except Exception as e:
        print(f"Error in trend analysis: {e}")
        return "Trend analysis unavailable"

def main():
    try:
        print("Starting comprehensive crypto price analysis...")
        
        # Time period for 2024 (from Jan 1, 2024 to current date)
        start_date = "2024-01-01"
        today_date = datetime.now().date()
        
        # For more context, get data from slightly before 2024
        extended_start = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=60)).strftime("%Y-%m-%d")
        
        print(f"Fetching data from {extended_start} to {today_date}...")
        
        # Get data for Bitcoin and Ethereum
        btc_full_data = get_crypto_price_data("BTC", extended_start, today_date.strftime("%Y-%m-%d"))
        eth_full_data = get_crypto_price_data("ETH", extended_start, today_date.strftime("%Y-%m-%d"))
        
        if btc_full_data.empty or eth_full_data.empty:
            print("Failed to fetch data.")
            return
        
        # Add technical indicators
        btc_full_data = add_technical_indicators(btc_full_data)
        eth_full_data = add_technical_indicators(eth_full_data)
        
        # Filter to just 2024 data for main analysis
        btc_data = btc_full_data[btc_full_data['Date'] >= pd.Timestamp(start_date)]
        eth_data = eth_full_data[eth_full_data['Date'] >= pd.Timestamp(start_date)]
        
        print("Generating price charts...")
        
        # Create figure and plot data - Price chart
        plt.figure(figsize=(14, 10))
        
        # Plot 1: Price with Moving Averages
        ax1 = plt.subplot(2, 1, 1)
        ax1.plot(btc_data['Date'], btc_data['Close'], 'b-', label='Bitcoin (USD)')
        ax1.plot(btc_data['Date'], btc_data['MA_20'], 'g--', label='BTC 20-day MA')
        ax1.plot(btc_data['Date'], btc_data['MA_50'], 'r--', label='BTC 50-day MA')
        ax1.set_ylabel('Bitcoin Price (USD)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.set_title('Bitcoin and Ethereum Prices in 2024 with Moving Averages')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        
        # Create a second y-axis for Ethereum
        ax2 = ax1.twinx()
        ax2.plot(eth_data['Date'], eth_data['Close'], 'r-', label='Ethereum (USD)')
        ax2.set_ylabel('Ethereum Price (USD)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        # Plot 2: Volatility Comparison
        ax3 = plt.subplot(2, 1, 2)
        ax3.plot(btc_data['Date'], btc_data['volatility_20d'], 'b-', label='BTC 20-day Volatility')
        ax3.plot(eth_data['Date'], eth_data['volatility_20d'], 'r-', label='ETH 20-day Volatility')
        ax3.set_ylabel('20-day Volatility (%)')
        ax3.set_title('Volatility Comparison')
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper left')
        
        # Format x-axis to show dates nicely
        first_date = btc_data['Date'].iloc[0].to_pydatetime().date()
        date_range = (today_date - first_date).days
        
        for ax in [ax1, ax3]:
            if date_range <= 90:  # Less than 3 months of data
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            else:
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout(pad=2.0)
        
        # Save the figure
        plt.savefig('crypto_prices_analysis_2024.png', dpi=300)
        print(f"Analysis chart saved to {os.path.abspath('crypto_prices_analysis_2024.png')}")
        
        # Create Technical Analysis Figure
        plt.figure(figsize=(14, 12))
        
        # BTC Technical Chart
        ax1 = plt.subplot(2, 1, 1)
        ax1.plot(btc_data['Date'], btc_data['Close'], 'b-', label='BTC Price')
        ax1.plot(btc_data['Date'], btc_data['bollinger_upper'], 'g--', alpha=0.6)
        ax1.plot(btc_data['Date'], btc_data['bollinger_mid'], 'g-', alpha=0.6)
        ax1.plot(btc_data['Date'], btc_data['bollinger_lower'], 'g--', alpha=0.6)
        ax1.fill_between(btc_data['Date'], btc_data['bollinger_upper'], btc_data['bollinger_lower'], color='g', alpha=0.1)
        ax1.set_ylabel('Bitcoin Price (USD)')
        ax1.set_title('Bitcoin Technical Analysis with Bollinger Bands')
        ax1.grid(True, alpha=0.3)
        
        # ETH Technical Chart
        ax2 = plt.subplot(2, 1, 2)
        ax2.plot(eth_data['Date'], eth_data['Close'], 'r-', label='ETH Price')
        ax2.plot(eth_data['Date'], eth_data['bollinger_upper'], 'g--', alpha=0.6)
        ax2.plot(eth_data['Date'], eth_data['bollinger_mid'], 'g-', alpha=0.6)
        ax2.plot(eth_data['Date'], eth_data['bollinger_lower'], 'g--', alpha=0.6)
        ax2.fill_between(eth_data['Date'], eth_data['bollinger_upper'], eth_data['bollinger_lower'], color='g', alpha=0.1)
        ax2.set_ylabel('Ethereum Price (USD)')
        ax2.set_title('Ethereum Technical Analysis with Bollinger Bands')
        ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            if date_range <= 90:
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            else:
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout(pad=2.0)
        
        # Save the technical analysis figure
        plt.savefig('crypto_technical_analysis_2024.png', dpi=300)
        print(f"Technical chart saved to {os.path.abspath('crypto_technical_analysis_2024.png')}")
        
        # Generate advanced insights
        print("\nGenerating comprehensive insights...")
        
        # Safe extraction of values
        def safe_float(series, idx):
            try:
                val = series.iloc[idx]
                return float(val) if pd.notna(val) else 0.0
            except:
                return 0.0
        
        # Basic price metrics
        btc_start = safe_float(btc_data['Close'], 0)
        btc_end = safe_float(btc_data['Close'], -1)
        btc_change_pct = ((btc_end / btc_start) - 1) * 100 if btc_start > 0 else 0
        
        eth_start = safe_float(eth_data['Close'], 0)
        eth_end = safe_float(eth_data['Close'], -1)
        eth_change_pct = ((eth_end / eth_start) - 1) * 100 if eth_start > 0 else 0
        
        # Volatility analysis
        btc_recent_volatility = safe_float(btc_data['volatility_20d'], -1)
        eth_recent_volatility = safe_float(eth_data['volatility_20d'], -1)
        volatility_ratio = btc_recent_volatility / eth_recent_volatility if eth_recent_volatility > 0 else "N/A"
        
        # Find max and min values safely
        try:
            btc_max = float(btc_data['Close'].max())
            btc_max_idx = btc_data['Close'].idxmax()
            btc_max_date = format_date(btc_data['Date'].iloc[btc_max_idx % len(btc_data)])
        except Exception as e:
            print(f"Error getting BTC max: {e}")
            btc_max = btc_end
            btc_max_date = "unknown"
        
        try:
            btc_min = float(btc_data['Close'].min())
            btc_min_idx = btc_data['Close'].idxmin()
            btc_min_date = format_date(btc_data['Date'].iloc[btc_min_idx % len(btc_data)])
        except Exception as e:
            print(f"Error getting BTC min: {e}")
            btc_min = btc_start
            btc_min_date = "unknown"
            
        try:
            eth_max = float(eth_data['Close'].max())
            eth_max_idx = eth_data['Close'].idxmax()
            eth_max_date = format_date(eth_data['Date'].iloc[eth_max_idx % len(eth_data)])
        except Exception as e:
            print(f"Error getting ETH max: {e}")
            eth_max = eth_end
            eth_max_date = "unknown"
            
        try:
            eth_min = float(eth_data['Close'].min())
            eth_min_idx = eth_data['Close'].idxmin()
            eth_min_date = format_date(eth_data['Date'].iloc[eth_min_idx % len(eth_data)])
        except Exception as e:
            print(f"Error getting ETH min: {e}")
            eth_min = eth_start
            eth_min_date = "unknown"
        
        # Trend analysis
        btc_trend = analyze_price_trend(btc_data['Close'].values)
        eth_trend = analyze_price_trend(eth_data['Close'].values)
        
        # Technical signals
        btc_ma_signal = "Bullish" if btc_end > safe_float(btc_data['MA_50'], -1) else "Bearish"
        eth_ma_signal = "Bullish" if eth_end > safe_float(eth_data['MA_50'], -1) else "Bearish"
        
        btc_rsi = safe_float(btc_data['RSI'], -1)
        eth_rsi = safe_float(eth_data['RSI'], -1)
        
        btc_rsi_signal = "Oversold (buying opportunity)" if btc_rsi < 30 else "Overbought (selling opportunity)" if btc_rsi > 70 else "Neutral"
        eth_rsi_signal = "Oversold (buying opportunity)" if eth_rsi < 30 else "Overbought (selling opportunity)" if eth_rsi > 70 else "Neutral"
        
        # Trading range analysis
        btc_trading_range = (btc_max - btc_min) / btc_min * 100 if btc_min > 0 else 0
        eth_trading_range = (eth_max - eth_min) / eth_min * 100 if eth_min > 0 else 0
        
        # Current position within range
        btc_range_position = (btc_end - btc_min) / (btc_max - btc_min) * 100 if (btc_max - btc_min) > 0 else 50
        eth_range_position = (eth_end - eth_min) / (eth_max - eth_min) * 100 if (eth_max - eth_min) > 0 else 50
        
        # Calculate correlation
        try:
            # Prepare data for correlation by aligning dates
            merged = pd.merge(btc_data, eth_data, on='Date', suffixes=('_btc', '_eth'))
            price_correlation = float(merged['Close_btc'].corr(merged['Close_eth']))
            return_correlation = float(merged['daily_return_btc'].corr(merged['daily_return_eth']))
        except Exception as e:
            price_correlation = return_correlation = "Could not calculate"
            print(f"Error calculating correlation: {e}")
        
        # Generate investment recommendations
        btc_outlook = "Positive" if btc_trend.startswith("Strong uptrend") or btc_trend.startswith("Moderate uptrend") else "Negative" if btc_trend.startswith("Strong downtrend") or btc_trend.startswith("Moderate downtrend") else "Neutral"
        eth_outlook = "Positive" if eth_trend.startswith("Strong uptrend") or eth_trend.startswith("Moderate uptrend") else "Negative" if eth_trend.startswith("Strong downtrend") or eth_trend.startswith("Moderate downtrend") else "Neutral"
        
        # Relative strength comparison
        relative_strength = btc_change_pct - eth_change_pct
        stronger_asset = "Bitcoin" if relative_strength > 0 else "Ethereum" if relative_strength < 0 else "Equal"
        
        # Create insights text
        insights = []
        insights.append("# Comprehensive Cryptocurrency Analysis for 2024")
        insights.append("\n## Price Performance")
        insights.append(f"BTC Starting Price (Jan 2024): ${btc_start:.2f}")
        insights.append(f"BTC Current Price: ${btc_end:.2f}")
        insights.append(f"BTC Price Change: {btc_change_pct:.2f}%")
        
        insights.append(f"\nETH Starting Price (Jan 2024): ${eth_start:.2f}")
        insights.append(f"ETH Current Price: ${eth_end:.2f}")
        insights.append(f"ETH Price Change: {eth_change_pct:.2f}%")
        
        insights.append(f"\nRelative Strength: {stronger_asset} has outperformed by {abs(relative_strength):.2f}%")
        
        insights.append("\n## Technical Analysis")
        insights.append(f"BTC Trend Assessment: {btc_trend}")
        insights.append(f"ETH Trend Assessment: {eth_trend}")
        
        insights.append(f"\nBTC 50-day Moving Average Signal: {btc_ma_signal}")
        insights.append(f"ETH 50-day Moving Average Signal: {eth_ma_signal}")
        
        insights.append(f"\nBTC RSI (14-day): {btc_rsi:.2f} - {btc_rsi_signal}")
        insights.append(f"ETH RSI (14-day): {eth_rsi:.2f} - {eth_rsi_signal}")
        
        insights.append("\n## Volatility Analysis")
        insights.append(f"BTC Recent Volatility (20-day): {btc_recent_volatility:.2f}%")
        insights.append(f"ETH Recent Volatility (20-day): {eth_recent_volatility:.2f}%")
        if isinstance(volatility_ratio, float):
            insights.append(f"BTC/ETH Volatility Ratio: {volatility_ratio:.2f}x")
        
        insights.append("\n## Price Range Analysis")
        insights.append(f"BTC 2024 High: ${btc_max:.2f} on {btc_max_date}")
        insights.append(f"BTC 2024 Low: ${btc_min:.2f} on {btc_min_date}")
        insights.append(f"BTC Trading Range: {btc_trading_range:.2f}%")
        insights.append(f"BTC Current Position in Range: {btc_range_position:.2f}% (0%=at low, 100%=at high)")
        
        insights.append(f"\nETH 2024 High: ${eth_max:.2f} on {eth_max_date}")
        insights.append(f"ETH 2024 Low: ${eth_min:.2f} on {eth_min_date}")
        insights.append(f"ETH Trading Range: {eth_trading_range:.2f}%")
        insights.append(f"ETH Current Position in Range: {eth_range_position:.2f}% (0%=at low, 100%=at high)")
        
        insights.append("\n## Correlation Analysis")
        if isinstance(price_correlation, float):
            insights.append(f"Price Correlation: {price_correlation:.4f} (1=perfect correlation, 0=no correlation, -1=perfect inverse)")
        if isinstance(return_correlation, float):
            insights.append(f"Daily Return Correlation: {return_correlation:.4f}")
        
        insights.append("\n## Investment Outlook")
        insights.append(f"Bitcoin Outlook: {btc_outlook}")
        insights.append(f"Ethereum Outlook: {eth_outlook}")
        
        insights.append("\n## Key Observations and Recommendations")
        
        # Add custom recommendations based on analysis
        if btc_outlook == "Positive" and eth_outlook == "Positive":
            insights.append("• Both cryptocurrencies show positive momentum; consider maintaining positions in both.")
        elif btc_outlook == "Positive" and eth_outlook != "Positive":
            insights.append("• Bitcoin shows stronger performance; consider overweighting BTC in your portfolio.")
        elif btc_outlook != "Positive" and eth_outlook == "Positive":
            insights.append("• Ethereum shows stronger performance; consider overweighting ETH in your portfolio.")
        else:
            insights.append("• Both assets show caution signals; consider reducing exposure or implementing hedging strategies.")
        
        if btc_rsi < 30 or eth_rsi < 30:
            insights.append("• Oversold conditions present potential buying opportunities.")
        elif btc_rsi > 70 or eth_rsi > 70:
            insights.append("• Overbought conditions suggest caution with new positions.")
        
        if isinstance(return_correlation, float) and return_correlation < 0.5:
            insights.append("• Lower correlation between assets suggests diversification benefits.")
        
        if btc_range_position > 80 or eth_range_position > 80:
            insights.append("• Current prices are near the high end of the trading range; consider taking partial profits.")
        elif btc_range_position < 20 or eth_range_position < 20:
            insights.append("• Current prices are near the low end of the trading range; potential value entry points.")
        
        # Print insights
        for line in insights:
            print(line)
        
        # Save insights to a file
        insights_file = 'crypto_insights_2024.txt'
        with open(insights_file, 'w') as f:
            f.write('\n'.join(insights))
        
        print(f"\nComprehensive insights saved to {os.path.abspath(insights_file)}")
        
        plt.close('all')  # Close all plots to free resources
        print("\nAnalysis complete!")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 