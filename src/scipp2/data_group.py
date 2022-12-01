# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)
# @author Simon Heybrock


class DataGroup:

    def __init__(self, items=None):
        self.items = {} if items is None else items

    def __repr__(self):
        r = 'DataGroup(\n'
        for name, var in self.items.items():
            r += f'    {name}: {var.sizes}\n'
        r += ')'
        return r

    @property
    def dims(self):
        dims = ()
        for var in self.items.values():
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
            for var in self.items.values():
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

    def __getitem__(self, name):
        if isinstance(name, str):
            return self.items[name]
        dim, index = name
        if isinstance(index, int) and self.sizes[dim] is None:
            raise ValueError(
                f"Positional indexing dim {dim} not possible as the length is not "
                "unique.")
        out = DataGroup()
        for key, var in self.items.items():
            if dim in var.dims:
                out[key] = var[dim, index]
            else:
                out[key] = var
        return out

    def __setitem__(self, name, value):
        self.items[name] = value
