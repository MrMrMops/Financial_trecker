from webbrowser import get
from fastapi import FastAPI



app = FastAPI()

@app.get('/')
async def test():
    return{'text':'hello'}
