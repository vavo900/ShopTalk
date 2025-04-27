FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 8501
CMD ["bash","-c","uvicorn app.api:app --host 0.0.0.0 --port 8000 & streamlit run app/ui_streamlit.py --server.port 8501"]
