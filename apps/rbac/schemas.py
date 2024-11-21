import re
from enum import StrEnum
from typing import Optional

from pydantic import field_validator
from core.schemas import (
    RequestSchema,
    ResponseSchema,
    Field,
    BaseModel,
    to_camel,
    datetime,
    PageResult,
    Result,
)


class Login(RequestSchema):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Route(RequestSchema):
    """接口"""

    path: str = Field(..., description="路由地址")
    name: str = Field(..., description="路由名称")
    method: str = Field(..., description="请求方法")
    summary: str | None = Field(None, description="路由描述")
    tags: list[str] | None = Field(None, description="路由分组")

    @field_validator("path")
    @classmethod
    def path_validator(cls, v):
        return re.sub(r"\{.*?\}", ":id", v)


class Token(ResponseSchema):
    """登录成功返回token"""

    token: str


class AssignRole(RequestSchema):
    """分配角色"""

    role_ids: list[int] = Field(..., description="角色ID列表")
    user_id: int = Field(..., description="用户ID")


class AssignMenu(RequestSchema):
    """分配菜单"""

    menu_ids: list[int] = Field(..., description="菜单ID列表")
    role_id: int = Field(..., description="角色ID")


class AssignRoute(RequestSchema):
    """分配接口"""

    routes: list[Route] = Field(..., description="接口列表")
    role_id: int = Field(..., description="角色ID")


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
    is_superuser: Optional[bool] = Field(None)

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class MenuTree(BaseModel):
    id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    children: list["MenuTree"] | None = Field(None)
    path: Optional[str] = Field(None)
    component: Optional[str] = Field(None)
    meta: Optional[dict] = Field(None)
    redirect: Optional[str] = Field(None)
    permission: Optional[str] = Field(None)
    type: Optional[int] = Field(None)


""" 当前登录用户 信息获取"""


class Info(User):
    password: str = Field(..., exclude=True)
    roles: list["Role"] | None = Field(None, description="角色列表")
    active_role: Optional["Role"] = Field(None, description="当前激活角色")
    menus: list[MenuTree] | None = Field(None, description="菜单树")
    permissions: list[str] | None = Field(None, description="按钮权限列表")


class UserQueryParams(User):
    page_number: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    order_by: Optional[list[UserFieldEnum]] = Field(
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
    order_by: Optional[list[RoleFieldEnum]] = Field(
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


class MenuMeta(BaseModel):
    title: str
    icon: Optional[str] = Field(None)
    is_hide: Optional[bool] = Field(False)


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
    order_by: Optional[list[MenuFieldEnum]] = Field(
        None, description="排序字段查询时使用"
    )


__all__ = ["PageResult", "Result"]
