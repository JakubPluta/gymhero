from typing import Tuple

from fastapi import Query


def get_pagination_params(
    skip: int = Query(0, ge=0), limit: int = Query(10, gt=0)
) -> Tuple[int, int]:
    return skip, limit
