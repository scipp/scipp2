# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
# @author Simon Heybrock
from __future__ import annotations
import operator
from typing import Callable


class DataGroup:
    """
    A group of data. Has dims and shape, but no coords.
    """

    def __init__(self, items=None):
        self._items = {}
        if items is not None:
            for name, item in items.items():
                self[name] = item

    def __repr__(self):
        r = 'DataGroup(\n'
        for name, var in self.items():
            r += f'    {name}: {var.sizes}\n'
        r += ')'
        return r

    @property
    def dims(self):
        dims = ()
        for var in self.values():
            # Preserve insertion order
            for dim in var.dims:
                if dim not in dims:
                    dims = dims + (dim, )
        return dims

    @property
    def shape(self):
        dims = self.dims

        def dim_size(dim):
            sizes = []
            for var in self.values():
                if dim in var.dims:
                    sizes.append(var.sizes[dim])
            sizes = set(sizes)
            if len(sizes) == 1:
                return next(iter(sizes))
            return None

        return tuple(dim_size(dim) for dim in dims)

    @property
    def sizes(self):
        return dict(zip(self.dims, self.shape))

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def items(self):
        return list(zip(self.keys(), self.values()))

    def __iter__(self):
        yield from self._items

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __getitem__(self, name):
        if isinstance(name, str):
            return self._items[name]
        dim, index = name
        if isinstance(index, int) and self.sizes[dim] is None:
            raise ValueError(
                f"Positional indexing dim {dim} not possible as the length is not "
                "unique.")
        out = DataGroup()
        for key, var in self.items():
            if dim in var.dims:
                out[key] = var[dim, index]
            else:
                out[key] = var
        return out

    def __setitem__(self, name, value):
        if not (hasattr(value, 'dims') and hasattr(value, 'shape')
                and hasattr(value, 'sizes')):
            raise ValueError("Cannot insert item without dims and shape.")
        self._items[name] = value

    def __delitem__(self, name: str):
        del self._items[name]

    def get(self, name: str, default=None, /):
        return self._items.get(name, default)

    def pop(self, name: str, default=None, /):
        return self._items.pop(name, default)

    def clear(self):
        self._items.clear()

    def __add__(self, other):
        return _data_group_binary(operator.add, self, other)

    def __mul__(self, other):
        return _data_group_binary(operator.mul, self, other)

    def _call_method(self, func: Callable) -> DataGroup:
        """Call method on all values and return new DataGroup containing the results."""
        return DataGroup({key: func(value) for key, value in self.items()})

    def copy(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('copy', *args, **kwargs))

    def bin(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('bin', *args, **kwargs))

    def group(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('group', *args, **kwargs))

    def hist(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('hist', *args, **kwargs))

    def sum(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('sum', *args, **kwargs))

    def mean(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('mean', *args, **kwargs))

    def min(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('min', *args, **kwargs))

    def max(self, *args, **kwargs):
        return self._call_method(operator.methodcaller('max', *args, **kwargs))


def _data_group_binary(func: Callable, dg1: DataGroup, dg2: DataGroup) -> DataGroup:
    return DataGroup({key: func(dg1[key], dg2[key]) for key in dg1.keys() & dg2.keys()})
