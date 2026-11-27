import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db
from backend.models import User
from backend.security import hash_password

@pytest.fixture
def client(tmp_path):
    engine = create_engine("sqlite:///"+str(tmp_path/"test.db"), connect_args={"check_same_thread":False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        db.add_all([User(username="admin",password_hash=hash_password("demo-password-123"),role="admin"),
                    User(username="analyst",password_hash=hash_password("demo-password-123"),role="analyst")])
        db.commit()
    def override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()

def login(client,name):
    response=client.post("/api/login",json={"username":name,"password":"demo-password-123"})
    assert response.status_code==200
    return {"Authorization":"Bearer "+response.json()["access_token"]}, response.json()["user"]["id"]

def test_authentication(client):
    assert client.get("/api/cases").status_code==401
    assert client.post("/api/login",json={"username":"admin","password":"wrong"}).status_code==401
    headers,_=login(client,"admin")
    assert client.post("/api/logout",headers=headers).status_code==204
    assert client.get("/api/cases",headers=headers).status_code==401

def test_lifecycle_and_audit(client):
    h,uid=login(client,"admin")
    item=client.post("/api/cases",headers=h,json={"title":"Demo case","owner_id":uid}).json()
    url="/api/cases/"+str(item["id"])
    assert client.patch(url,headers=h,json={"status":"RESOLVED","version":1}).status_code==422
    assert client.patch(url,headers=h,json={"status":"IN_PROGRESS","version":1}).status_code==200
    assert client.patch(url,headers=h,json={"status":"RESOLVED","version":1}).status_code==409
    assert client.patch(url,headers=h,json={"status":"RESOLVED","version":2}).status_code==200
    assert len(client.get(url+"/audit",headers=h).json())==3
    assert client.get("/api/metrics",headers=h).json()["RESOLVED"]==1

def test_permissions(client):
    h,uid=login(client,"admin")
    other,analyst_id=login(client,"analyst")
    item=client.post("/api/cases",headers=h,json={"title":"Private case","owner_id":uid}).json()
    assert client.get("/api/cases",headers=other).json()["total"]==0
    assert client.get("/api/cases/"+str(item["id"])+"/audit",headers=other).status_code==404
    assert client.post("/api/cases",headers=other,json={"title":"Wrong owner","owner_id":uid}).status_code==403
    assert client.post("/api/users",headers=other,json={"username":"new","password":"long-password"}).status_code==403
    assert client.post("/api/cases",headers=other,json={"title":"Own case","owner_id":analyst_id}).status_code==201
    assert client.get("/api/cases?search=Own",headers=other).json()["total"]==1
