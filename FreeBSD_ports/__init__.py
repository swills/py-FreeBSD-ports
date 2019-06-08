#!/usr/bin/env python3
#
# Copyright (c) 2019 Steve Wills <steve@mouf.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# import json
# from pprint import pprint
import re


class FreeBSD_ports:
    DEFAULT_INDEX_PATH = '/usr/ports/INDEX-13'

    def __init__(self, indexfile=DEFAULT_INDEX_PATH):
        self.indexfile = indexfile
        self.indexinfo = []
        self.indexinfo = self.parse_index_file(self.indexfile)
        self.pkgs_to_info = {pkg['pkgname']: pkg for pkg in self.indexinfo}

    def parse_index_line(self, line: str) -> dict:
        line = line.rstrip('\n')

        # INDEX and "describe" are different formats!
        # for INDEX, see:
        # https://github.com/freebsd/freebsd-ports/blob/master/Tools/make_index#L159-L180
        # https://github.com/freebsd/freebsd/blob/master/usr.sbin/portsnap/make_index/make_index.c#L380-L411

        (
            pkgname, portdir, prefix, comment, pkgdescr, maintainer,
            categories, bdep, rdep, www, edep, pdep, fdep,
        ) = line.split('|', 13)

        portdir = '/'.join(portdir.split('/')[-2:])
        bdep = bdep.split(' ')
        rdep = rdep.split(' ')
        edep = edep.split(' ')
        pdep = pdep.split(' ')
        fdep = fdep.split(' ')
        categories = categories.split(' ')
        port_info = {
            'pkgname': pkgname,
            'portdir': portdir,
            'prefix': prefix,
            'comment': comment,
            'pkgdescr': pkgdescr,
            'maintainer': maintainer,
            'categories': categories,
            'bdep': bdep,
            'rdep': rdep,
            'www': www,
            'edep': edep,
            'pdep': pdep,
            'fdep': fdep,
        }

        return port_info

    def parse_index_file(self, indexfile: str) -> list:
        indexinfo = []
        with open(indexfile) as file:
            for line in file:
                indexinfo.append(self.parse_index_line(line))
        return indexinfo

    # find portname from short incomplete package name, without version
    def find_portdir(self, pkgname):
        pattern = re.compile('^' + pkgname, re.IGNORECASE)
        try:
            for pkg in self.indexinfo:
                if re.match(pattern, pkg['pkgname']):
                    return pkg['portdir']
        except KeyError:
            raise KeyError(f'not found {pkgname}')

#    # find origin from exact pkgname
#    def find_pkgname_exact(self, pkgname) -> str:
#        try:
#            return self.pkgs_to_info[pkgname]['portdir']
#        except KeyError:
#            raise KeyError(f'not found {pkgname}')

    # find pkgname from portdir
    def find_pkgname(self, portdir) -> str:
        pattern = re.compile('^' + portdir)
        try:
            for pkg in self.indexinfo:
                if re.match(pattern, pkg['portdir']):
                    return pkg['pkgname']
        except KeyError:
            raise KeyError(f'not found {portdir}')

    # return all index info for given pkgname name, may return multiple entries
    # since a single port can generate more than one package and therefore more
    # than one pkg and more than one INDEX line
    def find_portinfo(self, portdir) -> list:
        ports = []
        for pkg in self.indexinfo:
            if portdir in pkg['portdir']:
                ports.append(pkg)
        return ports

    # return all index info for given pkgname name, single result
    def find_pkginfo(self, pkgname) -> list:
        try:
            return self.pkgs_to_info[pkgname]
        except KeyError:
            raise KeyError(f'not found {pkgname}')

    # find ports maintained by maintainer
    def search_maintainer(self, maintainer) -> list:
        ports = []
        for pkg in self.indexinfo:
            if pkg['maintainer'] == maintainer:
                ports.append(pkg)
        return ports

    # return build depends pkg names of given portdir
    def find_build_depends_port(self, portdir) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['portdir'] == portdir:
                deps = pkg['bdep']
        return deps

    # return build depends pkg names of given pkg
    def find_build_depends_pkg(self, pkgname) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['pkgname'] == pkgname:
                deps = pkg['bdep']
        return deps

    # return run depends pkg names of given portdir
    def find_run_depends_port(self, portdir) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['portdir'] == portdir:
                deps = pkg['rdep']
        return deps

    # return run depends pkg names of given pkg
    def find_run_depends_pkg(self, pkgname) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['pkgname'] == pkgname:
                deps = pkg['rdep']
        return deps

    # find deps of given pkg

    def find_pkg_reverse_deps(self, pkgname) -> list:
        ports = []
        for pkg in self.indexinfo:
            if pkgname in pkg['bdep']:
                if pkg['pkgname'] not in ports:
                    ports.append(pkg['pkgname'])
            if pkgname in pkg['rdep']:
                if pkg['pkgname'] not in ports:
                    ports.append(pkg['pkgname'])
            if pkgname in pkg['edep']:
                if pkg['pkgname'] not in ports:
                    ports.append(pkg['pkgname'])
            if pkgname in pkg['fdep']:
                if pkg['pkgname'] not in ports:
                    ports.append(pkg['pkgname'])
            if pkgname in pkg['pdep']:
                if pkg['pkgname'] not in ports:
                    ports.append(pkg['pkgname'])

        return ports

    # find origins of deps of given pkg
    def find_pkg_reverse_deps_origins(self, pkgname) -> list:
        ports = []
        for pkg in self.indexinfo:
            if pkgname in pkg['bdep']:
                if pkg['portdir'] not in ports:
                    ports.append(pkg['portdir'])
            if pkgname in pkg['rdep']:
                if pkg['portdir'] not in ports:
                    ports.append(pkg['portdir'])
            if pkgname in pkg['edep']:
                if pkg['portdir'] not in ports:
                    ports.append(pkg['portdir'])
            if pkgname in pkg['fdep']:
                if pkg['portdir'] not in ports:
                    ports.append(pkg['portdir'])
            if pkgname in pkg['pdep']:
                if pkg['portdir'] not in ports:
                    ports.append(pkg['portdir'])
        return ports

    # generate python dependency line
    def gen_py_dep(self, pkgname) -> list:
        portname = 'py36-' + pkgname
        origin = self.find_port_origin(portname)
        dep = '\t${{PYTHON_PKGNAMEPREFIX}}'
        dep = dep + '{}>=0:{}@${{PY_FLAVOR}} \\'.format(pkgname, origin[0])
        return dep
