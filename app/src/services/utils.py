from typing import NoReturn, Optional, TypeVar


def reserved_name_transformer(name: str) -> str:
    reserved_names_map = {"metadata": "metadata_"}

    return reserved_names_map.get(name, name)


_T = TypeVar("_T")


def Some(obj: Optional[_T]) -> _T | NoReturn:
    assert obj is not None

    return obj
