#!/usr/bin/env python3
import unittest
from main import *
import datetime

class TestSomething(unittest.TestCase):

    def test_full_line(self):
        line = "2015.07.09   food, milk; tinned food, tag2 67+77,3+51+41+57.0+36+40"
        a = Entry()
        a.cats = ["food", "milk"]
        a.time = datetime.date(2015, 7, 9)
        a.tags = set(["tinned food", "tag2"])
        a.value = -eval("67+77.3+51+41+57+36+40")
        self.assertEqual(Entry(line), a)

    def test_positive_value(self):
        line = "2015.07.09   food, milk; tinned food, tag2 +67+77+51+41+57+36+40"
        a = Entry()
        a.cats = ["food", "milk"]
        a.time = datetime.date(2015, 7, 9)
        a.tags = set(["tinned food", "tag2"])
        a.value = eval("67+77+51+41+57+36+40")
        self.assertEqual(Entry(line), a)

    def test_shortest_line(self):
        line = "2015.07.08 household      34"
        a = Entry()
        a.time = datetime.date(2015, 7, 8)
        a.cats = ["household"]
        a.tags = set()
        a.value = -34
        self.assertEqual(Entry(line), a)

    def test_whitespace_or_empty_line(self):
        self.assertEqual(Entry(""), Entry())
        self.assertEqual(Entry("     "), Entry())


if __name__ == "__main__":
    unittest.main()
