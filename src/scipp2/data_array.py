# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
# @author Simon Heybrock
import scipp as sc

from .data_group import DataGroup


class FrozenDataGroup(DataGroup):

    def __init__(self, sizes, items):
        self._sizes = sizes
        super().__init__(items)

    def __setitem__(self, name, value):
        for dim, size in value.sizes.items():
            # TODO What will happen to 'None' in shape?
            if self._sizes.get(dim) != size:
                raise sc.DimensionError("bad dims for meta data")
        super().__setitem__(name, value)


class DataArray:
    """
    An array of data (with dims and shape) combined with coords and masks.
    """

    def __init__(self, data, coords=None, masks=None, labels=None):
        # TODO Use DataGroup subclass with frozen dims and definite shape?
        # Allow extra dims (including dims with size=None?)?
        self.coords = FrozenDataGroup(data.sizes, coords)
        # da.coords.is_aligned('x')
        # da.coords.align('x')
        # da.coords.unalign('x')
        # Constructor?? Adding multiple from dict??
        self.masks = {} if masks is None else masks
        # is there a case for splitting attrs and labels if we support values
        # without dims/shape? Name clashes?
        # ... and different in HDF5
        self.labels = {} if labels is None else labels
        self.attrs = {}
        # TODO
        # - check that data has dims and shape
        # - check that data does not have coords
        self.data = data

    def __repr__(self):
        r = 'DataArray(\n'
        r += '  coords:\n'
        for name, var in self.coords.items():
            r += f'    {name}: {var.sizes}\n'
        r += f'  data: {self.data.sizes}\n'
        r += ')'
        return r

    @property
    def dims(self):
        return self.data.dims

    @property
    def shape(self):
        return self.data.shape

    @property
    def sizes(self):
        return dict(zip(self.dims, self.shape))

    def __getitem__(self, key):
        # TODO forward getitem to data is applicable, and re-wrap with coords, masks?
        dim, index = key
        if isinstance(index, sc.Variable):
            da = sc.DataArray(data=sc.arange(dim, self.sizes[dim]),
                              coords={dim: self.coords[dim]})
            return self[dim, da[dim, index].value]
        coords = {name: coord[key] for name, coord in self.coords.items()}
        return DataArray(data=self.data[key], coords=coords)
