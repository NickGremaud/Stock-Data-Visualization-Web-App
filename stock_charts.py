import pygal
import requests
from datetime import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()


def get_data(symbol, function):
    """Ask Alpha Vantage for stock data and return it as a dictionary."""
    api_key = os.environ.get("API_KEY")
    if api_key is None:
        print("No API key found. Put it in your .env file.")
        return None

    url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "full",
    }

    # Intraday needs an interval; the other functions do not.
    if function == "TIME_SERIES_INTRADAY":
        params["interval"] = "60min"

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
    except Exception:
        print("Could not get data from Alpha Vantage. Check your internet.")
        return None

    # Check for errors returned by the API.
    if "Error Message" in data:
        print("Symbol not found. Check the stock symbol.")
        return None

    # Try compact data if full data is unavailable.
    if "Information" in data and params["outputsize"] == "full":
        params["outputsize"] = "compact"
        time.sleep(2)

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
        except Exception:
            print("Could not get data from Alpha Vantage. Check your internet.")
            return None

    if "Note" in data or "Information" in data:
        print("The API gave a message:")
        print(data.get("Note") or data.get("Information"))
        return None

    # Find the time series section in the API response.
    for key in data:
        if "Time Series" in key:
            return data[key]

    print("No time series data in the response.")
    return None


def make_chart(symbol, data, chart_type, start, end):
    """Generate a stock chart and return it as an SVG string."""
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []

    # Sort dates from oldest to newest.
    for date in sorted(data.keys()):
        day = datetime.strptime(date[:10], "%Y-%m-%d").date()

        if start <= day <= end:
            dates.append(date)
            opens.append(float(data[date]["1. open"]))
            highs.append(float(data[date]["2. high"]))
            lows.append(float(data[date]["3. low"]))
            closes.append(float(data[date]["4. close"]))

    if len(dates) == 0:
        print("No data for those dates.")
        return None

    if chart_type == "bar":
        chart = pygal.Bar(x_label_rotation=45)
    else:
        chart = pygal.Line(x_label_rotation=45)

    chart.title = (
        "Stock Data for " + symbol + ": "
        + str(start) + " to " + str(end)
    )

    chart.x_labels = dates
    chart.x_labels_major_count = 10
    chart.show_minor_x_labels = False

    chart.add("Open", opens)
    chart.add("High", highs)
    chart.add("Low", lows)
    chart.add("Close", closes)

    return chart.render(is_unicode=True)


def show_stock_chart(symbol, chart_type, function, start, end):
    """Retrieve stock data and generate an SVG chart."""
    data = get_data(symbol.upper(), function)

    if data is not None:
        return make_chart(symbol.upper(), data, chart_type, start, end)

    return None