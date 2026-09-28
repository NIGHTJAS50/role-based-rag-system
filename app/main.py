from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title='Role-Based RAG System')
DOCUMENTS = [('engineering', 'Deploy services through the approved CI pipeline.'), ('finance', 'Invoices require two-person approval.')]
class Query(BaseModel): question: str

def retrieve(question: str, role: str) -> list[str]:
    terms = set(question.lower().split())
    return [text for doc_role, text in DOCUMENTS if doc_role == role and terms.intersection(text.lower().split())]

@app.get('/health')
def health(): return {'status': 'ok'}

@app.post('/query')
def query(payload: Query, x_role: str = Header(default='guest')):
    if x_role not in {'engineering', 'finance'}: raise HTTPException(403, 'Role is not allowed to query protected knowledge')
    sources = retrieve(payload.question, x_role)
    return {'answer': ' '.join(sources) if sources else 'I do not have enough authorized context to answer.', 'sources': sources, 'role': x_role}
