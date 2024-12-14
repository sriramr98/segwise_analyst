from typing import Any
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from sqlalchemy import Column
from sqlalchemy.orm import Session, Query as SqlQuery, load_only
import pandas as pd
from datetime import date, datetime
import json
import os

from starlette.responses import JSONResponse

from database import SessionLocal, create_tables, GameData, getNameToColumnMap
from models import Filter, UploadCsvRequest, Condition, ExploreDataRequest

app = FastAPI(title="Game Analytics Data Explorer")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def passwordHasher(input):
    return input

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    password = request.headers.get('password')
    if passwordHasher(password) != os.getenv("ADMIN_PASSWORD_HASH"):
        return JSONResponse({ 'error': 'UnAuthorized' }, 401, {"WWW-Authenticate": "Basic"})
    response = await call_next(request)
    return response


@app.on_event("startup")
def startup():
    create_tables()


def fixBadData(df: pd.DataFrame) -> None:
    df.fillna({ 'Name': '', 'Required age': 0, 'Price': 0, 'DLC count': 0, 'About the game': '', 'Supported languages': '', 'Windows': False, 'Mac': False, 'Linux': False, 'Positive': 0, 'Negative': 0, 'Score rank': 0, 'Developers': '', 'Publishers': '', 'Categories': '', 'Genres': '', 'Tags': ''}, inplace=True)

def parseDate(input):
    try:
        return datetime.strptime(input, "%b %d, %Y").date()
    except:
        # it is possible that sometimes there's no date in the input
        return datetime.strptime(input, "%b %Y").date()

def csvToList(input) -> list[str]:
    return input.split(",")

@app.post("/upload-csv/")
async def upload_csv(body: UploadCsvRequest, db: Session = Depends(get_db)):
    try:
        # Read CSV
        df = pd.read_csv(body.csv_link, parse_dates=['Release date'])
        fixBadData(df)
        
        # Prepare data for bulk insert
        records = df.to_dict('records')
        
        # Clear existing data
        db.query(GameData).delete()
        
        # Bulk insert
        db_records = [
            GameData(
                app_id=record.get('AppID'),
                name=record.get('Name'),
                release_date=parseDate(record.get('Release date')),
                required_age=record.get('Required age'),
                price=record.get('Price'),
                dlc_count=record.get('DLC count'),
                about_the_game=record.get('About the game'),
                supported_languages=json.loads(str(record.get('Supported languages')).replace("'", '"')),
                windows=record.get('Windows'),
                mac=record.get('Mac'),
                linux=record.get('Linux'),
                positive_reviews=record.get('Positive'),
                negative_reviews=record.get('Negative'),
                score_rank=record.get('Score rank'),
                developers=record.get('Developers'),
                publishers=record.get('Publishers'),
                categories=csvToList(record.get('Categories')),
                genres=csvToList(record.get('Genres')),
                tags=csvToList(record.get('Tags'))
            )
            for record in records
        ]
        
        db.bulk_save_objects(db_records)
        db.commit()
        
        return {"message": f"Uploaded {len(records)} records successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def applyFilter(query: SqlQuery[GameData], filter: Filter, col_name_map: dict[str, Column]):
    column = col_name_map.get(filter.column)
    if column is None:
        raise HTTPException(400, f'Unknown column {filter.column}')
    print(column, filter, column.type.python_type)
    if filter.condition == Condition.EQ:
        if column.type.python_type is str:
            condition = f'%{filter.value}%'
            return query.filter(column.ilike(condition))
        elif column.type.python_type is list:
            return query.filter(column.contains([filter.value]))

        value = parseDate(filter.value) if column.type.python_type is date else filter.value
        return query.filter(col_name_map[filter.column] == value)
    elif filter.condition == Condition.LT:
        if column.type.python_type in [str, bool, list]:
            raise HTTPException(400, f'Invalid filter operation ({filter.condition}) for column ({filter.column}) of type {column.type.python_type}')
        value = parseDate(filter.value) if column.type.python_type is date else filter.value
        return query.filter(column < value)
    elif filter.condition == Condition.GT:
        if column.type.python_type in [str, bool, list]:
            raise HTTPException(400, f'Invalid filter operation ({filter.condition}) for column ({filter.column}) of type {column.type.python_type}')
        value = parseDate(filter.value) if column.type.python_type is date else filter.value
        return query.filter(column > value)
    elif filter.condition == Condition.GTE:
        if column.type.python_type in [str, bool, list]:
            raise HTTPException(400, f'Invalid filter operation ({filter.condition}) for column ({filter.column}) of type {column.type.python_type}')
        value = parseDate(filter.value) if column.type.python_type is date else filter.value
        return query.filter(column >= value)
    elif filter.condition == Condition.LTE:
        if column.type.python_type in [str, bool, list]:
            raise HTTPException(400, f'Invalid filter operation ({filter.condition}) for column ({filter.column}) of type {column.type.python_type}')
        value = parseDate(filter.value) if column.type.python_type is date else filter.value
        return query.filter(column <= value)
    else:
        raise HTTPException(400, f'Invalid filter operation {filter.condition}')

@app.get("/explore/")
def explore_data(
    body: ExploreDataRequest,
    db: Session = Depends(get_db)
):
    query = db.query(GameData)

    col_name_map = getNameToColumnMap()
    for filter in body.filters:
        query = applyFilter(query, filter, col_name_map)

   
    total_count = query.count()
    results = query.all()
    
    return {
        "total_count": total_count,
        "results": results
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
