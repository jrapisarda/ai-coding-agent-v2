"""Minimal subset of the Pydantic API used for tests."""

from __future__ import annotations

from typing import Any, Dict, TypeVar


class ValidationError(Exception):
    def __init__(self, errors: list[dict[str, Any]]):
        super().__init__(str(errors))
        self._errors = errors

    def errors(self) -> list[dict[str, Any]]:
        return self._errors


def Field(*, description: str | None = None, default: Any = None) -> Any:
    return default


class HttpUrl(str):
    """Simplified string alias for URLs."""


T = TypeVar("T", bound="BaseModel")


class BaseModel:
    def __init__(self, **data: Any) -> None:
        for field in self.__annotations__:
            if field in data:
                value = data[field]
            elif hasattr(self.__class__, field):
                value = getattr(self.__class__, field)
            else:
                value = None
            setattr(self, field, value)

    def model_dump(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.__annotations__}

    @classmethod
    def model_validate(cls: type[T], data: Any) -> T:
        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise ValidationError([
                {"type": "type_error", "loc": (), "msg": "Expected dict"}
            ])
        missing = [
            field
            for field in cls.__annotations__
            if field not in data and not hasattr(cls, field)
        ]
        if missing:
            raise ValidationError(
                [
                    {
                        "type": "missing",
                        "loc": (field,),
                        "msg": "Field required",
                    }
                    for field in missing
                ]
            )
        return cls(**data)
