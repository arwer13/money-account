#!/usr/bin/env python3
import re
import datetime



def parse_line(s):
    r = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d) *([^;]+);?([^;]*) +([\d\+-\.,]+) *')
    date_gr, cat_gr, tag_gr, count_gr = r.match(s).groups()
    return date_gr, cat_gr, tag_gr, count_gr
    # return None


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
        return "{} {};{} {}".format(self.time, ','.join(self.cats), ','.join(self.tags), -self.value)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # return self.__str__() == other.__str__()
        return self.cats == other.cats and self.time == other.time and self.tags == other.tags and self.value == other.value



class Bookkeeper:

    def __init__(self):
        self.value = 0

    def process(self, e):
        if e != Entry():
            self.value += e.value

    def __str__(self):
        return "{}".format(self.value)

    def __repr__(self):
        return self.__str__()


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
    print(bk)
