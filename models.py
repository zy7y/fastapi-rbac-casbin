from enum import IntEnum

from tortoise import models, fields


class AbstractBaseModel(models.Model):
    """
    抽象模型，所有模型都继承自该模型
    """

    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True


class User(AbstractBaseModel):
    username = fields.CharField(max_length=32, unique=True, description="用户名")
    password = fields.CharField(max_length=128, description="密码")
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role", related_name="users", null=True, description="拥有角色"
    )
    active_role: fields.ForeignKeyRelation["Role"] = fields.ForeignKeyField(
        "models.Role", related_name="active_user", null=True, description="当前角色"
    )


class Role(AbstractBaseModel):
    name = fields.CharField(max_length=32, description="角色名")
    users: fields.ManyToManyRelation[User]
    menus: fields.ManyToManyRelation["Menu"] = fields.ManyToManyField(
        "models.Menu", related_name="roles", null=True, description="拥有菜单"
    )


class MenuType(IntEnum):
    DIRECTORY = 1
    MENU = 2
    BUTTON = 3
    EXTERNAL_LINK = 4


class Menu(AbstractBaseModel):
    name = fields.CharField(max_length=32, description="菜单名")
    roles: fields.ManyToManyRelation[Role]
    parent: fields.ForeignKeyRelation["Menu"] = fields.ForeignKeyField(
        "models.Menu", related_name="children", null=True, description="父菜单"
    )
    path = fields.CharField(max_length=128, null=True, description="路由地址")
    component = fields.CharField(max_length=128, null=True, description="组件")
    meta = fields.JSONField(null=True, description="菜单元数据")
    children = fields.ReverseRelation["Menu"]
    redirect = fields.CharField(max_length=128, null=True, description="重定向地址")
    permission = fields.CharField(max_length=128, null=True, description="权限标识")
    type = fields.IntEnumField(
        MenuType, default=MenuType.DIRECTORY, description="菜单类型"
    )
