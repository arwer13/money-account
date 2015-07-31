#!/usr/bin/env python3
import unittest
import main


class TestSomething(unittest.TestCase):

    def test_parse_line(self):
        lines = [
                "2015.07.09   food; tinned food 67+77+51+41+57+36+40",
                "2015.07.08 household      34",
                " 2015.07.08 misc;  +500 "
        ]
        for s in lines:
            print(main.parse_line(s))
        self.assertEqual(1, 1)
        pass



if __name__ == "__main__":
    unittest.main()