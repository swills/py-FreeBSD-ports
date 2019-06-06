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

        # load test data
        testlinefile = open('tests/d2.pkl', 'rb')
        testline = pickle.load(testlinefile)
        testlinefile.close()
        resultfile = open('tests/d3.pkl', 'rb')
        expected_result = pickle.load(resultfile)
        resultfile.close()

        # ensure it parsed properly
        actual_result = ports.parse_index_line(testline)
        self.assertEqual(expected_result, actual_result)

    def test_known_index_file(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        self.assertEqual(len(ports.indexinfo), 32322)

    def test_maintainer_search_count(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        maintainer = ports.search_maintainer('swills@FreeBSD.org')
        self.assertEqual(len(maintainer), 227)

    def test_maintainer_search_categories(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        maintainer = ports.search_maintainer('swills@FreeBSD.org')
        self.assertEqual(maintainer[0]['categories'][0], 'accessibility')

    def test_find_port_categories(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_port('fist-')
        self.assertEqual(port[0]['categories'][0], 'textproc')

    def test_find_port_portdir(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_port('fist-')
        self.assertEqual(port[0]['portdir'], 'textproc/fist')

    def test_find_port_py36_category(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_port('py36-evdev')
        self.assertEqual(port[0]['categories'][0], 'devel')

    def test_find_port_py36_portdir(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_port('py36-evdev')
        self.assertEqual(port[0]['portdir'], 'devel/py-evdev')

    def test_find_port_py27_category(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_port('py27-evdev')
        self.assertEqual(port[0]['categories'][0], 'devel')

    def test_find_port_py27_portdir(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_port('py27-evdev')
        self.assertEqual(port[0]['portdir'], 'devel/py-evdev')
