from fastapi import FastAPI
from utils.register import lifespan

app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", reload=True)
