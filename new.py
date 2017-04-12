#!/usr/bin/env python2
import os
import re
import datetime
from functools import total_ordering

import pandas as pd
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import flask


app = flask.Flask(__name__)


DEFAULT_MONEY_TXT_PATH = os.path.join(os.path.expanduser("~"),
                                      "Dropbox/Apps/money.txt-dev/money.txt")
MONEY_TXT_PATH_ENV = "MONEY_TXT_PATH"
DROPBOX_TOKEN_ENV = "MONEY_TXT_DROPBOX_TOKEN"


@app.route("/")
def index():
    args = flask.request.args
    begin = args.get("begin")
    begin = datetime.date.today() \
        if begin is None \
        else datetime.datetime.strptime(begin, "%Y-%m-%d").date()
    end = args.get("end")
    end = datetime.date.today() \
        if end is None \
        else datetime.datetime.strptime(end, "%Y-%m-%d").date()

    df = load_df()
    for_period = df[df.value < 0.0][df.date >= begin][df.date <= end]\
        .groupby(by="cat1").sum().sort_values("value")
    return for_period.to_html()


@total_ordering
class Entry:

    def __init__(self, s=None, date=None):
        self.cats = []
        self.tags = []
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

            value_gr = value_gr.replace(',', '.')
            note_words = list(filter(None, note_gr.split()))
            self.day = date if date_gr is None else datetime.date(*map(int, date_gr.split('.')))
            self.cats = tuple(filter(None, map(str.strip, desc_gr.split(','))))
            self.value = eval(value_gr) if value_gr[0] == '+' else -eval(value_gr)
            self.note = ' '.join(filter(lambda x: x[0] != '#', note_words))
            self.tags = list(map(lambda x: x[1:], filter(lambda x: x[0] == '#', note_words)))

    def __str__(self):
        if self.cmd is None:
            value_str = "{:.1f}".format(-self.value) if self.value < 0 else "+{:.0f}".format(self.value)
            return "{} {} {} {} {}".format(self.day, ','.join(self.cats), value_str,
                                           '' if self.note is None else self.note, ' '.join(map(lambda x: '#'+x, self.tags)))
        else:
            return "{} !{} {:.1f}".format(self.day, self.cmd, self.value)

    def __repr__(self):
        return '\n'+str(self.__dict__)

    def __eq__(self, other):
        return self.cats == other.cats and self.day == other.day and self.tags == other.tags \
               and self.value == other.value and self.note == other.note

    def __gt__(self, other):
        return self.day > other.day


def load_money_txt():
    if MONEY_TXT_PATH_ENV in os.environ:
        print('Loading local money.txt from {}'.format(MONEY_TXT_PATH_ENV))
        with open(os.environ[MONEY_TXT_PATH_ENV]) as ff:
            text = ff.read()
    elif DROPBOX_TOKEN_ENV in os.environ:
        print('Loading local money.txt from Dropbox')
        import dropbox_stuff
        text = dropbox_stuff.get_money_txt(os.environ[DROPBOX_TOKEN_ENV])
        if text is None:
            print('Can not load money.txt from Dropbox')
    elif os.path.exists(DEFAULT_MONEY_TXT_PATH):
        with open(DEFAULT_MONEY_TXT_PATH) as ff:
            text = ff.read()
    else:
        raise RuntimeError(
            "Can not find any of environmental variables: {}. "
            "And there is no file at default path {}".format(
                ', '.join([MONEY_TXT_PATH_ENV, DROPBOX_TOKEN_ENV]),
                DEFAULT_MONEY_TXT_PATH))
    return text


def load_money_txt_lines():
    text = load_money_txt()
    start_index = text.find("START")
    start_index = text.find("\n", start_index)
    if start_index != -1:
        text = text[start_index:]
    return filter(None, text.splitlines())


def load_df():
    df = pd.DataFrame()
    for line in load_money_txt_lines():
        e = Entry(line)
        d = {
            "value": e.value,
            "cat1": e.cats[0] if len(e.cats) > 0 else None,
            "cat2": e.cats[1] if len(e.cats) > 1 else None,
            "cat3": e.cats[2] if len(e.cats) > 2 else None,
            "date": e.day,
            "note": e.note,
        }
        df = df.append(d, ignore_index=True)
    return df


def split_monthly(period, first_day):
    assert len(period) == 2
    assert 1 <= first_day <= 28

    periods = list()
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=period[0],
                          until=period[1]):
        periods.append((dt.date(),
                       dt.date() + relativedelta(months=1)
                       - relativedelta(days=1)))
    return periods


if __name__ == "__main__":
    app.run()
    # df = load_df()
    # pass
    # whole_period = df.at[0, 'date'], df.at[len(df)-1, 'date']
    # periods = split_monthly(whole_period, 1)
    # print(df)