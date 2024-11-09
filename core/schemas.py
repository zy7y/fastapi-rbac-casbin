from datetime import datetime
from typing import Generic, TypeVar
from typing_extensions import override

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="额外消息")
    data: T | None = Field(None, description="响应数据")

    @classmethod
    def ok(cls, data: T = None, message: str = "成功"):  # type: ignore
        return cls(data=data, message=message, success=True)

    @classmethod
    def error(cls, message: str = "失败"):
        return cls(data=None, message=message, success=False)


class PageResult(Result[T]):
    total: int = Field(0, description="数据总数")
    data: list[T] | None = Field(default_factory=list, description="响应数据")  # type: ignore

    @classmethod
    @override
    def ok(cls, data: list[T] | None = None, message: str = "成功", total: int = 0):  # type: ignore
        return cls(data=data or [], total=total, message=message, success=True)


class RequestSchema(BaseModel):
    """BaseRequestSchema"""

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


class ResponseSchema(BaseModel):
    """BaseResponseSchema"""

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class PageParams(RequestSchema):
    """分页参数"""

    page_number: int = Field(1, gt=0, description="页码")
    page_size: int = Field(10, description="每页数量")
