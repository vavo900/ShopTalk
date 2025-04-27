"""Download + flatten Amazon‑Berkeley‑Objects metadata as parquet."""
import json, re, random, subprocess, tempfile
from pathlib import Path
import pandas as pd
from smart_open import open as sopen
from tqdm import tqdm
from .config import DATA_PROC

S3_PREFIX = "s3://amazon-berkeley-objects/listings/metadata/"

def normalise(txt: str) -> str:
    return re.sub(r"\s+", " ", txt.strip().lower())

def english_or_first(arr, key="value"):
    if not arr:
        return ""
    for d in arr:
        if d.get("language_tag", "").startswith("en"):
            return d.get(key, "")
    return arr[0].get(key, "")

def stream_records():
    with tempfile.TemporaryDirectory() as td:
        cmd = ["aws", "s3", "ls", "--no-sign-request", S3_PREFIX, "--recursive"]
        lines = subprocess.check_output(cmd, text=True).splitlines()
        files = [f"{S3_PREFIX}{line.split()[-1]}" for line in lines if line.strip().endswith(".json.gz")]
        for f in tqdm(files, desc="Streaming ABO"):
            with sopen(f, 'rb') as fp:
                for ln in fp:
                    yield json.loads(ln)

def build_df():
    rows = []
    for j in stream_records():
        rows.append(dict(
            asin=j["item_id"],
            title=normalise(english_or_first(j["item_name"])),
            desc=normalise(english_or_first(j.get("product_description")) or " ".join(bp["value"] for bp in j.get("bullet_point", []) if "value" in bp)),
            brand=english_or_first(j.get("brand")),
            url=f'https://www.amazon.com/dp/{j["item_id"]}'
        ))
    return pd.DataFrame(rows)

def create_triplets(df: pd.DataFrame) -> pd.DataFrame:
    descs=df["desc"].tolist()
    def rand_neg(x):
        import random
        n=random.randint(0,len(descs)-1)
        return descs[n] if descs[n]!=x else rand_neg(x)
    return pd.DataFrame({"query": df["title"], "pos": df["desc"], "neg":[rand_neg(x) for x in df["desc"]]})

def main():
    DATA_PROC.mkdir(parents=True, exist_ok=True)
    df=build_df().drop_duplicates("asin").query("desc!='' and title!=''")
    df.to_parquet(DATA_PROC / "products.parquet", index=False)
    trip=create_triplets(df)
    trip.to_parquet(DATA_PROC / "triplets.parquet", index=False)
    print(f"Saved {len(df)} products")

if __name__ == "__main__":
    main()
