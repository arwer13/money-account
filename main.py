#!/usr/bin/env python3
import re
import datetime
import bisect
from functools import total_ordering
from dateutil import rrule
from pprint import pprint

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

    def process(self, e):
        if e != Entry():
            bisect.insort_left(self.entries, e)

    def get_total_value(self):
        return sum([e.value for e in self.entries])

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


if __name__ == "__main__":
    file_path = "/home/arwer/Notes/money.txt"
    with open(file_path, "r") as ff:
        text = ff.read()
    start_index = text.find("\n\n\n")
    if start_index != -1: text = text[start_index:]
    bk = Bookkeeper()
    for line in text.split("\n"):
        e = Entry(line)
        bk.process(e)
    print(bk.get_total_value())
    weakly = bk.every_calendar_weak()
    pprint(weakly)
    pprint(bk.expenses_by_cats(["food","water"]))
