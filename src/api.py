import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.workflow import handle_error, on_fetch

app = FastAPI()


@app.get("/")
async def webhook(request: Request):
    try:
        result = await on_fetch(request)
        return JSONResponse(content=result)
    except Exception as e:
        return handle_error(e)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
