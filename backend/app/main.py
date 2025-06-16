from webbrowser import get
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from app.routes.auth import auth_router
from app.routes.transactions import transactions_router
from app.routes.category import categories_router
from app.routes.export import export_router
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import (
    sqlalchemy_exception_handler,
    database_exception_handler,
    http_exception_handler,
    DatabaseException,
)

app = FastAPI()
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(export_router)
app.mount("/static/exports", StaticFiles(directory="app/static/exports"), name="exports")


app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
