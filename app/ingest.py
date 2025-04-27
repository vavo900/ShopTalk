import pandas as pd, chromadb
from sentence_transformers import SentenceTransformer
from .config import DATA_PROC, CHROMA_DIR, LORA_OUTPUT, EMBED_MODEL

def encoder():
    return SentenceTransformer(str(LORA_OUTPUT if LORA_OUTPUT.exists() else EMBED_MODEL))

def main():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    coll = client.get_or_create_collection("products")
    df = pd.read_parquet(DATA_PROC/'products.parquet')
    enc = encoder()
    batch, meta, ids=[],[],[]
    for idx,row in df.iterrows():
        batch.append(f"{row.title}. {row.desc}")
        meta.append({"asin":row.asin,"url":row.url,"brand":row.brand})
        ids.append(str(idx))
        if len(batch)==64:
            coll.add(documents=batch, metadatas=meta, ids=ids)
            batch,meta,ids=[],[],[]
    if batch:
        coll.add(documents=batch, metadatas=meta, ids=ids)
    print("Ingested", len(df), "docs")

if __name__ == '__main__':
    main()
