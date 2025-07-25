from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()

class Clan(Base):
    __tablename__ = "clans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    region = Column(String)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

Base.metadata.create_all(bind=engine)

class ClanCreate(BaseModel):
    name: str
    region: str | None = None

@app.post("/clans")
def create_clan(clan: ClanCreate):
    db = SessionLocal()
    new_clan = Clan(name=clan.name, region=clan.region)
    db.add(new_clan)
    db.commit()
    db.refresh(new_clan)
    return {"id": str(new_clan.id), "message": "Clan created successfully."}

@app.get("/clans")
def list_clans(region: str | None = None, sort_by: str = "created_at"):
    db = SessionLocal()
    query = db.query(Clan)
    if region:
        query = query.filter(Clan.region == region)
    if sort_by == "created_at":
        query = query.order_by(Clan.created_at)
    return [clan.__dict__ for clan in query.all()]

@app.get("/clans/{clan_id}")
def get_clan(clan_id: str):
    db = SessionLocal()
    clan = db.query(Clan).get(clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found.")
    return clan.__dict__

@app.delete("/clans/{clan_id}")
def delete_clan(clan_id: str):
    db = SessionLocal()
    clan = db.query(Clan).get(clan_id)
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found.")
    db.delete(clan)
    db.commit()
    return {"message": "Clan deleted successfully."}
