#!/usr/bin/env python3
import re




def parse_line(s):
    r = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d) *([^;]+);?([^;]*) +([\d\+-\.,]+) *')
    date_gr, cat_gr, tag_gr, count_gr = r.match(s).groups()
    return date_gr, cat_gr, tag_gr, count_gr
    # return None


class Entry:
    def __init__(self):
        self.categories = None
        self.tags = None
        self.time = None
        self.increment = None

    def __init__(self, s):
        r = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d) *(.*) +([\d\+-\.,]+) *')
        date_gr, desc_gr, count_gr = r.match(s).groups()
        pass

    def __str__(self):
        return ''.format(self.category)



if __name__ == "__main__":
    print("Hello")
