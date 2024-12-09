import os.path
import time
from datetime import datetime
from typing import Annotated


from fastapi import APIRouter, Depends, Form, Query
from starlette.requests import Request
from tortoise.transactions import atomic

import apps.system.deps as deps
import apps.system.models as model
import apps.system.schemas as schema
from core import security
from core.settings import DISK_PATH

auth = APIRouter(prefix="", tags=["Auth"])


@auth.get(
    "/routes", summary="获取路由列表", response_model=schema.PageResult[schema.Route]
)
def get_routes(request: Request):
    data = []
    for route in request.app.routes:
        for method in route.methods:
            obj = schema.Route(**route.__dict__, method=method)
            data.append(obj)
    return schema.PageResult.ok(data, total=len(data))




@auth.post(
    "/upload", summary="上传文件", response_model=schema.UploadFileResult
)
async def upload(
    request: Request,
    payload: Annotated[
        schema.UploadFilePayload, Form(media_type="multipart/form-data")
    ],
):
    if not payload.key:
        payload.key = f"{int(time.time())}.{payload.file.filename.split('.')[1]}"
    os.makedirs(os.path.join(DISK_PATH, *payload.key.split("/")[:-1]), exist_ok=True)
    with open(os.path.join(DISK_PATH, payload.key), "wb") as buffer:
        content = await payload.file.read()
        buffer.write(content)
    url = f"{request.base_url}/{DISK_PATH}/{payload.key}"
    return dict(url=url, key=payload.key)


@auth.post("/login", response_model=schema.Result[schema.Token])
async def login(payload: schema.Login):
    if obj := await model.User.get_or_none(username=payload.username):
        if security.verify_password(payload.password, obj.password):
            token = security.generate_token(obj.username)
            obj.last_login = datetime.now()
            await obj.save()
            return schema.Result.ok(schema.Token(token=token))
    return schema.Result.error("用户名或密码错误")


def list2tree(
    arr: list, parent_name: str = "parent_id", children_name: str = "children"
):
    """
    列表转嵌套树
    :param arr: 传入的list
    :param parent_name: 关系的key名
    :param children_name: 嵌套数据使用的key名
    :return:
    """
    # 1. 将列表转换成字典，列表中元素的唯一标识作为key，列表元素作为value
    menu_map = {item["id"]: item for item in arr}

    tree = []
    for item in arr:
        if item.get(parent_name) is None:
            # 根节点
            tree.append(item)
        else:
            menu_item = menu_map.get(item[parent_name])
            # 子节点
            if menu_item.get(children_name) is None:
                menu_item[children_name] = []
            menu_item[children_name].append(item)
    return tree


@auth.get("/me", response_model=schema.Result[schema.Info])
async def info(obj: model.User = Depends(deps.jwt_auth)):
    obj = await model.User.get(id=obj.id).prefetch_related("roles", "active_role")
    if not obj.is_superuser:
        if role := await obj.active_role.first():
            result = await role.prefetch_related("menus").values()
    else:
        result = await model.Menu.filter().all().values()
    # 过滤出 按钮权限
    permissions = [item["permission"] for item in result if item["type"] == 3]
    menus = [item for item in result if item["type"] != 3]
    # menus 转 tree
    setattr(obj, "menus", list2tree(menus))
    setattr(obj, "permissions", permissions)

    return schema.Result.ok(obj)


user = APIRouter(
    prefix="/User", tags=["User"], dependencies=[Depends(deps.check_permission)]
)


@user.patch("/reset_passwd/{id}", summary="重置密码, 123456")
async def reset_passwd(id: int) -> schema.Result[schema.User]:
    obj = await model.User.get_or_none(id=id)
    if obj:
        obj.password = security.get_password_hash("123456")
        await obj.save()
        return schema.Result.ok()
    return schema.Result.error("更新失败")


@user.post("/assign/role", summary="分配角色", tags=["权限相关"])
@atomic()
async def assign_role(payload: schema.AssignRole) -> schema.Result:
    obj = await model.User.get_or_none(id=payload.user_id)
    if not obj:
        return schema.Result.error("用户不存在")

    # 检查所有角色是否存在
    existing_roles = await model.Role.filter(id__in=payload.role_ids).all()
    if len(existing_roles) != len(payload.role_ids):
        return schema.Result.error("部分角色不存在")
    # 删除角色
    await obj.roles.clear()
    # 批量添加角色
    await obj.roles.add(*existing_roles)

    return schema.Result.ok()


@user.get("/{id}", summary="通过ID查询详情")
async def query_user_by_id(id: int) -> schema.Result[schema.User]:
    obj = await model.User.get_or_none(id=id)
    return schema.Result.ok(obj)


@user.get("", summary="分页条件查询")
async def query_user_all_by_limit(
    query: schema.UserQueryParams = Query(),
) -> schema.PageResult[schema.User]:
    kwargs = query.model_dump(exclude_none=True)
    if kwargs.get("order_by"):
        order_by = kwargs.pop("order_by")
    else:
        order_by = []
    page_number = kwargs.pop("page_number")
    page_size = kwargs.pop("page_size")

    total = await model.User.filter(**kwargs).count()
    offset = (page_number - 1) * page_size

    data = (
        await model.User.filter(**kwargs)
        .offset(offset)
        .limit(page_size)
        .all()
        .order_by(*order_by)
    )
    return schema.PageResult.ok(data=data, total=total)


@user.post("", summary="新增数据")
async def create_user(instance: schema.User) -> schema.Result[schema.User]:
    instance.password = security.get_password_hash("123456")
    obj = await model.User.create(
        **instance.model_dump(
            exclude_unset=True,
            exclude={
                "id",
            },
        )
    )
    return schema.Result.ok(obj)


@user.patch("/{id}", summary="更新数据")
async def update_user_by_id(
    id: int, instance: schema.User
) -> schema.Result[schema.User]:
    obj = await model.User.get_or_none(id=id)
    if obj:
        for field, value in instance.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
        return schema.Result.ok(obj)
    return schema.Result.error("更新失败")


@user.delete("/{id}", summary="删除数据")
async def delete_user_by_id(id: int) -> schema.Result[schema.User]:
    obj = await model.User.get_or_none(id=id)
    if obj:
        await obj.delete()
        return schema.Result.ok(obj)
    return schema.Result.error("删除失败")


role = APIRouter(
    prefix="/Role", tags=["Role"], dependencies=[Depends(deps.check_permission)]
)


@role.post("/assign/menu", summary="分配菜单(权限)", tags=["权限相关"])
@atomic()
async def assign_menu(payload: schema.AssignMenu) -> schema.Result:
    obj = await model.Role.get_or_none(id=payload.role_id)
    if not obj:
        return schema.Result.error("角色不存在")

    existing_menus = await model.Menu.filter(id__in=payload.menu_ids).all()
    if len(existing_menus) != len(payload.menu_ids):
        return schema.Result.error("部分菜单不存在")
    await obj.menus.clear()
    # 批量添加角色
    await obj.menus.add(*existing_menus)

    return schema.Result.ok()


@role.get("/{id}", summary="通过ID查询详情")
async def query_role_by_id(id: int) -> schema.Result[schema.Role]:
    obj = await model.Role.get_or_none(id=id)
    return schema.Result.ok(obj)


@role.get("", summary="分页条件查询")
async def query_role_all_by_limit(
    query: schema.RoleQueryParams = Query(),
) -> schema.PageResult[schema.Role]:
    kwargs = query.model_dump(exclude_none=True)
    if kwargs.get("order_by"):
        order_by = kwargs.pop("order_by")
    else:
        order_by = []
    page_number = kwargs.pop("page_number")
    page_size = kwargs.pop("page_size")

    total = await model.Role.filter(**kwargs).count()
    offset = (page_number - 1) * page_size

    data = (
        await model.Role.filter(**kwargs)
        .offset(offset)
        .limit(page_size)
        .all()
        .order_by(*order_by)
    )
    return schema.PageResult.ok(data=data, total=total)


@role.post("", summary="新增数据")
async def create_role(instance: schema.Role) -> schema.Result[schema.Role]:
    print(instance, "GGG")
    obj = await model.Role.create(**instance.model_dump(exclude_unset=True))
    return schema.Result.ok(obj)


@role.patch("/{id}", summary="更新数据")
async def update_role_by_id(
    id: int, instance: schema.Role
) -> schema.Result[schema.Role]:
    obj = await model.Role.get_or_none(id=id)
    if obj:
        for field, value in instance.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
        return schema.Result.ok(obj)
    return schema.Result.error("更新失败")


@role.delete("/{id}", summary="删除数据")
async def delete_role_by_id(id: int) -> schema.Result[schema.Role]:
    obj = await model.Role.get_or_none(id=id)
    if obj:
        await obj.delete()
        return schema.Result.ok(obj)
    return schema.Result.error("删除失败")


menu = APIRouter(prefix="/Menu", tags=["Menu"])


@menu.get("/{id}", summary="通过ID查询详情")
async def query_menu_by_id(id: int) -> schema.Result[schema.Menu]:
    obj = await model.Menu.get_or_none(id=id)
    return schema.Result.ok(obj)


@menu.get("", summary="分页条件查询 -> 返回树结构")
async def query_menu_all_by_limit() -> schema.PageResult[schema.MenuTree]:
    total = await model.Menu.all().count()
    data = await model.Menu.all().order_by("-created_at").values()
    return schema.PageResult.ok(list2tree(data), total=total)


@menu.post("", summary="新增数据")
async def create_menu(instance: schema.Menu) -> schema.Result[schema.Menu]:
    if instance.parent_id == 0:
        instance.parent_id = None
    obj = await model.Menu.create(**instance.model_dump(exclude_unset=True))
    return schema.Result.ok(obj)


@menu.patch("/{id}", summary="更新数据")
async def update_menu_by_id(
    id: int, instance: schema.Menu
) -> schema.Result[schema.Menu]:
    obj = await model.Menu.get_or_none(id=id)
    if obj:
        if instance.parent_id == 0:
            instance.parent_id = None
        for field, value in instance.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await obj.save()
        return schema.Result.ok(obj)
    return schema.Result.error("更新失败")


@menu.delete("/{id}", summary="删除数据")
async def delete_menu_by_id(id: int) -> schema.Result[schema.Menu]:
    obj = await model.Menu.get_or_none(id=id)
    if obj:
        await obj.delete()
        return schema.Result.ok(obj)
    return schema.Result.error("删除失败")


@role.post("/assign/route", summary="分配接口(权限)", tags=["权限相关"])
@atomic()
async def assign_route(request: Request, payload: schema.AssignRoute) -> schema.Result:
    obj = await model.Role.get_or_none(id=payload.role_id)
    if not obj:
        return schema.Result.error("角色不存在")
    valid_routes = {route.path: route.method for route in request.app.routes}

    # 使用集合存储待添加的策略
    policies_to_add = set()

    # 收集策略
    for route in payload.routes:
        if route.path in valid_routes and route.method == valid_routes[route.path]:
            policy = (str(payload.role_id), route.path, route.method)
            policies_to_add.add(policy)
        else:
            return schema.Result.error("无效的路径或方法")

    # 一次性批量添加所有策略
    if policies_to_add:
        enforcer = request.app.state.enforcer
        await enforcer.remove_filtered_policy(0, str(payload.role_id))
        await enforcer.add_policies(list(policies_to_add))
    return schema.Result.ok()
