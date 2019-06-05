# -*- coding: utf-8 -*-
from FreeBSD_ports import main


def test_main_trivial():
    assert main() == 0
