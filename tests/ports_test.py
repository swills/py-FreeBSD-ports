# -*- coding: utf-8 -*-
import pickle
import unittest

from FreeBSD_ports import FreeBSD_ports


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

    def test_find_portdir(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        res = ports.find_portdir('ruby-2')
        self.assertEqual(res, 'lang/ruby25')

    def test_find_portdir_2(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        portdir = ports.find_portdir('ruby-2.5.5_2,1')
        self.assertEqual(portdir, 'lang/ruby25')

    def test_find_portdir_3(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_portdir('py27-evdev')
        self.assertEqual(port, 'devel/py-evdev')

    def test_find_portdir_4(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_portdir('fist-')
        self.assertEqual(port, 'textproc/fist')

    def test_find_pkgname(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        pkgname = ports.find_pkgname('lang/ruby25')
        self.assertEqual(pkgname, 'ruby-2.5.5_2,1')

    def test_find_pkgname_2(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        pkgname = ports.find_pkgname('devel/py-evdev')
        self.assertEqual(pkgname, 'py27-evdev-0.8.1')

    def test_find_portinfo(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        pkginfo = ports.find_portinfo('devel/py-evdev')
        self.assertEqual(pkginfo[0]['pkgname'], 'py27-evdev-0.8.1')
        self.assertEqual(pkginfo[1]['pkgname'], 'py36-evdev-0.8.1')

    def test_find_pkginfo(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        pkginfo = ports.find_pkginfo('py27-evdev-0.8.1')
        self.assertEqual(pkginfo['portdir'], 'devel/py-evdev')

    def test_find_port_categories(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        port = ports.find_portinfo('textproc/fist')
        self.assertEqual(port[0]['categories'][0], 'textproc')

    def test_maintainer_search_count(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        maintainer = ports.search_maintainer('swills@FreeBSD.org')
        self.assertEqual(len(maintainer), 227)

    def test_find_build_depends_port(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        bdeps = ports.find_build_depends_port('deskutils/syncthing-gtk')
        self.assertEqual(len(bdeps), 108)
        self.assertEqual(bdeps[0], 'adwaita-icon-theme-3.28.0')

    def test_find_build_depends_pkg(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        bdeps = ports.find_build_depends_pkg('syncthing-gtk-0.9.4.3')
        self.assertEqual(len(bdeps), 108)
        self.assertEqual(bdeps[0], 'adwaita-icon-theme-3.28.0')

    def test_find_run_depends_port(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        rdeps = ports.find_run_depends_port('deskutils/syncthing-gtk')
        self.assertEqual(len(rdeps), 127)
        self.assertEqual(rdeps[0], 'adwaita-icon-theme-3.28.0')

    def test_find_run_depends_pkg(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        rdeps = ports.find_run_depends_pkg('syncthing-gtk-0.9.4.3')
        self.assertEqual(len(rdeps), 127)
        self.assertEqual(rdeps[0], 'adwaita-icon-theme-3.28.0')

    def test_reverse_deps(self):
        ports = FreeBSD_ports('tests/INDEX-13')
        stpd = ports.find_portdir('syncthing-1')
        stpn = ports.find_pkgname(stpd)
        revdeps = ports.find_pkg_reverse_deps(stpn)
        self.assertEqual(len(revdeps), 1)
        self.assertEqual(revdeps[0], 'syncthing-gtk-0.9.4.3')
