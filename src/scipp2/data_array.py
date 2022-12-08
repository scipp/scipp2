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


class Coords(FrozenDataGroup):

    def __setitem__(self, name, value):
        # Shallow copy so alignment flag is internal to this Coord instance.
        copied = value.copy(deep=False)
        setattr(copied, '_scipp_align', getattr(value, '_scipp_align', True))
        super().__setitem__(name, copied)

    def is_aligned(self, name) -> bool:
        return self[name]._scipp_align

    def set_aligned(self, name, align: bool = True):
        self[name]._scipp_align = align


class DataArray:
    """
    An array of data (with dims and shape) combined with coords and masks.
    """

    def __init__(self, data, coords=None, masks=None, attrs=None):
        # coord/meta/attrs is horrible! must have flag instyead?!
        # have coord with alignment flag, but also attrs (never aligned)?
        # slicing and transform_coords switches flag off
        self._coords = Coords(data.sizes, coords)
        self._masks = FrozenDataGroup(data.sizes, masks)
        self._attrs = FrozenDataGroup(data.sizes, attrs)
        # da.coords.is_aligned('x')
        # da.coords.align('x')
        # da.coords.unalign('x')
        # Constructor?? Adding multiple from dict??
        # is there a case for splitting attrs and labels if we support values
        # without dims/shape? Name clashes?
        # ... and different in HDF5
        # TODO
        # - check that data has dims and shape
        # - check that data does not have coords
        self._data = data

    @property
    def coords(self):
        return self._coords

    @property
    def masks(self):
        return self._masks

    @property
    def attrs(self):
        return self._attrs

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if value.sizes != self.sizes:
            raise sc.DimensionError("Incompatible data size")
        self._data = value

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
