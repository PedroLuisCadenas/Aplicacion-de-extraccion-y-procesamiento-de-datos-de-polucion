from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import KUNAK_DEVICE_ID
from public_api import router as public_api_router
from influx_reader import (
    query_latest_user_info,
)


app = FastAPI(title="TFG Pollution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(public_api_router)


@app.get("/api/user/info")
def get_latest_user_info():
    return query_latest_user_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
