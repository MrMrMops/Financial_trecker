from webbrowser import get
from fastapi import FastAPI
from app.routes.auth import auth_router
from app.routes.transactions import transactions_router
from app.routes.category import categories_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)

@app.get('/')
async def test():
    return{'text':'hello'}
