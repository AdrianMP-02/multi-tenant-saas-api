from __future__ import annotations

import math
from collections.abc import Sequence

from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResult(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        arbitrary_types_allowed = True


def paginate(items: Sequence, total: int, params: PaginationParams) -> PaginatedResult:
    return PaginatedResult(
        items=list(items),
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=max(1, math.ceil(total / params.page_size)),
    )
