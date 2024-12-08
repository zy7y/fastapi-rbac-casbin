"""依赖项、后台权限系统"""

import os.path

import casbin_tortoise_adapter
from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from starlette.requests import Request

from apps.system.models import User
from core.settings import ALGORITHM, SECRET_KEY


async def init_casbin() -> AsyncEnforcer:
    adapter = casbin_tortoise_adapter.TortoiseAdapter()
    model_file = os.path.join(os.path.dirname(__file__), "model.conf")

    e = AsyncEnforcer(model_file, adapter)
    await e.load_policy()
    return e


async def jwt_auth(security: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """检查用户token"""
    token = security.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = await User.get(username=username)
        return user
    except JWTError:
        raise HTTPException(401, "用户认证失败")


async def check_permission(request: Request, user: User = Depends(jwt_auth)):
    """检查用户是否有权限访问"""
    if user.is_superuser:
        return user
    if not user.is_staff:
        raise HTTPException(401, "账号无法登录后台")
    role = await user.active_role.first() if user.active_role else None
    if role is None:
        raise HTTPException(401, "用户未激活角色")
    enforcer = request.app.state.enforcer
    if enforcer.enforce(str(role.id), request.url.path, request.method):
        return user
    raise HTTPException(403, "没有访问权限")
