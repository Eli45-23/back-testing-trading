"""Pure as-of registry; breached and old swings are never filtered."""


class Registry:
    def __init__(self, levels):
        self.levels = tuple(sorted(levels, key=lambda x: (x.available_at, x.id)))
        if len({x.id for x in self.levels}) != len(self.levels):
            raise ValueError("Duplicate level identity")

    def at(self, timestamp):
        if timestamp.utcoffset() is None:
            raise ValueError("Aware as-of required")
        return tuple(x for x in self.levels if x.available_at <= timestamp and
                     (x.expires_at is None or timestamp < x.expires_at))
