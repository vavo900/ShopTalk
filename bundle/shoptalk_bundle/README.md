# ShopTalk – quick‑start bundle

Generated on 2025-04-26T21:21:37.511584.

Run:

```bash
conda create -n shoptalk python=3.10 -y && conda activate shoptalk
pip install -r requirements.txt
python -m app.data_prep      # download + preprocess
python -m app.ingest         # build vector DB
uvicorn app.api:app --reload
streamlit run app/ui_streamlit.py
```
