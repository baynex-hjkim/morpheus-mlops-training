FROM rayproject/ray:2.40.0-py312

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.train"]
