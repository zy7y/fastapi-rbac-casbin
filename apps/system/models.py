from enum import IntEnum
from .schemas import MenuMeta
from core.models import AbstractBaseModel, AbstractUser, fields


class User(AbstractUser):
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role", related_name="users", null=True, description="拥有角色"
    )
    active_role: fields.ForeignKeyRelation["Role"] = fields.ForeignKeyField(
        "models.Role", related_name="active_user", null=True, description="当前角色"
    )


class Role(AbstractBaseModel):
    name = fields.CharField(max_length=32, description="角色名")
    remark = fields.CharField(max_length=128, null=True, description="备注")
    users: fields.ManyToManyRelation[User]
    menus: fields.ManyToManyRelation["Menu"] = fields.ManyToManyField(
        "models.Menu", related_name="roles", null=True, description="拥有菜单"
    )


class MenuType(IntEnum):
    DIRECTORY = 1
    MENU = 2
    BUTTON = 3


class Menu(AbstractBaseModel):
    name = fields.CharField(max_length=32, description="菜单名")
    roles: fields.ManyToManyRelation[Role]
    parent: fields.ForeignKeyRelation["Menu"] = fields.ForeignKeyField(
        "models.Menu", related_name="children", null=True, description="父菜单"
    )
    path = fields.CharField(max_length=128, null=True, description="路由地址")
    component = fields.CharField(max_length=128, null=True, description="组件")
    meta: MenuMeta = fields.JSONField(null=True, description="菜单元数据")
    redirect = fields.CharField(max_length=128, null=True, description="重定向地址")
    children = fields.ReverseRelation["Menu"]
    permission = fields.CharField(max_length=128, null=True, description="权限标识")
    type = fields.IntEnumField(
        MenuType, default=MenuType.DIRECTORY, description="菜单类型"
    )
