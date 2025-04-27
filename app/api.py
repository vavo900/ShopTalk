from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from .rag_chain import build_chain

app = FastAPI(title='ShopTalk RAG API')
retriever, chain = build_chain()

class Query(BaseModel):
    query:str
class Result(BaseModel):
    answer:str
    context_ids:List[str]

@app.post('/search', response_model=Result)
def search(q:Query):
    docs = retriever.get_relevant_documents(q.query)
    context="\n".join(d.page_content for d in docs)
    ans = chain.run({'context':context,'question':q.query})
    return Result(answer=ans, context_ids=[d.metadata.get("asin") for d in docs])
