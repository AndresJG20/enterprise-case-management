import os, sqlite3
from pathlib import Path
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(title="CaseFlow", version="0.1.0")
Status = Literal["OPEN","IN_PROGRESS","RESOLVED"]
Priority = Literal["LOW","MEDIUM","HIGH"]

@contextmanager
def db():
    con = sqlite3.connect(os.getenv("CASEFLOW_DB","caseflow.db"))
    con.row_factory = sqlite3.Row
    try:
        with con:
            con.execute("CREATE TABLE IF NOT EXISTS cases (id INTEGER PRIMARY KEY, title TEXT NOT NULL, owner TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            yield con
    finally:
        con.close()

class CaseInput(BaseModel):
    title: str = Field(min_length=3,max_length=160)
    owner: str = Field(min_length=1,max_length=80)
    priority: Priority = "MEDIUM"

class Update(BaseModel):
    status: Status

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).with_name("index.html"))

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/api/cases")
def cases():
    with db() as con:
        return [dict(r) for r in con.execute("SELECT * FROM cases ORDER BY id DESC")]

@app.post("/api/cases",status_code=201)
def create(case: CaseInput):
    with db() as con:
        cursor=con.execute("INSERT INTO cases(title,owner,priority,status) VALUES(?,?,?,'OPEN')",(case.title,case.owner,case.priority))
        return dict(con.execute("SELECT * FROM cases WHERE id=?",(cursor.lastrowid,)).fetchone())

@app.patch("/api/cases/{cid}")
def update(cid:int, payload:Update):
    with db() as con:
        if not con.execute("UPDATE cases SET status=? WHERE id=?",(payload.status,cid)).rowcount:
            raise HTTPException(404,"Case not found")
        return dict(con.execute("SELECT * FROM cases WHERE id=?",(cid,)).fetchone())
