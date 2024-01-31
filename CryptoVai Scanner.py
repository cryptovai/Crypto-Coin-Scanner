import requests
import numpy as np
from colorama import Fore, Style
import time

def get_coin_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch coin data.")
        return None

def calculate_ema(data, window):
    prices = [float(coin['current_price']) for coin in data]
    weights = [np.exp(-i) for i in range(window)]
    weights /= np.sum(weights)
    ema = np.convolve(prices, weights, mode='valid')
    return ema

def calculate_rsi(data, window):
    prices = [float(coin['current_price']) for coin in data]
    deltas = np.diff(prices)
    seed = deltas[:window + 1]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:window] = 100. - 100. / (1. + rs)

    for i in range(window, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (window - 1) + upval) / window
        down = (down * (window - 1) + downval) / window
        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi

def print_coin_data(data, ema9, ema20, rsi, direction):
    min_length = min(len(ema9), len(ema20), len(rsi), len(data))
    coins_found = False
    for i in range(min_length):
        coin = data[i]
        name = coin['name']
        symbol = coin['symbol'].upper()
        market_price = coin['current_price']
        volume = coin['total_volume']
        volume_suffix = "M"
        if volume >= 1000000000:
            volume_suffix = "B"
            volume /= 1000000000
        elif volume >= 1000000:
            volume_suffix = "M"
            volume /= 1000000
        volume_display = f"{volume:.2f}{volume_suffix}"
        ema9_val = ema9[i]
        ema20_val = ema20[i]
        rsi_val = rsi[i]

        if direction == "up" and ema9_val >= market_price and rsi_val >= 60:
            print(f"{Fore.GREEN}{i+1}. {name} ({symbol}) - Market Price: {Fore.LIGHTMAGENTA_EX}{market_price}")
            print(f"Volume: {Fore.CYAN}{volume_display}")
            print("****************************")
            time.sleep(1)
            coins_found = True
        elif direction == "down" and (ema9_val <= market_price or ema20_val <= market_price) and rsi_val <= 40:
            print(f"{Fore.GREEN}{i+1}. {name} ({symbol}) - Market Price: {Fore.LIGHTMAGENTA_EX}{market_price}")
            print(f"Volume: {Fore.CYAN}{volume_display}")
            print("****************************")
            time.sleep(1)
            coins_found = True

    if not coins_found:
        print(f"No coins found for {direction} direction with the specified conditions.")

def main():
    while True:
        coin_data = get_coin_data()
        if coin_data:
            ema9 = calculate_ema(coin_data, 9)
            ema20 = calculate_ema(coin_data, 20)
            rsi = calculate_rsi(coin_data, 14)

            direction = input(
                f"{Fore.YELLOW}{Style.BRIGHT}This coins list depends on EMA 9, EMA 20, and RSI Condition\n"
                f"For bullish coins list, type 'up'....:\n"
                f"For bearish coins list, type 'down'.....:\n"
                f"To stop the program, type 'stop'....:{Style.RESET_ALL}"
            ).lower()

            if direction == "stop":
                print("Stopping the program.")
                break

            if direction in ["up", "down"]:
                print_coin_data(coin_data, ema9, ema20, rsi, direction)
            else:
                print("Invalid direction. Please enter 'up' or 'down'.")

if __name__ == "__main__":
    main()

