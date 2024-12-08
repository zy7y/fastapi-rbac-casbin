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


class AbstractUser(AbstractBaseModel):
    username = fields.CharField(max_length=32, unique=True, description="用户名")
    password = fields.CharField(max_length=128, description="密码")
    avatar = fields.CharField(max_length=128, null=True, description="头像", default="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif?imageView2/1/w/80/h/80")
    is_superuser = fields.BooleanField(default=False, description="是否是超级管理员")
    last_login = fields.DatetimeField(null=True, description="上次登录时间")
    is_staff = fields.BooleanField(default=False, description="是否是管理员")

    class Meta:
        abstract = True
