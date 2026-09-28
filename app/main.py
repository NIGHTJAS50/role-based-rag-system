from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from functools import lru_cache

app = FastAPI(title='Role-Based RAG System')
DOCUMENTS = [('engineering', 'Deploy services through the approved CI pipeline.'), ('finance', 'Invoices require two-person approval.')]
class Query(BaseModel): question: str

@lru_cache(maxsize=2)
def collection(role: str):
    import chromadb
    from langchain_core.documents import Document
    client = chromadb.Client()
    store = client.get_or_create_collection(f'knowledge-{role}')
    docs = [Document(page_content=text, metadata={'role': doc_role}) for doc_role, text in DOCUMENTS if doc_role == role]
    if docs and not store.count():
        store.add(ids=[f'{role}-{i}' for i in range(len(docs))], documents=[doc.page_content for doc in docs], metadatas=[doc.metadata for doc in docs])
    return store

def retrieve(question: str, role: str) -> list[str]:
    result = collection(role).query(query_texts=[question], n_results=2)
    return result.get('documents', [[]])[0]

@app.get('/health')
def health(): return {'status': 'ok'}

@app.post('/query')
def query(payload: Query, x_role: str = Header(default='guest')):
    if x_role not in {'engineering', 'finance'}: raise HTTPException(403, 'Role is not allowed to query protected knowledge')
    sources = retrieve(payload.question, x_role)
    return {'answer': ' '.join(sources) if sources else 'I do not have enough authorized context to answer.', 'sources': sources, 'role': x_role}
