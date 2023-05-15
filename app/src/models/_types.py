import datetime
import uuid
from typing import Annotated, TypeAlias, Union

from sqlalchemy import UUID, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column
from ulid import ULID

_T_JSONDict: TypeAlias = dict[
    str,
    Union[
        int,
        float,
        bool,
        str,
        None,
        list[Union[int, float, bool, str, None, "_T_JSONDict"]],
        "_T_JSONDict",
    ],
]


ulid_pk = Annotated[
    uuid.UUID,
    mapped_column(
        UUID(as_uuid=True),
        default=lambda: ULID().to_uuid(),
        primary_key=True,
    ),
]

ulid = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True))]

timestamp = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime,
        default=datetime.datetime.now(tz=datetime.UTC),
    ),
]
timestamp_now = Annotated[
    datetime.datetime,
    mapped_column(
        default=datetime.datetime.now(tz=datetime.UTC),
        onupdate=datetime.datetime.now(tz=datetime.UTC),
    ),
]
sha256 = Annotated[str, mapped_column(String(64))]

varchar50 = Annotated[str, mapped_column(String(50))]
varchar255 = Annotated[str, mapped_column(String(255))]
jsonb = Annotated[_T_JSONDict, mapped_column(JSONB)]
numeric18_2 = Annotated[
    float,
    mapped_column(
        Numeric(
            18,
            2,
            asdecimal=False,
        ),
    ),
]
