from webbrowser import get
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.auth import auth_router
from app.routes.transactions import transactions_router
from app.routes.category import categories_router
from app.routes.export import export_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(export_router)
app.mount("/static/exports", StaticFiles(directory="app/static/exports"), name="exports")


@app.get('/')
async def test():
    return{'text':'hello'}
