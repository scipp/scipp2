# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc
import scipp2 as s2


def test_add():
    x = sc.arange('x', 4, unit='m')
    dg1 = s2.DataGroup({'a': x})
    dg2 = s2.DataGroup({'a': x, 'b': x})
    result = dg1 + dg2
    assert 'a' in result
    assert 'b' not in result
    assert sc.identical(result['a'], x + x)


def test_eq():
    x = sc.arange('x', 4, unit='m')
    dg1 = s2.DataGroup({'a': x})
    dg2 = s2.DataGroup({'a': x, 'b': x})
    result = dg1 == dg2
    assert 'a' in result
    assert 'b' not in result
    assert sc.identical(result['a'], x == x)


def test_hist():
    table = sc.data.table_xyz(1000)
    dg = s2.DataGroup()
    dg['a'] = table[:100]
    dg['b'] = table[100:]
    hists = dg.hist(x=10)
    assert sc.identical(hists['a'], table[:100].hist(x=10))
    assert sc.identical(hists['b'], table[100:].hist(x=10))
