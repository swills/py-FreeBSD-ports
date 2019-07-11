#!/usr/bin/env python3
import argparse

from FreeBSD_ports import FreeBSD_ports


def main():
    parser = argparse.ArgumentParser(description='Search ports INDEX')
    parser.add_argument(
        'searchtype', type=str,
        choices=['port', 'pkg', 'maintainer', 'revdeps'],
    )
    parser.add_argument('searchvalue', type=str)
    args = parser.parse_args()
    ports = FreeBSD_ports()
    if args.searchtype == 'maintainer':
        for pkg in ports.search_maintainer(args.searchvalue):
            print('\t{}'.format(pkg['pkgname']))
    elif args.searchtype == 'port':
        print(ports.find_portdir(args.searchvalue))
    elif args.searchtype == 'pkg':
        print(ports.find_pkgname(args.searchvalue))
    elif args.searchtype == 'revdeps':
        for pkg in ports.find_pkg_reverse_deps(args.searchvalue):
            print(pkg)


if __name__ == '__main__':
    main()
