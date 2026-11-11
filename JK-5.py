import pygal
import requests
from datetime import datetime
import re
import os
import time
import webbrowser
from dotenv import load_dotenv



while True:
    print("""Stock Data Visualizer
    ----------

    """)

    #Stock synbol
    while True:
        user_input_ss = input("Enter the stock symbol you are looking for: ")
        clean_user_input_ss = user_input_ss.strip().upper()

        #Check if length is between 1 and 10 and only contains A-Z, 0-9, ".", or "-"
        if (1 <= len(clean_user_input_ss) <= 10
                and re.fullmatch(r'[A-Z0-9.-]+', clean_user_input_ss)):
            break

        print('Invalid input. Stock symbol must be between 1 and 10 characters '
              'and only contain A-Z, 0-9, "." or "-".')
            
    #Chart type
    print("""
    Chart types:
    1. Bar
    2. Line

    """) 

    min_ct = 1
    max_ct = 2
    while True:
        try:
            #Check if input is an integer between 1-2
            user_input_ct = int(input("Enter the chart type you want (1, 2): "))
            
            if min_ct <= user_input_ct <= max_ct:
                break # Exit the loop since the input is valid
            else:
                print(f"Error: The number must be between {min_ct} and {max_ct}.")
             
        except ValueError:  # 3. Handle cases where the user types letters, symbols, or decimals
            print("Error: That is not a valid integer.")
     
    #Time series
    print("""
    Select the time series of the chaet you would like to Generate:
    ‐----------------
    1. Intraday
    2. Daily
    3. Weekly
    4. Monthly
     
    """)
          
    min_ts = 1
    max_ts = 4

    while True:
        # Check if input is an integer between 1 and 4
        try:
            user_input_ts = int(input("Enter the time series option(1, 2, 3, 4): "))
             
            if min_ts <= user_input_ts <= max_ts:
                break # Exit the loop since the input is valid
            else:
                print(f"Error: The number must be between {min_ts} and {max_ts}.")
             
        except ValueError:  # 3. Handle cases where the user types letters, symbols, or decimals
            print("Error: That is not a valid integer.")
     
     
    # Start Date
    while True:
        user_input_sd = input("Enter the start Date (YYYY-MM-DD): ")
        
        #Check format and if date is valid
        try:
            start_date = datetime.strptime(user_input_sd, "%Y-%m-%d")     
            break # Exit the loop because the format is correct and the date exists
         
        except ValueError: # 3. Handle incorrect formats (e.g., MM/DD/YYYY) or invalid dates (e.g., 2026-02-30)
            print("Error: Invalid date or format. Please use the YYYY-MM-DD format.")
     
     
    #End date
    while True:
        user_input_ed = input("Enter the end Date (YYYY-MM-DD): ")
        
        #Check format and if date is valid and not before start date
        try:
            valid_date = datetime.strptime(user_input_ed, "%Y-%m-%d")
            break # Exit the loop because the format is correct and the date exists
         
        except ValueError: print("Error: Invalid date or format. Please use the YYYY-MM-DD format.")
        
        if (user_input_ed <= user_input_sd):
            print("End date must be after Start date.")
            continue




    #Query API and display graph
    # loads the API key from the .env file
    load_dotenv()


    def get_data(symbol, function):
        """Ask Alpha Vantage for the stock data and return it as a dictionary."""
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

        # needs an interval, the other functions do not
        if function == "TIME_SERIES_INTRADAY":
            params["interval"] = "60min"

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
        except Exception:
            print("Could not get data from Alpha Vantage. Check your internet.")
            return None

        # sends errors back inside the json, so check for them
        if "Error Message" in data:
            print("Symbol not found. Check the stock symbol.")
            return None
        # the free key may not allow the full 20 years, so try again with less data
        if "Information" in data and params["outputsize"] == "full":
            params["outputsize"] = "compact"
            time.sleep(2)  # free keys only allow 1 request per second
            try:
                response = requests.get(url, params=params, timeout=15)
                data = response.json()
            except Exception:
                print("Could not get data from Alpha Vantage. Check your internet.")
                return None

        if "Note" in data or "Information" in data:
            # show what the API actually said so we know the real reason
            print("The API gave a message:")
            print(data.get("Note") or data.get("Information"))
            return None

        # the name of the data section changes depending on the function
        for key in data:
            if "Time Series" in key:
                return data[key]

        print("No time series data in the response.")
        return None


    def make_chart(symbol, data, chart_type, start, end):
        """Make the chart for the dates between start and end and open it."""
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []

        # go oldest to newest so the chart reads left to right
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
            return

        if chart_type == "bar":
            chart = pygal.Bar(x_label_rotation=45)
        else:
            chart = pygal.Line(x_label_rotation=45)

        chart.title = "Stock Data for " + symbol + ": " + str(start) + " to " + str(end)
        chart.x_labels = dates
        chart.x_labels_major_count = 10
        chart.show_minor_x_labels = False
        chart.add("Open", opens)
        chart.add("High", highs)
        chart.add("Low", lows)
        chart.add("Close", closes)

        chart.render_to_file("chart.svg")
        webbrowser.open("file://" + os.path.abspath("chart.svg"))


    def show_stock_chart(symbol, chart_type, function, start, end):
        """The teammates' input code calls this. start and end are date objects."""
        data = get_data(symbol.upper(), function)
        if data is not None:
            make_chart(symbol.upper(), data, chart_type, start, end)


    # quick test, run with: python stock_simple.py
    if __name__ == "__main__":
        show_stock_chart(
            "IBM",
            "line",
            "TIME_SERIES_DAILY",
            datetime(2026, 8, 1).date(),
            datetime(2026, 10, 15).date(),
        )


        while True:
            again = input("Search again? (y/n): ").strip().lower()
            if again in ("y", "n"):
                break
            print("Please enter y or n.")

        if again == "n":
            print("Goodbye!")
            break
        
        #Ask if user wants to continue. y = start from the begining, n= display exit message and close program
