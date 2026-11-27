from fastapi.testclient import TestClient
from app import app

def test_case_lifecycle(tmp_path,monkeypatch):
    monkeypatch.setenv("CASEFLOW_DB",str(tmp_path/"test.db"))
    c=TestClient(app)
    assert c.get("/health").json()=={"status":"ok"}
    assert c.get("/api/cases").json()==[]
    r=c.post("/api/cases",json={"title":"Demo incident","owner":"Demo user","priority":"HIGH"})
    assert r.status_code==201
    cid=r.json()["id"]
    assert r.json()["status"]=="OPEN"
    assert c.patch(f"/api/cases/{cid}",json={"status":"RESOLVED"}).json()["status"]=="RESOLVED"
    assert c.get("/api/cases").json()[0]["status"]=="RESOLVED"
    assert c.patch("/api/cases/999",json={"status":"OPEN"}).status_code==404
    assert c.post("/api/cases",json={"title":"x","owner":"Demo"}).status_code==422
