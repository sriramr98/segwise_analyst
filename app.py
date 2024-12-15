from dotenv import load_dotenv

from authorizer import verify_password
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
import pandas as pd
import json

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from database import SessionLocal, create_tables, GameData, getNameToColumnMap
from models import UploadCsvRequest, ExploreDataRequest
from utils import getAggregateFilter, getAggregateFunc, getFilter, parseDate, hashString


app = FastAPI(title="Game Analytics Data Explorer")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    create_tables()


def fixBadData(df: pd.DataFrame) -> None:
    df.fillna({ 'Name': '', 'Required age': 0, 'Price': 0, 'DLC count': 0, 'About the game': '', 'Supported languages': '', 'Windows': False, 'Mac': False, 'Linux': False, 'Positive': 0, 'Negative': 0, 'Score rank': 0, 'Developers': '', 'Publishers': '', 'Categories': '', 'Genres': '', 'Tags': ''}, inplace=True)


def csvToList(input) -> list[str]:
    return input.split(",")

@app.post("/upload-csv/")
async def upload_csv(body: UploadCsvRequest, db: Session = Depends(get_db), _ = Depends(verify_password)):
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

@app.get("/explore/")
def explore_data(
    body: ExploreDataRequest,
    db: Session = Depends(get_db),
    _ = Depends(verify_password)
):
    has_aggregations = len(body.aggregations) > 0
    if has_aggregations and len(body.group_bys) == 0:
        raise HTTPException(400, "Group by is required for any aggregation")

    if len(body.group_bys) > 0 and not has_aggregations:
        raise HTTPException(400, "Aggregations are required for group by")

    col_name_map = getNameToColumnMap()
    select_cols: list[str] = []
    
    filters: list[str] = [ getFilter(filter, col_name_map) for filter in body.filters ]

    group_bys: list[str] = []
    for group_by in body.group_bys:
        column = col_name_map.get(group_by)
        if column is None:
            raise HTTPException(400, f"Unknown column {group_by}")
        select_cols.append(column.name)
        group_bys.append(column.name)


    having_filters: list[str] = []

    for aggregate in body.aggregations:
        aggregate_clause = getAggregateFunc(aggregate, col_name_map)
        select_cols.append(aggregate_clause)
        if aggregate.filter:
            having_filters.append(getAggregateFilter(aggregate, col_name_map))

    query = f"SELECT {','.join(select_cols) if len(select_cols)> 0 else '*'} FROM {GameData.__tablename__}"
    if len(filters) > 0:
        query += f" WHERE {' AND '.join(filters)}"

    if len(group_bys) > 0:
        query += f" GROUP BY {','.join(group_bys)}"

    if len(having_filters) > 0:
        query += f" HAVING {' AND '.join(having_filters)}"

    print(query)
        
    with db.connection() as conn:
        result = conn.execute(text(query))
        result = result.mappings().all()

    return {
        "results": result
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
