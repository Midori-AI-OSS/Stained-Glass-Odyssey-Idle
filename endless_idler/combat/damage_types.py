class DamageTypeBase:
    id: str = "generic"
    name: str = "Generic"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"


class Generic(DamageTypeBase):
    id = "generic"
    name = "Generic"

