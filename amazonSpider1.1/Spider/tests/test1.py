#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append("../")


def function():
    pass


if __name__ == '__main__':
    print(sys.argv[0].split('/')[-1].split('.')[0])