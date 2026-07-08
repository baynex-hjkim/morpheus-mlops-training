FROM rayproject/ray:2.40.0-py312

WORKDIR /app
COPY src ./src

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.train"]
