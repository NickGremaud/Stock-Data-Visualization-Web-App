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

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()

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

        except (ValueError, TypeError):
            error = "Invalid date. Please select valid start and end dates."

    return render_template(
        "index.html",
        stock_symbols=stock_symbols,
        chart=chart,
        error=error
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)