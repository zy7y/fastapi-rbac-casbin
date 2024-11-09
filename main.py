import contextlib
import importlib
import inspect
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute
from tortoise.contrib.fastapi import register_tortoise
from casbin import AsyncEnforcer
import casbin_tortoise_adapter


def get_all_routes(root_dir: str) -> list[BaseRoute]:
    """
    动态获取当前项目下所有的路由（BaseRoute 实例），支持嵌套目录。

    :param root_dir: 项目根目录路径
    :return: 包含所有 BaseRoute 对象的列表
    """
    routes = []

    # 获取项目根目录下的所有 Python 文件（递归）
    def find_python_files(directory: Path):
        for file in directory.iterdir():
            if file.is_dir():
                yield from find_python_files(file)
            elif file.suffix == ".py" and file.name != "__init__.py":
                yield file

    # 动态导入模块并查找路由
    def import_and_find_routes(module_path: Path):
        relative_path = module_path.relative_to(root_dir)
        module_name = relative_path.with_suffix("").as_posix().replace("/", ".")

        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, APIRouter):
                    # 获取 APIRouter 中的所有 BaseRoute 对象
                    routes.extend(obj.routes)
        except Exception as e:
            print(f"无法导入模块 {module_name}: {e}")

    # 遍历根目录，查找所有 Python 文件并导入
    for python_file in find_python_files(Path(root_dir)):
        import_and_find_routes(python_file)

    return routes


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    adapter = casbin_tortoise_adapter.TortoiseAdapter()
    e = AsyncEnforcer("model.conf", adapter)
    await e.load_policy()
    app.state.enforcer = e

    exclude_path = ["/docs", "/openapi.json", "/redoc", "/docs/oauth2-redirect"]
    from schemas import Route, PageResult

    data = list()
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path in exclude_path:
            continue
        for method in route.methods:
            data.append(Route(**route.__dict__, method=method))

    total = len(data)
    app.add_api_route(
        "/routes",
        summary="获取路由列表",
        tags=["权限相关"],
        response_model=PageResult[Route],
        endpoint=lambda: PageResult.ok(total=total, data=data),
    )

    yield


app = FastAPI(lifespan=lifespan, routes=get_all_routes("."))

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models", "casbin_tortoise_adapter"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", reload=True)
