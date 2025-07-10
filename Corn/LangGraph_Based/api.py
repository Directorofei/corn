from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from Graph import build_graph
from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str
    image_path: str | None = None

class AskResponse(BaseModel):
    answer: str | None
    detection_result: str | None
    decision: str | None

class MedicationRequest(BaseModel):
    question: str
    image_path: str | None = None

class MedicationResponse(BaseModel):
    decision: str | None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_app = build_graph()

@app.post("/api/ask", response_model=AskResponse)
async def ask(data: AskRequest):
    state = {
        "question": data.question,
        "image_path": data.image_path,
        "image_description": None,
        "detection_result": None,
        "answer": None,
        "need_medication": None,
        "decision": None
    }
    result = graph_app.invoke(state)
    return AskResponse(
        answer=result.get("answer"),
        detection_result=result.get("detection_result"),
        decision=result.get("decision")
    )

@app.post("/api/medication", response_model=MedicationResponse)
async def medication(data: MedicationRequest):
    result = data.dict()
    result["need_medication"] = True
    result = graph_app.invoke(result)
    return MedicationResponse(
        decision=result.get("decision")
    )

@app.get("/")
def read_root():
    return {"msg": "后端已连接成功"}