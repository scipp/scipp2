# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
# @author Simon Heybrock
import scipp as sc


class DataArray:

    def __init__(self, data, coords=None, masks=None, labels=None):
        self.coords = {} if coords is None else coords
        self.masks = {} if masks is None else masks
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
        dim, index = key
        if isinstance(index, sc.Variable):
            da = sc.DataArray(data=sc.arange(dim, self.sizes[dim]),
                              coords={dim: self.coords[dim]})
            return self[dim, da[dim, index].value]
        coords = {name: coord[key] for name, coord in self.coords.items()}
        return DataArray(data=self.data[key], coords=coords)
