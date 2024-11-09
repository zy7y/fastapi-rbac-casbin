import re
from datetime import datetime
from enum import StrEnum
from typing import Generic, List, Optional, TypeVar, override  # type: ignore

from pydantic import BaseModel, Field, field_validator
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class BRQ(BaseModel):
    """BaseRequestSchema"""

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
    }


class BRS(BaseModel):
    """BaseResponseSchema"""

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class LoginReq(BRQ):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Route(LoginReq):
    """接口"""

    path: str = Field(..., description="路由地址")
    name: str = Field(..., description="路由名称")
    method: str = Field(..., description="请求方法")
    summary: str | None = Field(None, description="路由描述")
    tags: List[str] | None = Field(None, description="路由分组")

    @field_validator("path")
    @classmethod
    def path_validator(cls, v):
        return re.sub(r"\{.*?\}", ":id", v)


class Token(BRQ):
    """登录成功返回token"""

    access_token: str


class AssignRole(BRQ):
    """分配角色"""

    role_ids: list[int] = Field(..., description="角色ID列表")
    user_id: int = Field(..., description="用户ID")


class AssignMenu(BRQ):
    """分配菜单"""

    menu_ids: list[int] = Field(..., description="菜单ID列表")
    role_id: int = Field(..., description="角色ID")


class AssignRoute(BRQ):
    """分配接口"""

    routes: list[Route] = Field(..., description="接口列表")
    role_id: int = Field(..., description="角色ID")


class Result(BaseModel, Generic[T]):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="额外消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def ok(cls, data: T = None, message: str = "成功"):  # type: ignore[assignment]
        return cls(data=data, message=message, success=True)

    @classmethod
    def error(cls, message: str = "失败"):
        return cls(data=None, message=message, success=False)


class PageResult(Result[T]):
    total: int = Field(0, description="数据总数")
    data: List[T] = Field(default_factory=list, description="响应数据")  # type: ignore[assignment]

    @classmethod
    @override
    def ok(cls, data: list[T] = None, message: str = "成功", total: int = 0):  # type: ignore[assignment]
        return cls(data=data, total=total, message=message, success=True)


class UserFieldEnum(StrEnum):
    ID_ASC = "id"
    ID_DESC = "-id"
    USERNAME_ASC = "username"
    USERNAME_DESC = "-username"
    PASSWORD_ASC = "password"
    PASSWORD_DESC = "-password"
    ROLES_ASC = "roles"
    ROLES_DESC = "-roles"


class User(BaseModel):
    id: Optional[int] = Field(None)
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class Info(User):
    roles: list["Role"] | None = Field(None)
    active_role: Optional["Role"] = Field(None)


class UserQueryParams(User):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    order_by: Optional[List[UserFieldEnum]] = Field(
        None, description="排序字段查询时使用"
    )


class RoleFieldEnum(StrEnum):
    ID_ASC = "id"
    ID_DESC = "-id"
    NAME_ASC = "name"
    NAME_DESC = "-name"
    MENUS_ASC = "menus"
    MENUS_DESC = "-menus"


class Role(BaseModel):
    id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class RoleQueryParams(Role):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    order_by: Optional[List[RoleFieldEnum]] = Field(
        None, description="排序字段查询时使用"
    )


class MenuFieldEnum(StrEnum):
    ID_ASC = "id"
    ID_DESC = "-id"
    NAME_ASC = "name"
    NAME_DESC = "-name"
    PARENT_ASC = "parent"
    PARENT_DESC = "-parent"
    PATH_ASC = "path"
    PATH_DESC = "-path"
    ICON_ASC = "icon"
    ICON_DESC = "-icon"
    COMPONENT_ASC = "component"
    COMPONENT_DESC = "-component"
    META_ASC = "meta"
    META_DESC = "-meta"
    REDIRECT_ASC = "redirect"
    REDIRECT_DESC = "-redirect"
    PERMISSION_ASC = "permission"
    PERMISSION_DESC = "-permission"
    TYPE_ASC = "type"
    TYPE_DESC = "-type"


class Menu(BaseModel):
    id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    parent: Optional[None] = Field(None)
    path: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    component: Optional[str] = Field(None)
    meta: Optional[dict] = Field(None)
    redirect: Optional[str] = Field(None)
    permission: Optional[str] = Field(None)
    type: Optional[int] = Field(None)
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class MenuQueryParams(Menu):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    order_by: Optional[List[MenuFieldEnum]] = Field(
        None, description="排序字段查询时使用"
    )
