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

    # find ports maintained by maintainer
    def search_maintainer(self, maintainer) -> list:
        ports = []
        for pkg in self.indexinfo:
            if pkg['maintainer'] == maintainer:
                ports.append(pkg)
        return ports

    # find origin from pkgname
    def lookup_portdir(self, pkgname) -> str:
        portdir = ''
        for pkg in self.indexinfo:
            if pkg['pkgname'] == pkgname:
                portdir = pkg['portdir']
        return portdir

    # return build depends pkg names of given portdir
    def build_depends(self, portdir) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['portdir'] == portdir:
                deps = pkg['bdep']
        return deps

    # return build depends port dirs of given portdir
    def build_depends_ports(self, portdir) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['portdir'] == portdir:
                for dep in pkg['bdep']:
                    deps.append(self.lookup_portdir(dep))
        return deps

    # return run depends pkg names of given portdir
    def run_depends(self, portdir) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['portdir'] == portdir:
                deps = pkg['rdep']
        return deps

    # return run depends port dirs of given portdir
    def run_depends_ports(self, portdir) -> list:
        deps = []
        for pkg in self.indexinfo:
            if pkg['portdir'] == portdir:
                for dep in pkg['rdep']:
                    deps.append(self.lookup_portdir(dep))
        return deps

    # return all index info for given pkgname name
    def find_port(self, pkgname) -> list:
        ports = []
        pattern = re.compile('^' + pkgname)
        for pkg in self.indexinfo:
            if re.match(pattern, pkg['pkgname']):
                ports.append(pkg)
        return ports

    # return portdir for given pkgname name
    def find_port_origin(self, pkgname) -> list:
        ports = []
        for pkg in self.indexinfo:
            if pkgname in pkg['pkgname']:
                ports.append(pkg['portdir'])
        return ports

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


def main() -> int:
    #    ports = FreeBSD_ports('tests/INDEX-13')
    #    print('All ports: ')
    #    for pkg in ports.indexinfo:
    #        print('{}: {}'.format(pkg['portdir'], pkg['pkgname']))
    #        print('\tfdeps: {}'.format(pkg['fdep']))
    #        print('\tedeps: {}'.format(pkg['edep']))
    #        print('\tpdeps: {}'.format(pkg['pdep']))
    #        print('\tbdeps: {}'.format(pkg['bdep']))
    #        print('\trdeps: {}'.format(pkg['rdep']))
    #        print('\twww: {}'.format(pkg['www']))
    #    print('swills@FreeBSD.org ports:')
    #    for pkg in ports.search_maintainer('swills@FreeBSD.org'):
    #        print('\t{}: {}'.format(pkg['portdir'], pkg['pkgname']))
    #        print('\tbuild_depends:')
    #        print('\t\t', ports.build_depends_ports(pkg['portdir']))
    #        print('\trun_depends:')
    #        print('\t\t', ports.run_depends_ports(pkg['portdir']))
    #    print('accerciser info:')
    #    print(ports.lookup_portdir('accerciser-3.22.0'))
    #    print('bdeps: ')
    #    print(ports.build_depends('accessibility/accerciser'))
    #    print('bdeps_origins: ')
    #    print(ports.build_depends_ports('accessibility/accerciser'))
    #    print('find_deps:')
    #    print(ports.find_port('py36-billiard'))
    #    print('find_deps:')
    #    # billiard kombu pytz vine
    #    print(ports.find_port_origin('py36-billiard'))
    #    print(ports.gen_py_dep('billiard'))
    #    print(ports.gen_py_dep('pytz'))
    #    print(ports.gen_py_dep('kombu'))
    #    print(ports.gen_py_dep('vine'))
    #    pkgname = ports.find_port('ruby-2')[0]['pkgname']
    #    rubydeps = ports.find_pkg_reverse_deps(pkgname)
    #    print(len(rubydeps))
    #    rubydeporigins = []
    #    for dep in rubydeps:
    #        rubydeporigins.append(ports.find_port_origin(dep))
    #    rubydeporigins = ports.find_pkg_reverse_deps_origins(pkgname)
    #    for origin in rubydeporigins:
    #        print(origin)
    #    pkgname = ports.find_port('ruby25-gems-')[0]['pkgname']
    #    rubydeporigins = ports.find_pkg_reverse_deps_origins(pkgname)
    #    for origin in rubydeporigins:
    #        print(origin)
    #     pkgname = ports.find_port('jsoncpp-')[0]['pkgname']
    #     deporigins = ports.find_pkg_reverse_deps_origins(pkgname)
    #     for origin in deporigins:
    #         print(origin)
    return 0


if __name__ == '__main__':
    main()
