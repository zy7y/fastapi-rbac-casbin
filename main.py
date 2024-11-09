import contextlib
import importlib
import inspect
from pathlib import Path

from fastapi import FastAPI, APIRouter
from tortoise.contrib.fastapi import register_tortoise

import rbac


def register_routers(app: FastAPI, root_dir: str = "."):
    """
    动态获取当前项目下所有的路由（BaseRoute 实例），支持嵌套目录。

    :param app:
    :param root_dir: 项目根目录路径
    """

    # 获取项目根目录下的所有 Python 文件（递归）
    def find_python_files(directory: Path):
        for file in directory.iterdir():
            if file.is_dir():
                yield from find_python_files(file)
            elif file.suffix == ".py" and file.name != "__init__.py":
                yield file

    # 动态导入模块并查找路由
    def import_and_include_routers(module_path: Path):
        relative_path = module_path.relative_to(root_dir)
        module_name = relative_path.with_suffix("").as_posix().replace("/", ".")

        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, APIRouter):
                    app.include_router(obj)
        except Exception as e:
            print(f"无法导入模块 {module_name}: {e}")

    # 遍历根目录，查找所有 Python 文件并导入
    for python_file in find_python_files(Path(root_dir)):
        import_and_include_routers(python_file)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    e = await rbac.init_casbin()
    app.state.enforcer = e
    register_routers(app)
    yield


app = FastAPI(lifespan=lifespan)

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["rbac.models", "casbin_tortoise_adapter"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", reload=True)
