FROM python:3.12-slim

WORKDIR /app/AetherMind

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    vim \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/AetherMind

RUN pip3 install -r requirements.txt

RUN mkdir /app/AetherMind/static

COPY backup_openai_chat_models_base.py /usr/local/lib/python3.12/site-packages/langchain_openai/chat_models/base.py

EXPOSE 8601

HEALTHCHECK CMD curl --fail http://localhost:8601/_stcore/health

ENTRYPOINT ["streamlit", "run", "AetherMind.py", "--server.port=8601", "--server.address=0.0.0.0"]