#!/usr/bin/env python3
from cgitb import html
from collections import defaultdict
import re
import datetime
import bisect
from functools import total_ordering
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from pprint import pprint
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import importlib

import html_stuff
import config



@total_ordering
class Entry:

    def __init__(self, s=None):
        self.cats = None
        self.tags = None
        self.time = None
        self.value = None
        self.note = None
        if s is None:
            return
        if s.strip() == "" or s.strip()[0] == '#':
            return
        r = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d) *(.*?) +([\(\)\d\+-\.,]+)\w*(.*)')
        date_gr, desc_gr, value_gr, note_gr = r.match(s).groups()

        if ';' not in desc_gr: desc_gr += ';'
        value_gr = value_gr.replace(',', '.')

        cats, tags = map(str.strip, desc_gr.split(';'))
        self.cats = tuple(filter(None, map(str.strip, cats.split(','))))
        self.tags = set(filter(None, map(str.strip, tags.split(','))))
        self.time = datetime.date(*map(int, date_gr.split('.')))
        self.value = eval(value_gr) if value_gr[0] == '+' else -eval(value_gr)
        self.note = note_gr.strip()

    def __str__(self):
        return "{} {};{} {:.1f}   {}".format(self.time, ','.join(self.cats), ','.join(self.tags), -self.value, self.note)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # return self.__str__() == other.__str__()
        return self.cats == other.cats and self.time == other.time and self.tags == other.tags \
               and self.value == other.value and self.note == other.note

    def __ge__(self, other):
        return self.time >= other.time


class Bookkeeper:

    def __init__(self):
        self.entries = []

    def closest_monday(self, date):
        while date.weekday() != 0:
            date -= datetime.timedelta(days=1)
        return date

    def closest_month_beginning(self, date):
        while date.day != 11:
            date -= datetime.timedelta(days=1)
        return date

    def filter(self, period=None, cats=None, tags=None, sign=None):
        result = self.entries

        if sign == "+":
            result = filter(lambda a: a.value > 0, result)
        elif sign == "-":
            result = filter(lambda a: a.value < 0, result)

        if period is not None:
            result = filter(lambda x: period[0] <= x.time <= period[1], result)

        if cats is not None:
            filtered_by_cats = list()
            for e in result:
                for c in cats:
                    if len(e.cats) >= len(c) and all([e.cats[i] == c[i] for i in range(len(c))]):
                        filtered_by_cats.append(e)
                        continue
            result = filtered_by_cats

        if tags is not None:
            result = filter(lambda x: x.tags.intersection(tags) != set(), result)

        return result


    def process(self, e):
        if e != Entry():
            bisect.insort_left(self.entries, e)

    def get_total_value(self, entries=None):
        if entries is None:
            entries = self.entries
        return sum([e.value for e in entries])

    def expenses_by_period(self, begin, end):
        return self.filter(period=(begin, end), sign="-")

    def filter_by_cats(self, cats):
        return self.filter(cats=cats)

    def every_calendar_weak(self):
        result = dict()
        start_date = self.closest_monday(min(e.time for e in self.entries))
        for dt in rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=datetime.date.today()):
            period = dt.date(), dt.date() + datetime.timedelta(days=6)
            result[period] = -sum(map(lambda x: x.value, self.filter(period=period, sign="-", cats=config.weekly_categories)))
            # begin, end = period
            # es = list(filter(lambda x: begin <= x.time < end and x.value < 0, self.filter_by_cats(config.weekly_categories)))
            # result[(begin, end)] = -sum(a.value for a in es)
        return result

    def expenses_by_top_categories(self, entries=None):
        if entries is None:
            entries = self.entries
        result = defaultdict(float)
        for x in filter(lambda x: x.value < 0, entries):
            result[x.cats[:1]] += -x.value
        return result

    def monthly_by_categories(self):
        start_date = self.closest_month_beginning(min(e.time for e in self.entries))
        result = defaultdict(list)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=datetime.date.today()):
            period = dt.date(), dt.date() + relativedelta(months=1) - relativedelta(days=1)
            result[period] = self.filter(period=period)
            # result.update({period: x for x in self.filter(period=period)})
            # es = list(filter(lambda x: begin <= x.time < end, self.entries))
            # for entry in es:
            #     result[(begin, end)].append(entry)
        result = {k: self.expenses_by_top_categories(v) for k, v in result.items()}
        return result

    def all_categories(self):
        result = set()
        for et in self.entries:
            result.add(et.cats)
        return result

    def get_last_lines(self, num_lines=7):
        return "\n".join(map(str, self.entries[-num_lines:]))


model_template = {
    "title": None,
    "total_value": None,
    "current_date": None,
    "monthly_by_categories": None
}



def make_model(bk):
    result = dict()
    result["total_value"] = bk.get_total_value()

    expenses_weekly = bk.every_calendar_weak()
    expenses_array = [[], []]
    for i, period in enumerate(sorted(expenses_weekly.keys())):
        begin = period[0].strftime("%d.%m")
        end = (period[1] - datetime.timedelta(days=1)).strftime("%d.%m")
        expenses_array[0].append({"value": "{}-{}".format(begin, end),
                                 "note": "test_note"}
        )
        expenses_array[1].append("{:.0f}".format(expenses_weekly[period]))
    result["selected_expenses_weekly"] = html_stuff.make_table(expenses_array)
    result["weekly_categories"] = ", ".join([x[0] for x in config.weekly_categories])

    expenses_by_categories = bk.expenses_by_top_categories()
    array = [[], []]
    for cat, value in sorted(expenses_by_categories.items(), key=lambda x: x[1], reverse=True):
        array[0].append(", ".join(cat))
        array[1].append("{:.0f}".format(value))
    result["expenses_by_categories"] = html_stuff.make_table(array)

    monthly_by_categories = bk.monthly_by_categories()
    all_categories = list({c for mv in monthly_by_categories.values() for c in mv})
    all_categories = sorted(all_categories,
                            key=lambda cc: sum([mm[cc] for mm in monthly_by_categories.values()]), reverse=True)
    array = [["Month", "Income", "Total spent", "Balance"] + [c[0] for c in all_categories]]
    for m in sorted(monthly_by_categories.keys()):
        mv = monthly_by_categories[m]
        month = "{} {} ({}-{})".format(m[0].strftime("%Y"), m[0].strftime("%B"), m[0].strftime("%d.%m"), m[1].strftime("%d.%m"))
        total_spent = sum(mv.values())
        income = sum([x.value for x in bk.filter(period=m, sign="+")])
        balance = income - total_spent
        row = [month, "{:.0f}".format(income), "{:.0f}".format(total_spent), "{:.0f}".format(balance)]
        for c in all_categories:
            row.append("{:.0f}".format(mv.get(c, 0)))
        array.append(row)
    result["monthly_by_categories"] = html_stuff.make_table(array)
    # result["last_lines"] = bk.get_last_lines()

    return result


class HttpTestServer(BaseHTTPRequestHandler):

    def load_data(self):
        money_txt_path = os.environ.get("MONEY_TXT_PATH", config.money_txt_path)
        with open(money_txt_path, "r") as ff:
            text = ff.read()
        start_index = text.find("\n\n\n")
        if start_index != -1: text = text[start_index:]
        bk = Bookkeeper()
        for line in text.split("\n"):
            e = Entry(line)
            bk.process(e)
        return bk

    def do_GET(self):
        importlib.reload(config)
        bk = self.load_data()
        model = make_model(bk)
        html = html_stuff.represent_html(model)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))



if __name__ == "__main__":
    the_server = HTTPServer(("", config.port), HttpTestServer)
    try:
        the_server.serve_forever()
    except KeyboardInterrupt:
        pass

    the_server.server_close()
