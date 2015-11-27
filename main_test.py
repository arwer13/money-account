#!/usr/bin/env python3
import unittest
from main import *
import datetime
import html_stuff

class TestEntry(unittest.TestCase):

    def test_full_line(self):
        line = "2015.07.09   food, milk  67+77,3+51+41+57.0+36+40 #tinned-food имудон, #tag2 40т"
        a = Entry()
        a.cats = ("food", "milk")
        a.day = datetime.date(2015, 7, 9)
        a.tags = ["tinned-food", "tag2"]
        a.value = -eval("67+77.3+51+41+57+36+40")
        a.note = "имудон, 40т"
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

    def test_model(self):
        self.skipTest('Not up-to-date, needs ref')
        lines = """
    2015.07.25 food, fish 200
    2015.07.11 cats, fish 100
    2015.07.26 salary; some_place +1000
    2015.08.03 salary; some_place +8000

    2015.08.25 food, fish 200
    2015.08.11 cats, fish 100
    2015.08.20 salary; some_place +10000
    2015.09.05 salary; some_place +15000
    2015.09.10 food, meat 500
    2015.08.30 food 100
    2015.09.05 entertainment 300
"""
        bk = Bookkeeper()
        for a in lines.splitlines(keepends=False):
            bk.account(Entry(a))
        model = make_model(bk)
        em = dict()
        em["total_value"] = -200-100+1000+8000-200-100+10000+15000-500-100-300
        # em["selected_expenses_weekly"] =
        for k in set(em.keys()).intersection(set(model.keys())):
            self.assertEqual(model[k], em[k])



class TestHtmlStuff(unittest.TestCase):

    def test_make_html_table(self):
        self.skipTest('obsolete')
        table = [
            ["cats", "dogs", "platypuses"],
            [1,2,3]
        ]
        html_should_be = """<table>
<tr><td>cats</td><td>dogs</td><td>platypuses</td></tr>
<tr><td>1</td><td>2</td><td>3</td></tr>
</table>"""
        html = html_stuff.make_table(table)
        self.assertEqual(html, html_should_be)


if __name__ == "__main__":
    unittest.main()
