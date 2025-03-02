import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from db_data_extractor import DbDataExtractor
from entities import DbData

app = FastAPI()

# Разрешаем CORS для всех запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все домены
    allow_methods=["*"],  # Разрешаем все HTTP-методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app = FastAPI()


@app.get("/")
def read_root():
    return FileResponse('interface/interface.html')


@app.get(
    '/get_data',
    response_model=DbData,
)
def get_data() -> DbData:
    return DbDataExtractor()()


uvicorn.run(app)
