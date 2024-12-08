from apps.system import schemas
from apps.system.models import User, MenuType, Menu
from core.security import get_password_hash


async def init_db():
    if not await User.get_or_none(username="admin"):
        # 1. 创建用户
        await User.create(username="admin",
                          password=get_password_hash("123456"),
                          is_superuser=True)

        # 2. 创建菜单
        root = await Menu.create(
            name="系统管理",
            path="/system",
            component="",
            permission="",
            type=MenuType.DIRECTORY,
            meta=schemas.MenuMeta(
                title="系统管理",
                icon="Management",
            ).model_dump(),
        )
        user = await Menu.create(
            name="用户管理",
            path="/system/user",
            parent=root,
            component="/views/system/user/index.vue",
            permission="",
            type=MenuType.MENU,
            meta=schemas.MenuMeta(
                title="用户管理",
            ).model_dump(),
        )
        role = await Menu.create(
            name="角色管理",
            path="/system/role",
            parent=root,
            component="/views/system/role/index.vue",
            permission="",
            type=MenuType.MENU,
            meta=schemas.MenuMeta(
                title="角色管理",
            ).model_dump(),
        )

        menu = await Menu.create(
            name="菜单管理",
            path="/system/menu",
            parent=root,
            component="/views/system/menu/index.vue",
            permission="",
            type=MenuType.MENU,
            meta=schemas.MenuMeta(
                title="菜单管理",
            ).model_dump(),
        )

        await Menu.create(
            name="用户新增",
            path="",
            parent=user,
            component="",
            permission="user:create",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="用户新增",
            ).model_dump(),
        )
        await Menu.create(
            name="用户删除",
            path="",
            parent=user,
            component="",
            permission="user:delete",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="用户删除",
            ).model_dump(),
        )
        await Menu.create(
            name="用户修改",
            path="",
            parent=user,
            component="",
            permission="user:update",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="用户修改",
            ).model_dump(),
        )
        await Menu.create(
            name="用户查询",
            path="",
            parent=user,
            component="",
            permission="user:query",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="用户查询",
            ).model_dump(),
        )
        await Menu.create(
            name="角色新增",
            path="",
            parent=role,
            component="",
            permission="role:create",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="角色新增",
            ).model_dump(),
        )
        await Menu.create(
            name="角色删除",
            path="",
            parent=role,
            component="",
            permission="role:delete",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="角色删除",
            ).model_dump(),
        )
        await Menu.create(
            name="角色修改",
            path="",
            parent=role,
            component="",
            permission="role:update",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="角色修改",
            ).model_dump(),
        )
        await Menu.create(
            name="角色查询",
            path="",
            parent=role,
            component="",
            permission="role:query",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="角色查询",
            ).model_dump(),
        )
        await Menu.create(
            name="菜单新增",
            path="",
            parent=menu,
            component="",
            permission="menu:create",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="菜单新增",
            ).model_dump(),
        )
        await Menu.create(
            name="菜单删除",
            path="",
            parent=menu,
            component="",
            permission="menu:delete",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="菜单删除",
            ).model_dump(),
        )
        await Menu.create(
            name="菜单修改",
            path="",
            parent=menu,
            component="",
            permission="menu:update",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="菜单修改",
            ).model_dump(),
        )
        await Menu.create(
            name="菜单查询",
            path="",
            parent=menu,
            component="",
            permission="sys:menu:query",
            type=MenuType.BUTTON,
            meta=schemas.MenuMeta(
                title="菜单查询",
            ).model_dump(),
        )

