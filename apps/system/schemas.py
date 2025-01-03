import re
from enum import StrEnum
from typing import Optional

from fastapi import UploadFile
from pydantic import HttpUrl, field_validator

from core.schemas import (
    BaseModel,
    Field,
    PageResult,
    RequestSchema,
    ResponseSchema,
    Result,
    datetime,
    to_camel,
)


class UploadFilePayload(RequestSchema):
    key: str | None = Field(None)
    file: UploadFile


class UploadFileResult(ResponseSchema):
    url: HttpUrl
    key: str | None = None


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
    last_login: Optional[datetime] = Field(None)
    is_staff: Optional[bool] = Field(None)
    is_superuser: Optional[bool] = Field(None)
    avatar: Optional[str] = Field(None)

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "json_encoders": {datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")},
    }


class Info(User):
    roles: list["Role"] | None = Field(None)
    active_role: Optional["Role"] = Field(None)
    menus: list["MenuTree"] | None = Field(None, description="菜单权限列表")
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
    remark: Optional[str] = Field(None)
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


class Menu(BaseModel):
    id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    parent_id: Optional[int] = Field(None)
    path: Optional[str] = Field(None)
    component: Optional[str] = Field(None)
    meta: Optional["MenuMeta"] = Field(None)
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


class MenuMeta(RequestSchema):
    title: str | None = Field(None, description="菜单标题")
    icon: str | None = Field(None, description="菜单图标")
    show: bool | None = Field(True, description="是否显示")
    link: str | None = Field(None, description="外链地址")


class MenuTree(Menu):
    children: list["MenuTree"] | None = Field(None)


__all__ = ["PageResult", "Result"]
