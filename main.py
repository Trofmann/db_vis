from fastapi import FastAPI
from entities import DbData
from db_data_extractor import DbDataExtractor

app = FastAPI()


@app.get(
    '/get_data/',
    response_model=DbData,
)
def get_data() -> DbData:
    return DbDataExtractor()()
