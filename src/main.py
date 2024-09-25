import uvicorn
from fastapi import FastAPI

from src.api import router

app = FastAPI(docs_url='/api/docs')
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
