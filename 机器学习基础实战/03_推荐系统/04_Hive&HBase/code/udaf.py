#!/usr/bin/env python
# encoding: utf-8


"""
@author:  'Administrator'
@contact:  
@time: 
"""
import sys
import logging
from itertools import groupby
from operator import itemgetter
import numpy as np
import pandas as pd

SEP = ','
NULL = '\\N'

_logger = logging.getLogger(__name__)


def read_input(input_data):
    for line in input_data:
        yield line.strip().split(SEP)


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    data = read_input(sys.stdin)
    for vtype, group in groupby(data, itemgetter(1)):
        _logger.info("Reading group {}...".format(vtype))
        group = [(int(rowid), vtype, np.nan if price == NULL else float(price))
                 for rowid, vtype, price in group]
        df = pd.DataFrame(group, columns=('id', 'vtype', 'price'))
        output = [vtype, df['price'].mean(), df['price'].std()]
        print(SEP.join(str(o) for o in output))


if __name__ == '__main__':
    main()