#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import datetime

from money import *


class TestEntry(unittest.TestCase):
    def test_full_line(self):
        line = u"2015.07.09   food, milk  67+77,3+51+41+57.0+36+40 #tinned-food имудон, #tag2 40т"
        a = Entry()
        a.cats = ("food", "milk")
        a.day = datetime.date(2015, 7, 9)
        a.tags = ["tinned-food", "tag2"]
        a.value = -eval("67+77.3+51+41+57+36+40")
        a.note = u"имудон, 40т"
        self.assertEqual(Entry(line), a)

    def test_positive_value(self):
        line = "2015.07.09   food, milk +67+77+51+41+57+36+40 #tinned-food #tag2"
        a = Entry()
        a.cats = ("food", "milk")
        a.day = datetime.date(2015, 7, 9)
        a.tags = ["tinned-food", "tag2"]
        a.value = eval("67+77+51+41+57+36+40")
        self.assertEqual(Entry(line), a)

    def test_shortest_line(self):
        line = "2015.07.08 household      34"
        a = Entry()
        a.day = datetime.date(2015, 7, 8)
        a.cats = ("household",)
        a.tags = []
        a.value = -34
        self.assertEqual(Entry(line), a)

    def test_whitespace_or_empty_line(self):
        self.assertEqual(Entry(""), Entry())
        self.assertEqual(Entry("     "), Entry())

    def test_line_without_date(self):
        day = datetime.date(2014, 11, 23)
        actual = Entry('food, cheese 22', day)
        expected = Entry()
        expected.day = day
        expected.cats = ('food', 'cheese')
        expected.value = -22
        self.assertEqual(actual, expected, '\n'+repr(expected.__dict__)+'\n'+(repr(actual.__dict__)))


class TestDevelopment(unittest.TestCase):
    def test_load_df(self):
        df = load_df()
        d = df.tail(10)
        x = 1


if __name__ == "__main__":
    unittest.main()
