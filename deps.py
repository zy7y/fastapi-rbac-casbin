"""依赖项、后台权限系统"""
from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from starlette.requests import Request

from models import User
from security import ALGORITHM, SECRET_KEY

bearer = HTTPBearer()


async def jwt_auth(security: HTTPAuthorizationCredentials = Depends(bearer)):
    """检查用户token"""
    token = security.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = await User.get(username=username)
        return user
    except JWTError:
        raise HTTPException(401, "用户认证失败")


async def get_enforcer(request: Request) -> AsyncEnforcer:
    """获取casbin enforcer"""
    return request.app.state.enforcer


async def check_permission(request: Request, user: User = Depends(jwt_auth)):
    """检查用户是否有权限访问"""
    role = await user.active_role.first()
    enforcer = request.app.state.enforcer
    if enforcer.enforce(str(role.id), request.url.path, request.method):
        return user
    raise HTTPException(403, "没有访问权限")
