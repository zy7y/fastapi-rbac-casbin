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
    is_superuser = fields.BooleanField(default=False, description="是否是超级管理员")

    class Meta:
        abstract = True
