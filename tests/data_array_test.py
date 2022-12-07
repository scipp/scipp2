# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
import pytest
import scipp as sc
import scipp2 as s2


def test_slice():
    data = sc.array(dims=['xx', 'yy'], unit='m', values=[[1.1, 2.2], [3.3, 4.4]])
    da = s2.DataArray(data=data)
    assert da['xx', 1].dims == ('yy', )


def test_data_group_as_data():
    var1 = sc.array(dims=['x', 'y'],
                    unit='m',
                    values=[[1.1, 2.2, 3.3], [3.3, 4.4, 5.5]])
    var2 = sc.array(dims=['x'], unit='m', values=[0, 1])
    dg = s2.DataGroup({'a': var1, 'b': var2})
    da = s2.DataArray(data=dg)
    assert da.dims == ('x', 'y')
    assert da.shape == (2, 3)
    assert da['y', 1:2].dims == ('x', 'y')
    assert da['y', 1:2].shape == (2, 1)


def test_value_based_slicing():
    xy = sc.array(dims=['y', 'x'], unit='K', values=[[1.1, 2.2, 3.3], [3.3, 4.4, 5.5]])
    x = sc.array(dims=['x'], unit='m', values=[0, 1, 2])
    da = s2.DataArray(data=xy, coords={'x': x})
    assert sc.identical(da['x', sc.scalar(1, unit='m')].data, xy['x', 1])


def test_value_based_slicing_ignores_nested_coords():
    x = sc.arange('x', 4, unit='m')
    x2 = x * 2
    col = sc.DataArray(data=sc.ones_like(x2), coords={'x': x2})
    dg = s2.DataGroup({'a': col})
    da = s2.DataArray(data=dg, coords={'x': x})
    sel = da['x', sc.scalar(2, unit='m')]
    assert sc.identical(sel.data['a'], da['x', 2].data['a'])
    assert sc.identical(sel.data['a'].attrs['x'], sc.scalar(4, unit='m'))


def test_raises_if_coord_dims_exceed_data_dims():
    x = sc.arange('x', 4, unit='m')
    y = sc.arange('y', 4, unit='m')
    with pytest.raises(sc.DimensionError):
        s2.DataArray(x, coords={'x': x, 'y': y})
