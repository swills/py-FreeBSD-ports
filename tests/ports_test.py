# -*- coding: utf-8 -*-
import pickle
import unittest

from FreeBSD_ports import FreeBSD_ports
from FreeBSD_ports import main


def test_main_trivial():
    assert main() == 0


class DataTests(unittest.TestCase):
    def test_one_index_line(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        testlinefile = open('tests/d2.pkl', 'rb')
        testline = pickle.load(testlinefile)
        testlinefile.close()
        resultfile = open('tests/d3.pkl', 'rb')
        expected_result = pickle.load(resultfile)
        resultfile.close()
        actual_result = ports.parse_index_line(testline)
        self.assertEqual(expected_result, actual_result)

    def test_known_index_file(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        self.assertEqual(len(ports.indexinfo), 32322)

    def test_maintainer_search(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        maintainer = ports.search_maintainer('swills@FreeBSD.org')
        self.assertEqual(len(maintainer), 227)
