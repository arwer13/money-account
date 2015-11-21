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
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt

import html_stuff
import config


@total_ordering
class Entry:

    def __init__(self, s=None, date=None):
        self.cats = []
        self.tags = set()
        self.day = None
        self.value = 0
        self.note = ""
        self.cmd = None
        if s is None:
            return
        if s.strip() == "":
            return
        elif s.strip()[0] == '#':
            return
        cmd_re = re.compile(r'\s*(\d\d\d\d\.\d\d\.\d\d)?\s+!(.*?) +([\(\)\d\+-\.\*,]+)\s*')
        entry_re = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d)? *(.*?) +([\(\)\d\+-\.,\*]+)\w*(.*)')

        cmd_match = cmd_re.match(s)
        if cmd_match is not None:
            print(cmd_match.groups())
            date_str, self.cmd, value_str = cmd_match.groups()
            self.day = datetime.date(*map(int, date_str.split('.')))
            self.value = eval(value_str)
        else:
            try:
                date_gr, desc_gr, value_gr, note_gr = entry_re.match(s).groups()
            except AttributeError as e:
                msg = str(e)
                print("Error line: {} ({})".format(s, e))
                return

            if ';' not in desc_gr: desc_gr += ';'
            value_gr = value_gr.replace(',', '.')

            cats, tags = map(str.strip, desc_gr.split(';'))
            self.cats = tuple(filter(None, map(str.strip, cats.split(','))))
            self.tags = set(filter(None, map(str.strip, tags.split(','))))
            self.day = date if date_gr is None else datetime.date(*map(int, date_gr.split('.')))
            self.value = eval(value_gr) if value_gr[0] == '+' else -eval(value_gr)
            self.note = note_gr.strip()

    def __str__(self):
        if self.cmd is None:
            value_str = "{:.1f}".format(-self.value) if self.value < 0 else "+{:.0f}".format(self.value)
            return "{} {};{} {} {}".format(self.day, ','.join(self.cats), ','.join(self.tags), value_str,
                                           '' if self.note is None else self.note)
        else:
            return "{} !{} {:.1f}".format(self.day, self.cmd, self.value)

    def __repr__(self):
        return '\n'+str(self.__dict__)

    def __eq__(self, other):
        return self.cats == other.cats and self.day == other.day and self.tags == other.tags \
               and self.value == other.value and self.note == other.note

    def __gt__(self, other):
        return self.day > other.day


class Bookkeeper:

    def __init__(self):
        self.entries = []
        self.last_day = None

    def closest_monday(self, date):
        date -= datetime.timedelta(days=date.weekday())
        return date

    # scary way to step back to known date
    def closest_month_beginning(self, date):
        while date.day != config.month_period_day:
            date -= datetime.timedelta(days=1)
        return date

    def filter(self, period=None, cats=None, tags=None, sign=None, cmds=(None,)):
        result = self.entries
        result = list(filter(lambda x: x.cmd in cmds, result))

        if sign == "+":
            result = filter(lambda a: a.value > 0, result)
        elif sign == "-":
            result = filter(lambda a: a.value < 0, result)

        if period is not None:
            pr = [None, None]
            pr[0] = period[0] if period[0] is not None else self.entries[0].day
            pr[1] = period[1] if period[1] is not None else datetime.date.today()
            result = filter(lambda x: pr[0] <= x.day <= pr[1], result)

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

    def account(self, line):
        if line == "":
            return
        e = Entry(line, self.last_day)
        self.last_day = e.day
        if e != Entry():
            if len(self.entries) > 0 and self.entries[-1].day >= e.day:
                self.entries.append(e)
            else:
                bisect.insort_right(self.entries, e)

    def get_total_value(self):
        # milestone = self.milestones[-1]
        # return milestone[2] + sum([e.value for e in self.filter(period=(milestone[0], datetime.date.today()))])
        result = 0.0
        for e in self.entries:
            if e.cmd == "milestone":
                result = e.value
            else:
                result += e.value
        return result

    def every_calendar_weak(self):
        result = dict()
        start_date = self.closest_monday(min(e.day for e in self.entries))
        for dt in rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=datetime.date.today()):
            period = dt.date(), dt.date() + datetime.timedelta(days=6)
            week_expenses = self.filter(period=period, sign="-", cats=config.weekly_categories)
            week_expenses = list(week_expenses)
            notes = [str(x) for x in week_expenses]
            value = -sum(map(lambda x: x.value, week_expenses))
            result[period] = {"value": value, "note": notes}
        return result

    def expenses_by_top_categories(self, entries=None):
        if entries is None:
            entries = self.entries
        result = defaultdict(lambda : {"value": 0.0, "note": []})
        for x in filter(lambda x: x.value < 0, entries):
            cat = x.cats[:1]
            result[cat]["value"] += -x.value
            result[cat]["note"].append(str(x))
        return result

    def monthly_by_categories(self):
        start_date = self.closest_month_beginning(min(e.day for e in self.entries))
        result = defaultdict(list)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=datetime.date.today()):
            period = dt.date(), dt.date() + relativedelta(months=1) - relativedelta(days=1)
            result[period] = self.filter(period=period)
        result = {k: self.expenses_by_top_categories(v) for k, v in result.items()}
        return result

    def all_categories(self):
        result = set()
        for et in self.entries:
            result.add(et.cats)
        return result


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
        end = period[1].strftime("%d.%m")
        # end = (period[1] - datetime.timedelta(days=1)).strftime("%d.%m")
        expenses_array[0].append("{}-{}".format(begin, end))
        expenses_array[1].append(expenses_weekly[period])
    result["selected_expenses_weekly"] = expenses_array
    result["weekly_categories"] = ", ".join([x[0] for x in config.weekly_categories])

    monthly_by_categories = bk.monthly_by_categories()
    all_categories = list({c for mv in monthly_by_categories.values() for c in mv})
    all_categories = sorted(all_categories,
                            key=lambda cc: sum([mm[cc]["value"] for mm in monthly_by_categories.values()]), reverse=True)
    array = [["Month", "Income", "Total spent", "Balance"] + [c[0] for c in all_categories]]
    for m in sorted(monthly_by_categories.keys()):
        mv = monthly_by_categories[m]
        month = "{} {} ({}-{})".format(m[0].strftime("%Y"), m[0].strftime("%B"), m[0].strftime("%d.%m"), m[1].strftime("%d.%m"))
        total_spent = sum([x["value"] for x in mv.values()])
        income = {"value": 0, "note": []}
        for x in bk.filter(period=m, sign="+"):
            income["value"] += x.value
            income["note"].append(str(x))
        balance = income["value"] - total_spent
        row = [month, income, total_spent, balance]
        for c in all_categories:
            row.append(mv.get(c, 0))
        array.append(row)
    result["monthly_by_categories"] = array

    errors_arr = [[], []]
    current_value = 0.0
    left_date = bk.entries[0].day
    for e in bk.filter(cmds=(None, "milestone")):
        if e.cmd == "milestone":
            period = "{}-{}".format(left_date.strftime("%d.%m"), e.day.strftime("%d.%m"))
            errors_arr[0].append(period)
            cell = {
                "value":  e.value - current_value,
                "note": ["Accounted: {:.0f}".format(current_value), "Actual: {:.0f}".format(e.value)]
            }
            errors_arr[1].append(cell)
            current_value = e.value
            left_date = e.day
        else:
            current_value += e.value

    result["errors"] = errors_arr

    return result


class LineFormatError(Exception):
    pass

class HttpTestServer(BaseHTTPRequestHandler):

    def load_data(self):
        money_txt_path = os.environ.get("MONEY_TXT_PATH", config.money_txt_path)
        with open(money_txt_path, "r", encoding="utf8") as ff:
            text = ff.read()
        start_index = text.find("\n\n\n")
        if start_index != -1: text = text[start_index:]
        bk = Bookkeeper()
        for line in text.split("\n"):
            try:
                bk.account(line)
            except Exception as e:
                raise LineFormatError('Error\n{}\nprocessing line\n{}'.format(e, line))

        return bk

    # routing
    route_root = "^[/]{0,1}$"
    route_chart = "^/chart[/]{0,1}$"

    def do_GET(self):
        importlib.reload(config)
        try:
            bk = self.load_data()
            model = make_model(bk)
            if re.match(self.route_root, self.path):
                self.do_GET_root(model)
            elif re.match(self.route_chart, self.path):
               self.do_GET_chart(model)
        except Exception as e:
            self.do_GET_error(e)

    def do_GET_error(self, e):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_stuff.html_error_template.format(e).encode('utf-8'))



    def do_GET_root(self, model):
        html = html_stuff.represent_html(model)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def expenses_by_periods_plot(self, labels, values):
        ind = np.arange(len(values))
        plt.figure(figsize=(7,4))
        plt.bar(ind, values, facecolor='green', alpha=0.5, width=0.9)
        _, lbs = plt.xticks(ind + ind[1]/3, labels)
        plt.setp(lbs, rotation=70)
        plt.rc('font', size=9)
        plt.tight_layout()
        return plt.gcf()

    def do_GET_chart(self, model):
        pp = self.expenses_by_periods_plot(
            model["selected_expenses_weekly"][0],
            [a['value'] for a in model["selected_expenses_weekly"][1]]
        )

        figdata = BytesIO()
        format = "png"
        pp.savefig(figdata, format=format)

        self.send_response(200)
        self.send_header("Content-type", "image/" + format)
        self.end_headers()
        self.wfile.write(figdata.getvalue())


if __name__ == "__main__":
    the_server = HTTPServer(("", config.port), HttpTestServer)
    try:
        the_server.serve_forever()
    except KeyboardInterrupt:
        pass

    the_server.server_close()
