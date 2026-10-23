FROM python:3.11-slim
WORKDIR /app
COPY . .
CMD ["python", "-m", "src.matcher.pipeline", "--input", "data/business_partners.csv", "--out", "out/"]
