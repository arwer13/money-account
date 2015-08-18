#!/usr/bin/env python3
import re
import datetime
import bisect
from functools import total_ordering
from dateutil import rrule
from pprint import pprint
from http.server import BaseHTTPRequestHandler, HTTPServer


g_money_txt_path = "/home/arwer/Notes/money.txt"


html_template = """<html>
<head><title>{title}</title></head>
<body>
<h1>Total: {total_value:.0f} </h1> </br>
<h1>Current weak: {spent_on_current_week:.0f} </h1>


</body>
</html>"""



@total_ordering
class Entry:

    def __init__(self, s=None):
        self.cats = None
        self.tags = None
        self.time = None
        self.value = None
        if s is None:
            return
        if s.strip() == "" or s.strip()[0] == '#':
            return
        r = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d) *(.*) +([\(\)\d\+-\.,]+) *')
        date_gr, desc_gr, value_gr = r.match(s).groups()

        if ';' not in desc_gr: desc_gr += ';'
        value_gr = value_gr.replace(',', '.')

        cats, tags = map(str.strip, desc_gr.split(';'))
        self.cats = list(filter(None, map(str.strip, cats.split(','))))
        self.tags = set(filter(None, map(str.strip, tags.split(','))))
        self.time = datetime.date(*map(int, date_gr.split('.')))
        self.value = eval(value_gr) if value_gr[0] == '+' else -eval(value_gr)

    def __str__(self):
        return "{} {};{} {:.1f}".format(self.time, ','.join(self.cats), ','.join(self.tags), -self.value)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # return self.__str__() == other.__str__()
        return self.cats == other.cats and self.time == other.time and self.tags == other.tags and self.value == other.value

    def __ge__(self, other):
        return self.time >= other.time



class Bookkeeper:

    def __init__(self):
        self.entries = []

    def closest_monday(self, date):
        while date.weekday() != 0:
            date -= datetime.timedelta(days=1)
        return date

    def process(self, e):
        if e != Entry():
            bisect.insort_left(self.entries, e)

    def get_total_value(self, entries=None):
        if entries is None:
            entries = self.entries
        return sum([e.value for e in entries])

    def expenses_by_period(self, begin, end):
        return list(filter(lambda x: begin <= x.time < end and x.value < 0, self.entries))

    def expenses_by_cats(self, cats):
        result = []
        for e in self.entries:
            if len(e.cats) >= len(cats) and all([e.cats[i] == cats[i] for i in range(len(cats))]):
                result.append(e)
        return result

    def every_calendar_weak(self):
        result = dict()
        start_date = min(e.time for e in self.entries)
        while start_date.weekday() != 0:
            start_date -= datetime.timedelta(days=1)
        for dt in rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=datetime.date.today()):
            begin, end = dt.date(), dt.date() + datetime.timedelta(days=7)
            es = list(filter(lambda x: begin <= x.time < end and x.value < 0, self.entries))
            result[(begin, end)] = -sum(a.value for a in es)
        return result

    def spent_on_current_week(self):
        start_date = self.closest_monday(datetime.date.today())
        finish_date = datetime.date.today() + datetime.timedelta(days=1)
        es = self.expenses_by_period(start_date, finish_date)
        return -self.get_total_value(es)


class HttpTestServer(BaseHTTPRequestHandler):

    def load_data(self):
        bk = Bookkeeper()
        with open(g_money_txt_path, "r") as ff:
            text = ff.read()
        start_index = text.find("\n\n\n")
        if start_index != -1: text = text[start_index:]
        bk = Bookkeeper()
        for line in text.split("\n"):
            e = Entry(line)
            bk.process(e)
        return bk

    def do_GET(self):
        bk = self.load_data()
        fields = dict()
        fields["title"] = "Welcome!"
        fields["total_value"] = bk.get_total_value()
        fields["spent_on_current_week"] = bk.spent_on_current_week()
        html = html_template.format(**fields)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))



if __name__ == "__main__":
    the_server = HTTPServer(("localhost", 13013), HttpTestServer)
    try:
        the_server.serve_forever()
    except KeyboardInterrupt:
        pass

    the_server.server_close()
