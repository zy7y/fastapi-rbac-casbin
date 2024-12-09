from fastapi import FastAPI

from core.register import lifespan, middleware

app = FastAPI(lifespan=lifespan, middleware=middleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", reload=True)
