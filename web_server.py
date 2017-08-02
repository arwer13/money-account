#!/usr/bin/env python3
import os
import datetime

import flask

import money


app = flask.Flask(__name__)


DEFAULT_MONEY_TXT_PATH = os.path.join(os.path.expanduser("~"),
                                      "Dropbox/Apps/money.txt-dev/money.txt")
MONEY_TXT_PATH_ENV = "MONEY_TXT_PATH"
DROPBOX_TOKEN_ENV = "MONEY_TXT_DROPBOX_TOKEN"


@app.route("/")
def route_index():
    args = flask.request.args
    begin = args.get("begin")
    begin = datetime.date.today() \
        if begin is None \
        else datetime.datetime.strptime(begin, "%Y-%m-%d").date()
    end = args.get("end")
    end = datetime.date.today() \
        if end is None \
        else datetime.datetime.strptime(end, "%Y-%m-%d").date()

    df = money.load_df()
    for_period = df[df.value < 0.0][df.date >= begin][df.date <= end]\
        .groupby(by="cat1").sum().sort_values("value")
    return for_period.to_html()


@app.route("/value")
def route_value():
    df = money.load_df()
    value = money.get_total(df)
    return "{:.0f}".format(value)


if __name__ == "__main__":
    app.run()
    # df = load_df()
    # pass
    # whole_period = df.at[0, 'date'], df.at[len(df)-1, 'date']
    # periods = split_monthly(whole_period, 1)
    # print(df)
