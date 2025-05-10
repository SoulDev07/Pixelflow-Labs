# Stage 1: Build client
FROM node:20-alpine AS client-build
WORKDIR /app/client

# Copy package files
COPY client/package.json ./

# Install dependencies with specific esbuild version
RUN npm install -g npm@latest && npm install

# Copy source files and build
COPY client/ ./
RUN npm run build

# Stage 2: Build server
FROM python:3.10-slim AS server-build
WORKDIR /app/server
COPY server/requirements.txt ./
RUN pip install -r requirements.txt
COPY server/ ./

# Stage 3: Build trend_job
FROM python:3.10-slim AS trend-job-build
WORKDIR /app/trend_job
COPY trend_job/requirements.txt ./
RUN pip install -r requirements.txt && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
COPY trend_job/ ./

# Final stage: Run all services
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy client build
COPY --from=client-build /app/client/dist /app/client/dist

# Copy server and install dependencies
COPY --from=server-build /app/server /app/server
COPY server/requirements.txt /app/server/
RUN pip install -r /app/server/requirements.txt

# Copy trend_job and install dependencies
COPY --from=trend-job-build /app/trend_job /app/trend_job
COPY trend_job/requirements.txt /app/trend_job/
RUN pip install -r /app/trend_job/requirements.txt && \
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Expose ports
EXPOSE 80 8000

# Start all services
CMD ["sh", "-c", "cd /app/server && python app.py & cd /app/trend_job && python main.py & wait"] 