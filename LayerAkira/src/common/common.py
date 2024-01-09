from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    data: T
    error_type: Optional[Any] = None
    error: str = ''
