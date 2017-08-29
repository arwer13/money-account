#!/usr/bin/env python3
import os
import datetime

import flask

import money


app = flask.Flask(__name__)


BY_CATEGORIES_TEMPLATE = """<html>
<body>
    <h1>Income</h1>
    Total income: {total_income}
    {income}
    <h1>Expenses</h1>
    Total: {total_expenses}
    {expenses}
</body>
</html>
"""

DATE_FORMAT = "%Y-%m-%d"


@app.route("/")
def route_index():
    args = flask.request.args
    print(args)
    today_str = datetime.date.today().strftime(DATE_FORMAT)

    def str_to_date(s):
        return datetime.datetime.strptime(s, DATE_FORMAT).date()

    first_day = str_to_date(args.get("first_day", today_str))
    last_day = str_to_date(args.get("last_day", today_str))

    df = money.load_df()
    for_period = money.for_period(df, first_day, last_day)
    if len(for_period) == 0:
        return "No records for this period."
    by_cat1 = money.by_cat1(for_period)

    result = by_cat1[["value"]]
    result.value = result.value.astype(int)

    # Income.
    income = result[result.value > 0.0]
    total_income = income.value.sum()

    # Expenses.
    expenses = result[result.value <= 0.0]
    expenses.value = -expenses.value
    total_expenses = expenses.value.sum()

    return BY_CATEGORIES_TEMPLATE.format(**{
        "income": income.to_html(),
        "expenses": expenses.to_html(),
        "total_income": total_income,
        "total_expenses": total_expenses,
    })


@app.route("/value")
def route_value():
    df = money.load_df()
    value = money.get_total(df)
    return "{:.0f}".format(value)


if __name__ == "__main__":
    app.run()
