from fastapi import FastAPI
from routes.text_routes import router as text_router

app = FastAPI(title="ChefAI Recipe API")

# Register routes
app.include_router(text_router)

@app.get("/")
def home():
    return {"message": "ChefAI backend running"}