# Stage 1: Build Frontend
FROM node:18-slim AS build-stage
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Run Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for newspaper3k and lxml
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend from Stage 1
COPY --from=build-stage /app/frontend/build ./frontend/build

# Ensure environment variables are handled (Port is set by Render)
ENV PORT=8000
EXPOSE 8000

# Start unified service
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
