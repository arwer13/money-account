#!/usr/bin/env python3
import re

def parse_line(s):
    r = re.compile(r' *(\d\d\d\d\.\d\d\.\d\d) *(.*) +([\d\+-\.,]+) *')
    date_gr, desc_gr, count_gr = r.match(s).groups()
    return date_gr, desc_gr, count_gr
    # return None


if __name__ == "__main__":
    print("Hello")
