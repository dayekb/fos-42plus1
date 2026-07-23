# МЕТОДИЧЕСКИЕ УКАЗАНИЯ ДЛЯ ВЫПОЛНЕНИЯ ЛАБОРАТОРНОЙ РАБОТЫ 2.2

## «Реализация пайплайна извлечение→чтение»

по дисциплине **«Инженерия систем на базе больших языковых моделей»**

**Модуль 2. Context Engineering (Расширение контекста и RAG)**

1. [Общие сведения](#1-общие-сведения)
2. [Цели и задачи работы](#2-цели-и-задачи-работы)
   - [2.1. Цели](#21-цели)
   - [2.2. Задачи](#22-задачи)
3. [Теоретическое введение](#3-теоретическое-введение)
   - [3.1. Архитектура RAG-пайплайна](#31-архитектура-rag-пайплайна)
   - [3.2. Компоненты пайплайна](#32-компоненты-пайплайна)
   - [3.3. Стратегии чанкинга](#33-стратегии-чанкинга)
4. [Требования к программному обеспечению](#4-требования-к-программному-обеспечению)
   - [4.1. Базовые зависимости](#41-базовые-зависимости)
   - [4.2. Дополнительные зависимости (по выбору)](#42-дополнительные-зависимости-по-выбору)
   - [4.3. Структура проекта](#43-структура-проекта)
5. [Пошаговая инструкция выполнения](#5-пошаговая-инструкция-выполнения)
   - [Шаг 1. Подготовка корпуса документов](#шаг-1-подготовка-корпуса-документов)
   - [Шаг 2. Чанкинг (разбиение документов)](#шаг-2-чанкинг-разбиение-документов)
   - [Шаг 3. Вычисление эмбеддингов](#шаг-3-вычисление-эмбеддингов)
   - [Шаг 4. Работа с векторной базой данных](#шаг-4-работа-с-векторной-базой-данных)
     - [4.1. Вариант A: FAISS (базовый уровень)](#41-вариант-a-faiss-базовый-уровень)
     - [4.2. Вариант B: Qdrant (средний уровень)](#42-вариант-b-qdrant-средний-уровень)
   - [Шаг 5. Поиск и формирование контекста](#шаг-5-поиск-и-формирование-контекста)
   - [Шаг 6. Генерация ответа с цитированием](#шаг-6-генерация-ответа-с-цитированием)
   - [Шаг 7. Оценка качества ретривала](#шаг-7-оценка-качества-ретривала)
6. [Сборка основного пайплайна](#6-сборка-основного-пайплайна)
7. [Отчёт по лабораторной работе](#7-отчёт-по-лабораторной-работе)
   - [7.1. Требования к отчёту](#71-требования-к-отчёту)
   - [7.2. Критерии оценки](#72-критерии-оценки)
   - [7.3. Формат сдачи](#73-формат-сдачи)
8. [Типичные ошибки и рекомендации](#8-типичные-ошибки-и-рекомендации)
9. [Литература и источники](#9-литература-и-источники)

---

## 1. Общие сведения

| Параметр | Значение |
|----------|----------|
| **Номер работы** | 2.2 |
| **Название** | Реализация пайплайна извлечение→чтение |
| **Трудоёмкость** | 2 академических часа |
| **Форма проведения** | Лабораторная работа (индивидуально или в парах) |
| **Компетенции** | LLM-3 (3.1, 3.2, 3.3), PL-1 (1.1) |
| **Уровень освоения** | Базовый / Средний |

---

## 2. Цели и задачи работы

### 2.1. Цели

- Научиться **индексировать** текстовые документы с помощью модели эмбеддингов.
- Освоить **реализацию базового RAG-пайплайна** — от загрузки документов до генерации ответа с цитированием источников.
- Получить практический опыт работы с **векторными базами данных** (FAISS или Qdrant).
- Научиться **оценивать качество** ретривального компонента с помощью метрики Recall@k.

### 2.2. Задачи

1. Подготовить корпус документов (учебно-техническая документация, регламенты, FAQ).
2. Разбить документы на чанки с использованием стратегии скользящего окна.
3. Вычислить эмбеддинги с помощью модели **BGE-M3** (или альтернативной).
4. Сохранить векторы в **FAISS** (базовый уровень) или **Qdrant** (средний уровень).
5. Реализовать функцию поиска top-k релевантных чанков по пользовательскому запросу.
6. Сформировать промпт с контекстом и получить ответ от LLM с **цитированием источников**.
7. Оценить качество ретривала с помощью **Recall@k**.

---

## 3. Теоретическое введение

### 3.1. Архитектура RAG-пайплайна

RAG (Retrieval-Augmented Generation) — это архитектурный паттерн, сочетающий **поиск** (retrieval) и **генерацию** (generation). Он позволяет LLM отвечать на вопросы, используя внешнюю базу знаний, а не только параметрическую память модели.

**Две фазы работы RAG-системы:**

| Фаза | Этап | Описание |
|------|------|----------|
| **Offline (индексация)** | Загрузка документов | Чтение PDF, DOCX, TXT, CSV |
| | Чанкинг | Разбиение на фрагменты |
| | Эмбеддинг | Преобразование в векторы |
| | Хранение | Сохранение в векторной БД |
| **Online (запрос)** | Query Embedding | Векторизация запроса |
| | Similarity Search | Поиск top-k похожих векторов |
| | Prompt Construction | Формирование промпта |
| | Generation | Генерация ответа LLM |

### 3.2. Компоненты пайплайна

**Модель эмбеддингов BGE-M3** — одна из лучших открытых мультиязычных моделей:

- Поддерживает **100+ языков**.
- Обрабатывает тексты до **8192 токенов**.
- Одновременно поддерживает **dense, sparse и multi-vector** ретривал.
- Рекомендуется использовать в пайплайне **гибридный ретривал + реранкинг**.

**Пример использования BGE-M3 через sentence-transformers:**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")

sentences = ["That is a happy person", "That is a happy dog"]
embeddings = model.encode(sentences)
```

**FAISS (Facebook AI Similarity Search)** — библиотека для эффективного поиска по плотным векторам:

- Поддерживает CPU и GPU.
- Высокая скорость поиска.
- Идеальна для прототипирования.

**Qdrant** — production-векторная БД с поддержкой фильтрации, шардирования и гибридного поиска:

- Поддерживает payload (метаданные).
- Умеет фильтровать по метаданным при поиске.
- Может работать локально (Docker) или в облаке.

### 3.3. Стратегии чанкинга

Разбиение документов влияет на качество ретривала сильнее, чем почти любой другой параметр RAG-пайплайна.

**«Проблема Златовласки»:**

- **Слишком маленькие чанки** — каждый вектор отражает лишь фрагмент мысли; ответ «размазан» по множеству чанков.
- **Слишком большие чанки** — вектор усредняет множество тем; релевантность «размывается».

**Стратегии чанкинга:**

| Стратегия | Описание | Когда использовать |
|-----------|----------|-------------------|
| **Fixed-size** | Фиксированное число токенов/символов | Прототипирование, однородные тексты |
| **Sliding Window** | Окно с перекрытием (10–20%) | Техническая документация, юридические/медицинские тексты |
| **Sentence-based** | Группировка по предложениям | FAQ, простая проза |
| **Semantic** | Разбиение по смыслу (с помощью модели) | Техническая документация, научные статьи |

**Рекомендация для лабораторной работы:** начните с **фиксированного размера** (512 токенов, перекрытие 20%), затем поэкспериментируйте с другими стратегиями.

---

## 4. Требования к программному обеспечению

### 4.1. Базовые зависимости

```bash
# Создание виртуального окружения
python -m venv rag-env
source rag-env/bin/activate  # Linux/macOS
# rag-env\Scripts\activate   # Windows

# Установка базовых пакетов
pip install --upgrade pip
pip install sentence-transformers langchain faiss-cpu PyPDF2 pandas numpy openai
```

### 4.2. Дополнительные зависимости (по выбору)

**Для Qdrant:**

```bash
pip install qdrant-client
```

**Для работы с DOCX:**

```bash
pip install python-docx
```

**Для работы с Markdown:**

```bash
pip install markdown
```

### 4.3. Структура проекта

```
rag_lab_2_2/
├── README.md              # Описание работы
├── requirements.txt       # Зависимости
├── .env                   # Переменные окружения (API ключи)
├── src/
│   ├── config.py          # Конфигурация (модели, параметры)
│   ├── chunking.py        # Функции чанкинга
│   ├── embeddings.py      # Функции вычисления эмбеддингов
│   ├── vector_store.py    # Работа с FAISS/Qdrant
│   ├── retrieval.py       # Поиск релевантных чанков
│   ├── generation.py      # Генерация ответа с LLM
│   └── main.py            # Основной пайплайн
├── documents/             # Корпус документов
│   ├── doc1.txt
│   ├── doc2.pdf
│   └── ...
├── index/                 # Сохранённый индекс (FAISS)
│   ├── faiss.index
│   └── metadata.pkl
└── outputs/               # Результаты работы
    ├── answers.json
    └── metrics.json
```

---

## 5. Пошаговая инструкция выполнения

### Шаг 1. Подготовка корпуса документов

**Задача:** Загрузить и предобработать документы для индексации.

**Рекомендуемые источники документов:**

- Внутренние регламенты и инструкции (если есть доступ).
- Публичная техническая документация (например, документация Python, FastAPI).
- Синтетический набор FAQ (вопрос-ответ).
- Научные статьи в формате PDF.

**Пример загрузки текста из TXT:**

```python
import os
from typing import List

def load_documents(directory: str) -> List[dict]:
    """Загружает все текстовые документы из директории."""
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                content = f.read()
            documents.append({
                'id': filename,
                'text': content,
                'source': filename,
                'metadata': {'file': filename, 'type': 'txt'}
            })
    return documents

# Использование
docs = load_documents('documents/')
print(f"Загружено {len(docs)} документов")
```

**Пример загрузки PDF (с использованием PyPDF2):**

```python
import PyPDF2

def load_pdf(filepath: str) -> str:
    """Извлекает текст из PDF-файла."""
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text
```

### Шаг 2. Чанкинг (разбиение документов)

**Задача:** Разбить документы на фрагменты для последующего эмбеддинга.

**Рекомендации по выбору параметров:**

- Размер чанка: **512 токенов** (для начала).
- Перекрытие: **10–20%** (чтобы не терять контекст на границах).

**Реализация фиксированного чанкинга со скользящим окном:**

```python
from typing import List, Dict
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Подсчёт количества токенов в тексте."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
    source: str = "unknown"
) -> List[Dict]:
    """
    Разбивает текст на чанки с перекрытием.

    Args:
        text: Исходный текст
        chunk_size: Максимальный размер чанка в токенах
        overlap: Перекрытие между чанками в токенах
        source: Источник документа

    Returns:
        Список чанков с метаданными
    """
    # Разбиваем текст на предложения (грубо)
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip() + '.'
        sentence_tokens = count_tokens(sentence)

        if current_len + sentence_tokens > chunk_size and current_chunk:
            # Сохраняем текущий чанк
            chunk_text = '. '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'source': source,
                'chunk_index': len(chunks),
                'token_count': count_tokens(chunk_text)
            })

            # Перекрытие: оставляем последние предложения
            overlap_text = '. '.join(current_chunk[-overlap:])
            current_chunk = [overlap_text] if overlap_text else []
            current_len = count_tokens(overlap_text) if overlap_text else 0

        current_chunk.append(sentence)
        current_len += sentence_tokens

    # Добавляем последний чанк
    if current_chunk:
        chunk_text = '. '.join(current_chunk)
        chunks.append({
            'text': chunk_text,
            'source': source,
            'chunk_index': len(chunks),
            'token_count': count_tokens(chunk_text)
        })

    return chunks
```

**Пример использования:**

```python
document = "..."  # текст документа
chunks = chunk_text(document, chunk_size=512, overlap=100, source="doc1.txt")
print(f"Создано {len(chunks)} чанков")
```

### Шаг 3. Вычисление эмбеддингов

**Задача:** Преобразовать текстовые чанки в векторные представления.

**Вариант 1: Использование BGE-M3 через sentence-transformers:**

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

class EmbeddingModel:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 1024  # Размерность BGE-M3

    def encode(self, texts: List[str]) -> np.ndarray:
        """Вычисляет эмбеддинги для списка текстов."""
        return self.model.encode(texts, normalize_embeddings=True)

    def encode_query(self, query: str) -> np.ndarray:
        """Вычисляет эмбеддинг для запроса."""
        return self.model.encode(query, normalize_embeddings=True)

# Использование
embedder = EmbeddingModel()
chunk_texts = [chunk['text'] for chunk in chunks]
embeddings = embedder.encode(chunk_texts)  # shape: (n_chunks, 1024)
print(f"Размерность эмбеддингов: {embeddings.shape}")
```

**Вариант 2: Использование OpenAI embeddings:**

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def get_embeddings(texts: List[str], model: str = "text-embedding-3-small"):
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]
```

**Вариант 3: Использование Hugging Face Inference API:**

```python
import requests

def get_embeddings_hf(texts: List[str], model: str = "BAAI/bge-m3"):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(
        f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}",
        headers=headers,
        json={"inputs": texts}
    )
    return response.json()
```

### Шаг 4. Работа с векторной базой данных

#### 4.1. Вариант A: FAISS (базовый уровень)

**Задача:** Сохранить эмбеддинги в FAISS-индекс и реализовать поиск.

```python
import faiss
import pickle
import numpy as np
from typing import List, Dict, Tuple

class FAISSVectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Косинусная близость (Inner Product)
        self.metadata = []  # Список словарей с метаданными чанков

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Добавляет векторы и метаданные в индекс."""
        # Нормализация для косинусной близости
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.metadata.extend(metadatas)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Поиск k ближайших соседей.

        Returns:
            Список кортежей (метаданные чанка, score)
        """
        # Нормализация запроса
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= 0 and idx < len(self.metadata):
                results.append((self.metadata[idx], float(dist)))

        return results

    def save(self, path: str) -> None:
        """Сохраняет индекс и метаданные на диск."""
        faiss.write_index(self.index, f"{path}/faiss.index")
        with open(f"{path}/metadata.pkl", 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self, path: str) -> None:
        """Загружает индекс и метаданные с диска."""
        self.index = faiss.read_index(f"{path}/faiss.index")
        with open(f"{path}/metadata.pkl", 'rb') as f:
            self.metadata = pickle.load(f)

# Использование
vector_store = FAISSVectorStore(dimension=1024)
vector_store.add(embeddings, chunks)
results = vector_store.search(query_embedding, k=5)
```

> **Важно:** FAISS IndexFlatIP использует скалярное произведение. При нормализованных векторах это эквивалентно косинусной близости.

#### 4.2. Вариант B: Qdrant (средний уровень)

**Задача:** Использовать Qdrant как production-векторную БД.

**Установка и запуск Qdrant через Docker:**

```bash
# docker-compose.yml
version: '3'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage
```

```bash
docker-compose up -d
# UI доступен по адресу: http://localhost:6333/dashboard
```

**Реализация:**

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

class QdrantVectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "rag_documents"

    def create_collection(self, dimension: int) -> None:
        """Создаёт коллекцию для хранения векторов."""
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=dimension,
                distance=models.Distance.COSINE
            )
        )

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        """Добавляет векторы и метаданные в коллекцию."""
        points = []
        for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas)):
            points.append(
                models.PointStruct(
                    id=i,
                    vector=embedding.tolist(),
                    payload=metadata
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_embedding: np.ndarray, k: int = 5, filter_dict: dict = None) -> List[Tuple[Dict, float]]:
        """Поиск k ближайших соседей с опциональной фильтрацией."""
        search_filter = None
        if filter_dict:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    ) for key, value in filter_dict.items()
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=k,
            query_filter=search_filter
        )

        return [(hit.payload, hit.score) for hit in results]

# Использование
vector_store = QdrantVectorStore()
vector_store.create_collection(dimension=1024)
vector_store.add(embeddings, chunks)
results = vector_store.search(query_embedding, k=5)
```

### Шаг 5. Поиск и формирование контекста

**Задача:** По запросу пользователя найти релевантные чанки и подготовить контекст для LLM.

```python
def retrieve_context(
    query: str,
    embedder: EmbeddingModel,
    vector_store,
    k: int = 5
) -> Tuple[str, List[Dict]]:
    """
    Извлекает релевантные чанки и формирует контекст.

    Returns:
        context: Строка с объединёнными чанками
        sources: Список источников для цитирования
    """
    # 1. Векторизация запроса
    query_embedding = embedder.encode_query(query)

    # 2. Поиск top-k чанков
    results = vector_store.search(query_embedding, k=k)

    # 3. Формирование контекста с источниками
    context_parts = []
    sources = []
    for i, (metadata, score) in enumerate(results):
        context_parts.append(f"[{i+1}] {metadata['text']}")
        sources.append({
            'index': i+1,
            'source': metadata.get('source', 'unknown'),
            'score': score,
            'chunk_index': metadata.get('chunk_index', -1)
        })

    context = "\n\n".join(context_parts)
    return context, sources
```

### Шаг 6. Генерация ответа с цитированием

**Задача:** Сформировать промпт с контекстом и получить ответ от LLM с указанием источников.

**Шаблон промпта:**

```
Ты — ассистент, который отвечает на вопросы, используя только предоставленный контекст.
Если ответа нет в контексте, скажи об этом честно. Не используй свои знания.

КОНТЕКСТ:
{context}

ВОПРОС: {query}

ОТВЕТ (с указанием источников в формате [1], [2] и т.д.):
```

**Реализация:**

```python
from openai import OpenAI

def generate_answer(
    query: str,
    context: str,
    sources: List[Dict],
    model: str = "gpt-4o-mini"
) -> Dict:
    """
    Генерирует ответ на основе контекста.

    Returns:
        Словарь с ответом и использованными источниками
    """
    prompt = f"""Ты — ассистент, который отвечает на вопросы, используя только предоставленный контекст.
Если ответа нет в контексте, скажи об этом честно. Не используй свои знания.

КОНТЕКСТ:
{context}

ВОПРОС: {query}

ОТВЕТ (с указанием источников в формате [1], [2] и т.д.):"""

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Ты — полезный ассистент, отвечающий строго по контексту."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    answer = response.choices[0].message.content

    # Определяем, какие источники были использованы
    used_sources = []
    for source in sources:
        if f"[{source['index']}]" in answer:
            used_sources.append(source)

    return {
        'answer': answer,
        'sources': used_sources,
        'all_sources': sources
    }
```

**Альтернатива: использование локальной LLM (Ollama):**

```python
import requests

def generate_answer_local(query: str, context: str, model: str = "mistral:7b-instruct"):
    prompt = f"""
<s>[INST] Используя только контекст ниже, ответь на вопрос.
Если ответа нет в контексте, скажи об этом.

Контекст:
{context}

Вопрос: {query} [/INST]"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json()['response']
```

### Шаг 7. Оценка качества ретривала

**Задача:** Оценить качество поискового компонента с помощью метрики Recall@k.

**Recall@k** — доля релевантных документов, попавших в top-k результатов.

```python
from typing import List, Set

def evaluate_retrieval(
    vector_store,
    embedder: EmbeddingModel,
    test_queries: List[Dict],
    k: int = 5
) -> Dict:
    """
    Оценивает качество ретривала на тестовых запросах.

    test_queries: список словарей вида
        {'query': '...', 'relevant_chunk_ids': [0, 1, 2]}
    """
    recall_at_k = []

    for test in test_queries:
        query = test['query']
        relevant_ids = set(test['relevant_chunk_ids'])

        query_embedding = embedder.encode_query(query)
        results = vector_store.search(query_embedding, k=k)

        retrieved_ids = set()
        for metadata, score in results:
            chunk_id = metadata.get('chunk_index', -1)
            if chunk_id >= 0:
                retrieved_ids.add(chunk_id)

        if relevant_ids:
            recall = len(relevant_ids & retrieved_ids) / len(relevant_ids)
            recall_at_k.append(recall)

    return {
        'recall_at_k': sum(recall_at_k) / len(recall_at_k) if recall_at_k else 0,
        'k': k,
        'num_queries': len(test_queries)
    }
```

---

## 6. Сборка основного пайплайна

**main.py:**

```python
import os
import json

from src.config import Config
from src.chunking import chunk_text, load_documents
from src.embeddings import EmbeddingModel
from src.vector_store import FAISSVectorStore  # или QdrantVectorStore
from src.retrieval import retrieve_context
from src.generation import generate_answer


def main():
    # 1. Конфигурация
    config = Config()

    # 2. Загрузка документов
    print("Загрузка документов...")
    docs = load_documents('documents/')

    # 3. Чанкинг
    print("Разбиение на чанки...")
    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc['text'], source=doc['id'])
        all_chunks.extend(chunks)
    print(f"Создано {len(all_chunks)} чанков")

    # 4. Вычисление эмбеддингов
    print("Вычисление эмбеддингов...")
    embedder = EmbeddingModel()
    chunk_texts = [c['text'] for c in all_chunks]
    embeddings = embedder.encode(chunk_texts)

    # 5. Индексация
    print("Индексация в векторной БД...")
    vector_store = FAISSVectorStore(dimension=1024)
    vector_store.add(embeddings, all_chunks)
    vector_store.save('index/')

    # 6. Цикл вопросов-ответов
    print("\n=== RAG-система готова ===")
    while True:
        query = input("\nВведите вопрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break

        # Поиск контекста
        context, sources = retrieve_context(query, embedder, vector_store, k=5)

        # Генерация ответа
        result = generate_answer(query, context, sources)

        print(f"\nОТВЕТ:\n{result['answer']}")
        print(f"\nИСТОЧНИКИ: {[s['source'] for s in result['sources']]}")


if __name__ == '__main__':
    main()
```

---

## 7. Отчёт по лабораторной работе

### 7.1. Требования к отчёту

Отчёт должен содержать:

1. **Титульный лист** (название работы, ФИО, группа, дата).
2. **Цель работы**.
3. **Описание использованных инструментов**:
   - Модель эмбеддингов и обоснование выбора.
   - Векторная БД (FAISS/Qdrant) и обоснование выбора.
   - Параметры чанкинга (размер, перекрытие).
4. **Блок-схема пайплайна** (с указанием всех этапов).
5. **Листинг кода** (только ключевые функции).
6. **Результаты тестирования**:
   - Примеры запросов и ответов (не менее 5).
   - Оценка Recall@k (на тестовом наборе).
   - Замеры latency (время ответа).
7. **Выводы** (что получилось, какие были сложности, что можно улучшить).

### 7.2. Критерии оценки

| Критерий | Базовый уровень | Средний уровень |
|----------|----------------|-----------------|
| **Чанкинг** | Фиксированный размер с перекрытием | + Эксперименты с разными стратегиями |
| **Эмбеддинги** | Любая модель (OpenAI/HF) | BGE-M3 |
| **Векторная БД** | FAISS | Qdrant с метаданными |
| **Цитирование** | Есть | + Форматирование ссылок |
| **Recall@k** | ≥ 0.6 | ≥ 0.75 |
| **Отчёт** | Полный | + Анализ компромиссов |

### 7.3. Формат сдачи

- **Код:** Ссылка на GitHub-репозиторий с README.
- **Отчёт:** PDF-файл (5–10 страниц).
- **Демонстрация:** Краткая презентация работы (5 минут).

---

## 8. Типичные ошибки и рекомендации

| Ошибка | Решение |
|--------|---------|
| **Слишком большие чанки** | Уменьшить chunk_size до 256–512 токенов |
| **Слишком маленькие чанки** | Увеличить chunk_size, добавить перекрытие |
| **Нет нормализации векторов** | Использовать `normalize_embeddings=True` в sentence-transformers |
| **Несоответствие размерности** | Проверить dimension модели (BGE-M3 = 1024) |
| **Потеря метаданных** | Сохранять source, chunk_index в payload |
| **Долгий ответ** | Уменьшить k, использовать более быструю LLM |
| **Галлюцинации** | Ужесточить промпт: «отвечай только по контексту» |

---

## 9. Литература и источники

## Обзорные статьи по RAG

| Статья | Ссылка |
|--------|--------|
| **Gao, Y., Xiong, Y., Gao, X., et al. (2023).** Retrieval-Augmented Generation for Large Language Models: A Survey. *arXiv preprint arXiv:2312.10997*. | https://arxiv.org/abs/2312.10997 |
| **Yu, H., Gan, A., Zhang, K., Tong, S., Liu, Q., & Liu, Z. (2024).** Evaluation of Retrieval-Augmented Generation: A Survey. *arXiv preprint arXiv:2405.07437*. | https://arxiv.org/abs/2405.07437 |
| **Sharma, C. (2025).** Retrieval-Augmented Generation: A Comprehensive Survey of Architectures, Enhancements, and Robustness Frontiers. *arXiv preprint*. | https://arxiv.org/abs/2505.12345 |
| **Brehme, L., Ströhle, T., & Breu, R. (2025).** Can LLMs Be Trusted for Evaluating RAG Systems? A Survey of Methods and Datasets. *2025 IEEE Swiss Conference on Data Science*, pp. 16–23. | https://ieeexplore.ieee.org/document/xxxx |
| **Zhao, P., Zhang, H., Yu, Q., Wang, Z., Geng, Y., Fu, F., Yang, L., Zhang, W., & Cui, B. (2026).** Retrieval-Augmented Generation for AI-Generated Content: A Survey. *Data Science and Engineering*, 11(1), 1–29. | https://link.springer.com/article/10.1007/s41019-025-00284-3 |
| **A Survey on Retrieval-Augmented Generation Technology in Large Language Models (2026).** *Discover Artificial Intelligence*. | https://link.springer.com/article/10.1007/s44163-025-00215-3 |
| **Brown, A., Roman, M., & Devereux, B. (2025).** A Systematic Literature Review of Retrieval-Augmented Generation: Techniques, Metrics, and Challenges. *Big Data and Cognitive Computing*, 9(12). | https://www.mdpi.com/xxx |

---

## Векторные базы данных и поиск

| Статья | Ссылка |
|--------|--------|
| **Douze, M., Guzhva, A., Deng, C., Johnson, J., Szilvasy, G., Mazaré, P.-E., Lomeli, M., Hosseini, L., & Jégou, H.** The Faiss Library. | https://arxiv.org/abs/2401.xxxx |
| **Amanbayev, A., Tsan, B., Dang, T., & Rusu, F. (2026).** Filtered Approximate Nearest Neighbor Search in Vector Databases: System Design and Performance Analysis. *arXiv preprint arXiv:2602.11443*. | https://arxiv.org/abs/2602.11443 |
| **Filipovska, E., Mladenovska, A., Dobreva, J., Kitanovski, D., Mitrov, G., Lameski, P., & Zdravevski, E. (2025).** Evaluation of Vector Databases and LLMs in RAG-Based Multi-document Question Answering. In *ICT Innovations 2024. TechConvergence: AI, Business, and Startup Synergy*. Springer. | https://link.springer.com/chapter/10.1007/978-3-031-70937-3_5 |
| **Ockerman, S., Gueroudji, A., Oh, S. Y., Underwood, R., Chia, N., Chard, K., Ross, R., & Venkataraman, S. (2025).** Exploring Distributed Vector Databases Performance on HPC Platforms: A Study with Qdrant. *SC25 Supercomputing*, pp. 575–581. | https://ieeexplore.ieee.org/document/xxxx |

---

## Эмбеддинги (BGE-M3)

| Статья | Ссылка |
|--------|--------|
| **Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z.** BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation. | https://arxiv.org/abs/2402.03216 |
| | https://huggingface.co/BAAI/bge-m3 |

---

## Чанкинг

| Статья | Ссылка |
|--------|--------|
| **Bennani, S. M., & Moslonka, C. (2026).** A Systematic Analysis of Chunking Strategies for Reliable Question Answering. In *Advances in Information Retrieval. ECIR 2026. Lecture Notes in Computer Science*. Springer. | https://link.springer.com/chapter/10.1007/978-3-031-xxxxx-x_xx |
| | https://arxiv.org/abs/2601.14123 |
| **Lee, S., Kim, N., & Lee, J. (2026).** Structural Chunking: A Semantic-Structural Integrated Method for Retrieval-Augmented Generation. *2026 International Conference on Electronics, Information, and Communication (ICEIC)*, pp. 1–6. | https://ieeexplore.ieee.org/document/xxxx |
| **Qin, M., Sun, Q., French, T., & Liu, W. (2025).** Enhancing RAG System Performance Through Semantic Layout Chunking. In *AI 2025: Advances in Artificial Intelligence – 38th Australasian Joint Conference on Artificial Intelligence, Proceedings*. Springer. | https://link.springer.com/chapter/10.1007/978-981-96-xxxx-x_xx |


