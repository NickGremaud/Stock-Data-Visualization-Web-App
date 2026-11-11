import csv
from pathlib import Path
from flask import Flask, render_template, request
from stock_charts import show_stock_chart
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    chart = None
    error = None
    stock_symbols = []

    csv_path = Path(__file__).resolve().parent / "stocks.csv"

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            stock_symbols.append(row["Symbol"])

    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")
        time_series = request.form.get("time_series")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        valid_chart_types = ["bar", "line"]
        valid_time_series = [
            "TIME_SERIES_INTRADAY",
            "TIME_SERIES_DAILY",
            "TIME_SERIES_WEEKLY",
            "TIME_SERIES_MONTHLY"
        ]

        if not symbol or symbol not in stock_symbols:
            error = "Please select a valid stock symbol."

        elif chart_type not in valid_chart_types:
            error = "Please select a valid chart type."

        elif time_series not in valid_time_series:
            error = "Please select a valid time series."

        elif not start_date:
            error = "Please select a start date."

        elif not end_date:
            error = "Please select an end date."

        else:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                error = "Invalid start date. Please select a valid date."

            if error is None:
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d").date()
                except ValueError:
                    error = "Invalid end date. Please select a valid date."

            if error is None:
                if end <= start:
                    error = "End date must be after start date."
                else:
                    chart = show_stock_chart(
                        symbol,
                        chart_type,
                        time_series,
                        start,
                        end
                    )

                    if chart is None:
                        error = "Unable to generate chart. Check the stock data or date range."

    return render_template(
        "index.html",
        stock_symbols=stock_symbols,
        chart=chart,
        error=error
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)