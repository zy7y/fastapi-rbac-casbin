import contextlib

from starlette.middleware import Middleware
from tortoise.contrib.fastapi import RegisterTortoise

from apps import system
from core.settings import DB_URL

import importlib
import inspect
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from tortoise.models import Model


def find_python_files(directory: Path):
    """
    递归查找目录下的所有 Python 文件，排除 __init__.py 文件。

    :param directory: 要搜索的目录
    """
    for file in directory.iterdir():
        if file.is_dir():
            yield from find_python_files(file)
        elif file.suffix == ".py" and file.name != "__init__.py":
            yield file


def register_routers(app: FastAPI, root_dir: str = "."):
    """
    动态获取当前项目下所有的路由（BaseRoute 实例），支持嵌套目录。

    :param app: FastAPI 应用实例
    :param root_dir: 项目根目录路径
    """
    root_path = Path(root_dir).resolve()

    for python_file in find_python_files(root_path):
        relative_path = python_file.relative_to(root_path)
        module_name = relative_path.with_suffix("").as_posix().replace("/", ".")

        try:
            module = importlib.import_module(module_name)
            routers = [
                obj
                for _, obj in inspect.getmembers(module)
                if isinstance(obj, APIRouter)
            ]
            for router in routers:
                app.include_router(router)
        except Exception as e:
            print(f"无法导入模块 {module_name}: {e}")


def find_models(root_dir: str = "."):
    """
    动态获取当前项目下所有的模型类（TortoiseORM），支持嵌套目录。

    :param root_dir: 项目根目录路径
    """
    models_str = set()
    root_path = Path(root_dir).resolve()

    for python_file in find_python_files(root_path):
        relative_path = python_file.relative_to(root_path)
        module_name = relative_path.with_suffix("").as_posix().replace("/", ".")

        try:
            module = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module):
                if issubclass(obj, Model):
                    if obj._meta.abstract:
                        continue
                    models_str.add(module_name)
        except Exception as e:
            print(f"无法导入模块 {module_name}: {e}")
    return models_str


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    register_routers(app)
    async with RegisterTortoise(
            app,
            db_url=DB_URL,
            modules={"models": ["casbin_tortoise_adapter", *find_models()]},
            generate_schemas=True,
            add_exception_handlers=True,
    ):
        e = await system.init_casbin()
        app.state.enforcer = e
        from apps.system.utils import init_db
        await init_db()
        yield


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
]
