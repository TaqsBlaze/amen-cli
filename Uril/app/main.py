from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Uril")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
async def root():
    return {"message": "Welcome to Uril API!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Uril"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
