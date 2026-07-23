# МЕТОДИЧЕСКИЕ УКАЗАНИЯ ДЛЯ ВЫПОЛНЕНИЯ ЛАБОРАТОРНОЙ РАБОТЫ 2.3

## «Оптимизация и интеграция RAG: гибридный поиск, реранкинг и переформулировка запросов»

### с метрической автопроверкой качества

по дисциплине **«Инженерия систем на базе больших языковых моделей»**

**Модуль 2. Context Engineering (Расширение контекста и RAG)**

1. [Общие сведения](#1-общие-сведения)
2. [Цели и задачи работы](#2-цели-и-задачи-работы)
   - [2.1. Цели](#21-цели)
   - [2.2. Задачи](#22-задачи)
3. [Теоретическое введение](#3-теоретическое-введение)
   - [3.1. Гибридный поиск (Hybrid Search)](#31-гибридный-поиск-hybrid-search)
   - [3.2. Reciprocal Rank Fusion (RRF)](#32-reciprocal-rank-fusion-rrf)
   - [3.3. Двухстадийный реранкинг (Cross-Encoder)](#33-двухстадийный-реранкинг-cross-encoder)
   - [3.4. Query Rewriting (переформулировка запроса)](#34-query-rewriting-переформулировка-запроса)
4. [Требования к программному обеспечению](#4-требования-к-программному-обеспечению)
   - [4.1. Дополнительные зависимости](#41-дополнительные-зависимости)
   - [4.2. Структура проекта (дополнение к лабораторной 2.2)](#42-структура-проекта-дополнение-к-лабораторной-22)
   - [4.3. Тестовый датасет](#43-тестовый-датасет-evaluationtest_queriesjson)
5. [Пошаговая инструкция выполнения](#5-пошаговая-инструкция-выполнения)
   - [Шаг 1. Реализация BM25-ретривера](#шаг-1-реализация-bm25-ретривера)
   - [Шаг 2. Реализация гибридного поиска с RRF](#шаг-2-реализация-гибридного-поиска-с-rrf)
   - [Шаг 3. Реализация реранкинга (Cross-Encoder)](#шаг-3-реализация-реранкинга-cross-encoder)
   - [Шаг 4. Реализация Query Rewriting](#шаг-4-реализация-query-rewriting)
   - [Шаг 5. Сборка оптимизированного пайплайна](#шаг-5-сборка-оптимизированного-пайплайна)
   - [Шаг 6. Запуск метрической автопроверки](#шаг-6-запуск-метрической-автопроверки)
6. [Отчёт по лабораторной работе](#6-отчёт-по-лабораторной-работе)
   - [6.1. Требования к отчёту](#61-требования-к-отчёту)
   - [6.2. Критерии оценки](#62-критерии-оценки)
7. [Типичные ошибки и рекомендации](#7-типичные-ошибки-и-рекомендации)
8. [Литература и источники](#8-литература-и-источники)
9. [Скрипт для проверки прохождения лабораторной (для преподавателя)](#9-скрипт-для-проверки-прохождения-лабораторной-для-преподавателя)

---

## 1. Общие сведения

| Параметр | Значение |
|----------|----------|
| **Номер работы** | 2.3 |
| **Название** | Оптимизация и интеграция RAG: гибридный поиск, реранкинг, query rewriting |
| **Трудоёмкость** | 2 академических часа |
| **Форма проведения** | Лабораторная работа (индивидуально) |
| **Компетенции** | LLM-3 (3.4, 3.5), LLM-1 (1.2) |
| **Уровень освоения** | Средний / Продвинутый |
| **Особенность** | Встроенная метрическая автопроверка (автоматическая оценка улучшения метрик) |

---

## 2. Цели и задачи работы

### 2.1. Цели

- Научиться интегрировать **лексический поиск (BM25)** в RAG-пайплайн.
- Освоить технику **Reciprocal Rank Fusion (RRF)** для объединения результатов dense и sparse поиска.
- Реализовать **двухстадийный реранкинг** с использованием cross-encoder для повышения точности ранжирования.
- Освоить технику **Query Rewriting** (переформулировка запроса) для повышения релевантности поиска.
- Провести **сравнительный анализ** качества различных конфигураций RAG-пайплайна с использованием автоматических метрик.

### 2.2. Задачи

1. Реализовать **BM25-ретривер** для лексического поиска.
2. Реализовать функцию **гибридного поиска** с объединением результатов через **RRF**.
3. Настроить **реранкер на основе cross-encoder** для уточнения ранжирования top-N кандидатов.
4. Реализовать модуль **Query Rewriting** для улучшения поисковых запросов.
5. Собрать **оптимизированный пайплайн**, объединяющий все компоненты.
6. Запустить **автопроверку** на тестовом датасете и оценить прирост качества.

---

## 3. Теоретическое введение

### 3.1. Гибридный поиск (Hybrid Search)

**Проблема:** Dense-поиск (эмбеддинги) отлично работает с синонимами и семантическими вариациями, но «слеп» к точным терминам, кодам и редким словам. BM25 (лексический поиск), наоборот, ищет точные совпадения, но не понимает смысла.

**Решение:** Гибридный поиск комбинирует оба подхода.

- **BM25 (Best Matching 25)** — ранжирующая функция, основанная на TF-IDF, которая учитывает частоту термина в документе, длину документа и обратную частоту документа.
- **Dense Search** — поиск по косинусной близости плотных векторных представлений.

### 3.2. Reciprocal Rank Fusion (RRF)

RRF — это метод объединения нескольких ранжированных списков в один, устойчивый к разномасштабным скорингам.

**Формула RRF:**

```
RRF_score(d) = Σ_{r∈R} 1 / (k + rank_r(d))
```

где:
- **R** — множество ранжированных списков (например, BM25 и Dense),
- **rank_r(d)** — позиция документа d в списке r,
- **k** — константа (обычно 60), сглаживающая влияние высоких рангов.

**Преимущество:** RRF не требует нормализации скорингов, что делает его идеальным для комбинирования гетерогенных ретриверов.

### 3.3. Двухстадийный реранкинг (Cross-Encoder)

**Проблема:** Bi-encoder (используемый для плотного поиска) кодирует запрос и документ независимо — быстро, но не идеально точно. Cross-encoder обрабатывает пару (запрос, документ) совместно, что даёт высокую точность, но медленно.

**Стратегия:**

| Стадия | Метод | Скорость | Точность |
|--------|-------|----------|----------|
| **1. Быстрый поиск** | Bi-encoder + BM25 (гибрид) | Высокая | Средняя |
| **2. Точный реранкинг** | Cross-encoder (на top-50) | Низкая | Высокая |

**Пример модели cross-encoder:**

- `cross-encoder/ms-marco-MiniLM-L-6-v2` — лёгкая, высокая скорость.
- `cross-encoder/ms-marco-MiniLM-L-12-v2` — более точная, медленнее.

**Реализация через sentence-transformers:**

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
scores = reranker.predict([(query, doc) for doc in docs])
```

### 3.4. Query Rewriting (переформулировка запроса)

**Зачем?** Пользовательские запросы часто содержат местоимения, аббревиатуры, неполные формулировки или разговорный сленг, что ухудшает качество поиска.

**Техника:**

1. Использовать LLM для переформулировки запроса в «поисково-дружественный» вид.
2. Декомпозировать сложные запросы на подзапросы.
3. Расширить аббревиатуры и уточнить неоднозначности.

**Пример промпта для переформулировки:**

```
Преобразуй следующий вопрос в оптимальный поисковый запрос для векторной базы данных.
Сохрани ключевые термины. Выведи только запрос, без пояснений.

Исходный вопрос: {query}

Оптимизированный запрос:
```

**Компромисс:** Переформулировка улучшает качество, но добавляет ~0.5–1 секунду к времени ответа (за счёт вызова LLM).

---

## 4. Требования к программному обеспечению

### 4.1. Дополнительные зависимости

```bash
pip install rank_bm25   # Реализация BM25
pip install sentence-transformers  # Для Cross-Encoder
```

> Если используется Qdrant с поддержкой гибридного поиска «из коробки» (версия ≥ 1.8.0), можно использовать его API вместо самостоятельной реализации RRF.

### 4.2. Структура проекта (дополнение к лабораторной 2.2)

```
rag_lab_2_3/
├── src/
│   ├── hybrid_retriever.py     # Гибридный поиск (BM25 + Dense + RRF)
│   ├── reranker.py             # Cross-encoder реранкинг
│   ├── query_rewriter.py       # Переформулировка запросов
│   └── pipeline_optimized.py   # Оптимизированный пайплайн
├── evaluation/
│   ├── test_queries.json       # Тестовый датасет (query + relevant_docs)
│   ├── metrics.py              # Расчёт метрик (Recall, MRR, NDCG)
│   └── auto_check.py           # Скрипт автопроверки (запуск и сверка с порогом)
└── experiments/
    ├── baseline_results.json   # Результаты базового пайплайна
    └── optimized_results.json  # Результаты оптимизированного пайплайна
```

### 4.3. Тестовый датасет (`evaluation/test_queries.json`)

```json
[
  {
    "query": "Как настроить FastAPI для асинхронной обработки?",
    "relevant_doc_ids": ["doc_fastapi_async.pdf", "doc_uvicorn_tips.txt"]
  },
  {
    "query": "Какие гиперпараметры влияют на сходимость SGD?",
    "relevant_doc_ids": ["doc_sgd_params.pdf", "doc_optimizers.md"]
  },
  ...
]
```

---

## 5. Пошаговая инструкция выполнения

### Шаг 1. Реализация BM25-ретривера

**Задача:** Реализовать лексический поиск на основе BM25.

```python
# src/hybrid_retriever.py
import os
import pickle
from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple

class BM25Retriever:
    def __init__(self):
        self.bm25 = None
        self.corpus = []
        self.metadata = []

    def fit(self, chunks: List[Dict]):
        """Индексирует чанки для BM25."""
        self.corpus = [chunk['text'] for chunk in chunks]
        self.metadata = chunks
        # Токенизация (простая, по пробелам и знакам препинания)
        tokenized_corpus = [self._tokenize(text) for text in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        """Простая токенизация для BM25."""
        import re
        # Приводим к нижнему регистру, удаляем пунктуацию
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()

    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        """Поиск top-k чанков по BM25."""
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        # Сортировка по убыванию скора
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in indexed_scores[:k]:
            results.append((self.metadata[idx], score))
        return results

    def get_all_scores(self, query: str) -> List[float]:
        """Возвращает скоринг BM25 для всех документов (для RRF)."""
        tokenized_query = self._tokenize(query)
        return self.bm25.get_scores(tokenized_query).tolist()
```

**Сохраняем BM25-индекс на диск:**

```python
def save_bm25_index(bm25_retriever, path: str):
    with open(f"{path}/bm25_corpus.pkl", 'wb') as f:
        pickle.dump(bm25_retriever.corpus, f)
    with open(f"{path}/bm25_metadata.pkl", 'wb') as f:
        pickle.dump(bm25_retriever.metadata, f)
    # BM25Okapi не сериализуется стандартно, поэтому сохраняем только данные
```

### Шаг 2. Реализация гибридного поиска с RRF

**Задача:** Объединить результаты Dense-поиска и BM25 с помощью RRF.

```python
# src/hybrid_retriever.py (продолжение)
from typing import List, Dict, Tuple
import numpy as np

class HybridRetriever:
    def __init__(self, dense_store, bm25_retriever, embedder, k_rrf: int = 60):
        """
        Args:
            dense_store: FAISS/Qdrant хранилище с методом search
            bm25_retriever: экземпляр BM25Retriever
            embedder: модель эмбеддингов для векторизации запроса
            k_rrf: константа для RRF (обычно 60)
        """
        self.dense_store = dense_store
        self.bm25 = bm25_retriever
        self.embedder = embedder
        self.k_rrf = k_rrf

    def search(self, query: str, k: int = 10, dense_weight: float = 0.5) -> List[Tuple[Dict, float]]:
        """
        Гибридный поиск с RRF.
        Args:
            query: запрос
            k: количество возвращаемых документов
            dense_weight: вес для плотного поиска (если нужна настройка)
        """
        # 1. Dense-поиск (получаем top-k * 3 для запаса)
        query_embedding = self.embedder.encode_query(query)
        dense_results = self.dense_store.search(query_embedding, k=k*3)
        dense_rank_map = {self._get_id(meta): rank for rank, (meta, score) in enumerate(dense_results)}

        # 2. BM25-поиск
        bm25_results = self.bm25.search(query, k=k*3)
        bm25_rank_map = {self._get_id(meta): rank for rank, (meta, score) in enumerate(bm25_results)}

        # 3. Объединение всех документов
        all_doc_ids = set(dense_rank_map.keys()) | set(bm25_rank_map.keys())

        # 4. Вычисление RRF-скора для каждого документа
        rrf_scores = {}
        for doc_id in all_doc_ids:
            score = 0.0
            if doc_id in dense_rank_map:
                score += 1.0 / (self.k_rrf + dense_rank_map[doc_id] + 1)
            if doc_id in bm25_rank_map:
                score += 1.0 / (self.k_rrf + bm25_rank_map[doc_id] + 1)
            rrf_scores[doc_id] = score

        # 5. Сортировка по RRF-скору
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:k]

        # 6. Извлечение метаданных
        id_to_meta = {self._get_id(meta): meta for meta in self.dense_store.metadata}
        results = []
        for doc_id, score in sorted_docs:
            if doc_id in id_to_meta:
                results.append((id_to_meta[doc_id], score))
        return results

    def _get_id(self, metadata: Dict) -> str:
        """Генерирует уникальный ID для чанка."""
        return f"{metadata.get('source', 'unknown')}_{metadata.get('chunk_index', 0)}"
```

### Шаг 3. Реализация реранкинга (Cross-Encoder)

**Задача:** Использовать cross-encoder для уточнения ранжирования топ-N документов.

```python
# src/reranker.py
from sentence_transformers import CrossEncoder
from typing import List, Dict, Tuple

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
        self.model_name = model_name

    def rerank(self, query: str, candidates: List[Tuple[Dict, float]], top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Переранжирует кандидатов с помощью cross-encoder.
        Args:
            query: запрос пользователя
            candidates: список кортежей (metadata, score) от первичного ретривера
            top_k: количество документов для реранжинга (берём top-N от candidates)
        Returns:
            Отреранжированный список кортежей (metadata, new_score)
        """
        if not candidates:
            return []

        # Берём только top-k для переранжирования (ускоряем)
        rerank_candidates = candidates[:min(len(candidates), 50)]

        # Формируем пары (query, document_text)
        pairs = [(query, meta['text']) for meta, _ in rerank_candidates]

        # Получаем скоринги от cross-encoder
        scores = self.model.predict(pairs)

        # Объединяем с метаданными и сортируем по новому скору (по убыванию)
        reranked = [(meta, float(score)) for (meta, _), score in zip(rerank_candidates, scores)]
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]
```

> **Оптимизация:** Cross-encoder медленный, поэтому **подаём только топ-50** документов от гибридного ретривера. Это стандартная индустриальная практика (two-stage retrieval).

### Шаг 4. Реализация Query Rewriting

**Задача:** Улучшить поисковый запрос с помощью LLM.

```python
# src/query_rewriter.py
import re
from typing import Optional

class QueryRewriter:
    def __init__(self, use_llm: bool = True, llm_model: str = "gpt-4o-mini"):
        self.use_llm = use_llm
        self.llm_model = llm_model
        self._cache = {}  # Простой кэш для повторяющихся запросов

    def rewrite(self, query: str) -> str:
        """Переформулирует запрос для улучшения поиска."""
        if not self.use_llm:
            return self._rule_based_rewrite(query)
        if query in self._cache:
            return self._cache[query]
        rewritten = self._llm_rewrite(query)
        self._cache[query] = rewritten
        return rewritten

    def _llm_rewrite(self, query: str) -> str:
        """Использует LLM для переформулировки."""
        from openai import OpenAI
        client = OpenAI()
        prompt = f"""Ты — эксперт по информационному поиску. Преобразуй следующий вопрос в оптимальный поисковый запрос для векторной базы данных.

Правила:
1. Сохрани все ключевые термины и сущности.
2. Раскрой аббревиатуры.
3. Удали лишние местоимения и разговорные обороты.
4. Если вопрос состоит из нескольких частей, разбей на несколько запросов (верни только лучший).
5. Выведи только итоговый запрос, без пояснений.

Исходный вопрос: {query}

Оптимизированный запрос:"""

        response = client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

    def _rule_based_rewrite(self, query: str) -> str:
        """Простая эвристическая переформулировка (без LLM)."""
        # Удаление лишних слов
        query = re.sub(r'как (настроить|сделать|использовать)', r'настройка', query)
        query = re.sub(r'что такое', '', query)
        query = re.sub(r'помогите с', '', query)
        return query.strip()
```

### Шаг 5. Сборка оптимизированного пайплайна

**Задача:** Интегрировать все компоненты в единый пайплайн.

```python
# src/pipeline_optimized.py
from src.hybrid_retriever import HybridRetriever
from src.reranker import CrossEncoderReranker
from src.query_rewriter import QueryRewriter
from src.embeddings import EmbeddingModel
from src.vector_store import FAISSVectorStore
from src.chunking import load_documents, chunk_text
from typing import Dict, List

class OptimizedRAGPipeline:
    def __init__(self, dense_store, bm25_retriever):
        self.dense_store = dense_store
        self.bm25_retriever = bm25_retriever
        self.embedder = EmbeddingModel()
        self.hybrid_retriever = HybridRetriever(dense_store, bm25_retriever, self.embedder)
        self.reranker = CrossEncoderReranker()
        self.rewriter = QueryRewriter(use_llm=True)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Полный пайплайн ретривала с оптимизациями."""
        # 1. Переформулировка запроса
        rewritten_query = self.rewriter.rewrite(query)
        # 2. Гибридный поиск (возвращает top-20 для реранкинга)
        candidates = self.hybrid_retriever.search(rewritten_query, k=20)
        # 3. Реранкинг cross-encoder
        reranked = self.reranker.rerank(rewritten_query, candidates, top_k=top_k)
        # 4. Возвращаем метаданные
        return [meta for meta, score in reranked]

    def answer(self, query: str, llm_model: str = "gpt-4o-mini") -> Dict:
        """Полный ответ с генерацией."""
        from src.generation import generate_answer
        from src.retrieval import retrieve_context

        # Получаем контекст
        context, sources = retrieve_context(query, self.embedder, self.dense_store, k=5)

        # Но используем оптимизированный поиск для контекста
        optimized_context_chunks = self.retrieve(query, top_k=5)
        optimized_context = "\n\n".join([chunk['text'] for chunk in optimized_context_chunks])
        optimized_sources = [{'source': c['source'], 'index': i} for i, c in enumerate(optimized_context_chunks)]

        # Генерация ответа
        result = generate_answer(query, optimized_context, optimized_sources)
        return result
```

### Шаг 6. Запуск метрической автопроверки

**Важно:** Это центральный элемент лабораторной работы. Студент запускает скрипт, который автоматически сравнивает метрики (Recall@k, MRR@k) базового пайплайна (лаба 2.2) и улучшенного (лаба 2.3).

**`evaluation/metrics.py`:**

```python
import numpy as np
from typing import List, Dict, Set

def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Доля релевантных документов в top-k."""
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    return len(retrieved_set & relevant_ids) / len(relevant_ids)

def mrr_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Обратный ранг первого релевантного документа."""
    for i, doc_id in enumerate(retrieved_ids[:k]):
        if doc_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0

def ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Normalized Discounted Cumulative Gain."""
    # Упрощённая версия: binary relevance
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k]):
        rel = 1.0 if doc_id in relevant_ids else 0.0
        dcg += rel / np.log2(i + 2)  # i+2 потому что log2(2)=1

    # IDCG (идеальный случай)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant_ids), k)))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_retriever(retriever_func, test_queries: List[Dict], k: int = 5) -> Dict:
    """Запускает оценку на тестовом наборе."""
    recalls, mrrs, ndcgs = [], [], []
    for test in test_queries:
        query = test['query']
        relevant = set(test['relevant_doc_ids'])
        # Получаем ID документов от ретривера
        retrieved_ids = retriever_func(query, k=k*3)  # берём с запасом
        retrieved_ids = [doc['source'] for doc in retrieved_ids]  # упрощённо
        recalls.append(recall_at_k(retrieved_ids, relevant, k))
        mrrs.append(mrr_at_k(retrieved_ids, relevant, k))
        ndcgs.append(ndcg_at_k(retrieved_ids, relevant, k))
    return {
        'recall@k': np.mean(recalls),
        'mrr@k': np.mean(mrrs),
        'ndcg@k': np.mean(ndcgs),
        'k': k
    }
```

**`evaluation/auto_check.py` (главный скрипт автопроверки):**

```python
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline_optimized import OptimizedRAGPipeline
from evaluation.metrics import evaluate_retriever

# 1. Загрузка тестовых запросов
with open('evaluation/test_queries.json', 'r') as f:
    test_queries = json.load(f)

# 2. Инициализация пайплайнов (загрузка индекса)
from src.vector_store import FAISSVectorStore
from src.embeddings import EmbeddingModel
from src.hybrid_retriever import BM25Retriever

# Загрузка подготовленных данных
vector_store = FAISSVectorStore(dimension=1024)
vector_store.load('index/')
embedder = EmbeddingModel()
bm25 = BM25Retriever()
bm25.fit(vector_store.metadata)  # Загружаем чанки

optimized = OptimizedRAGPipeline(vector_store, bm25)

# 3. Оценка Baseline (чистый Dense из лабораторной 2.2)
print("Оценка Baseline (Dense only)...")

def baseline_retriever(query, k):
    query_embedding = embedder.encode_query(query)
    return [meta for meta, score in vector_store.search(query_embedding, k=k)]

baseline_metrics = evaluate_retriever(baseline_retriever, test_queries, k=5)

# 4. Оценка Optimized (Hybrid + Rerank + Rewrite)
print("Оценка Optimized (Hybrid + Rerank + Rewrite)...")

def optimized_retriever(query, k):
    return optimized.retrieve(query, top_k=k)

optimized_metrics = evaluate_retriever(optimized_retriever, test_queries, k=5)

# 5. Сравнение и проверка порогов
print("\n=== РЕЗУЛЬТАТЫ АВТОПРОВЕРКИ ===")
print(f"Baseline Recall@5: {baseline_metrics['recall@k']:.4f}")
print(f"Optimized Recall@5: {optimized_metrics['recall@k']:.4f}")

improvement = (optimized_metrics['recall@k'] - baseline_metrics['recall@k']) / baseline_metrics['recall@k'] * 100

# ПРОВЕРКА: улучшение должно быть >= 15% ИЛИ абсолютный Recall@5 >= 0.85
threshold_improvement = 15.0
threshold_absolute = 0.85

# Сохранение результатов в JSON
results = {
    "baseline": baseline_metrics,
    "optimized": optimized_metrics,
    "improvement_percent": improvement,
    "pass": (improvement >= threshold_improvement) or (optimized_metrics['recall@k'] >= threshold_absolute)
}

with open('experiments/evaluation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Вывод результата автопроверки
if results["pass"]:
    print(f"\n✅ АВТОПРОВЕРКА ПРОЙДЕНА! Улучшение: {improvement:.1f}%")
    print("  (Порог: +15% ИЛИ абсолютный Recall@5 >= 0.85)")
    sys.exit(0)
else:
    print(f"\n❌ АВТОПРОВЕРКА НЕ ПРОЙДЕНА. Улучшение: {improvement:.1f}%")
    print("  Рекомендации: проверьте реализацию RRF, реранкинга и query rewriting.")
    sys.exit(1)
```

---

## 6. Отчёт по лабораторной работе

### 6.1. Требования к отчёту

1. **Титульный лист**.
2. **Цель работы**.
3. **Теоретическая часть**: краткое описание гибридного поиска, RRF, cross-encoder, query rewriting.
4. **Реализация**: листинг кода ключевых модулей (bm25, hybrid, reranker, rewriter).
5. **Эксперименты**:
   - Таблица сравнения метрик (Baseline vs Optimized).
   - График улучшения.
   - Вывод о влиянии каждой оптимизации (если проводили ablation study).
6. **Скриншот результата автопроверки** (терминал с выводом PASS/FAIL).
7. **Выводы**: какие техники дали наибольший прирост качества, какие компромиссы (latency vs accuracy) были выявлены.

### 6.2. Критерии оценки

| Критерий | Баллы |
|----------|-------|
| Реализован BM25-ретривер | 15 |
| Реализован гибридный поиск с RRF | 20 |
| Реализован реранкинг (cross-encoder) | 20 |
| Реализован query rewriting (любой вариант) | 15 |
| Собран оптимизированный пайплайн | 10 |
| Автопроверка пройдена (PASS) | 10 |
| Качественное оформление отчёта | 10 |
| **Итого** | **100** |

**Дополнительные бонусы:**

- +5: Ablation study (сравнение каждой техники по отдельности).
- +5: Использование Qdrant с нативным гибридным поиском.
- +5: Внедрение кэширования для query rewriting.

---

## 7. Типичные ошибки и рекомендации

| Ошибка | Решение |
|--------|---------|
| **RRF даёт худший результат, чем pure dense** | Проверьте k в RRF (обычно 60). Убедитесь, что BM25 корректно токенизирует русский язык (используйте nltk или pymorphy2). |
| **Cross-encoder слишком медленный** | Уменьшите количество кандидатов для реранкинга (например, с 50 до 20). Используйте модель -L-6-v2 вместо -L-12-v2. |
| **Query rewriting ухудшает поиск** | Проверьте промпт. Иногда LLM «переписывает» запрос до неузнаваемости. Установите temperature=0.1. |
| **Не проходит автопроверка** | Запустите Ablation Study: проверьте, какой компонент даёт отрицательный прирост. Возможно, BM25 индексирован неправильно. |
| **Размерность эмбеддингов** | Убедитесь, что вы используете одну и ту же модель эмбеддингов во всех экспериментах (для честного сравнения). |

---

## 8. Литература и источники

Фундаментальные работы по информационному поиску и ранжированию

Robertson, S., Zaragoza, H. The Probabilistic Relevance Framework: BM25 and Beyond // Foundations and Trends in Information Retrieval, 2009. — Vol. 3, No. 4. — P. 333–389. — DOI: 10.1561/1500000019 — https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf
Cormack, G.V., Clarke, C.L.A., Buettcher, S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods // Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR), 2009. — P. 758–759. — DOI: 10.1145/1571941.1572114 — https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/
Nogueira, R., Cho, K. Passage Re-ranking with BERT // arXiv preprint arXiv:1901.04085, 2019. — https://arxiv.org/abs/1901.04085
Nogueira, R., Yang, W., Cho, K., Lin, J. Multi-Stage Document Ranking with BERT // Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2020. — https://arxiv.org/abs/1910.14424
Khattab, O., Zaharia, M. ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT // Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR), 2020. — https://arxiv.org/abs/2004.12832

RAG и нейронный поиск

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.-t., Rocktäschel, T., Riedel, S., Kiela, D. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks // Advances in Neural Information Processing Systems (NeurIPS), 2020. — Vol. 33. — P. 9459–9474. — https://arxiv.org/abs/2005.11401
Guu, K., Lee, K., Tung, Z., Pasupat, P., Chang, M.W. REALM: Retrieval-Augmented Language Model Pre-Training // Proceedings of the 37th International Conference on Machine Learning (ICML), 2020. — P. 3929–3938. — https://arxiv.org/abs/2002.08909
Izacard, G., Lewis, P., Lomeli, M., Hosseini, L., Petroni, F., Schick, T., Dwivedi-Yu, J., Joulin, A., Riedel, S., Grave, E. Atlas: Few-shot Learning with Retrieval Augmented Language Models // Journal of Machine Learning Research (JMLR), 2023. — Vol. 24. — P. 1–43. — https://arxiv.org/abs/2208.03299
Asai, A., Wu, Z., Wang, Y., Sil, A., Hajishirzi, H. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection // Proceedings of the International Conference on Learning Representations (ICLR), 2024. — https://arxiv.org/abs/2310.11511
Jiang, Z., Xu, F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y., Callan, J., Neubig, G. Active Retrieval Augmented Generation // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 7969–7992. — https://arxiv.org/abs/2305.06983
Sarthi, P., Abdullah, S., Tuli, A., Khanna, S., Goldie, A., Manning, C.D. RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval // Proceedings of the International Conference on Learning Representations (ICLR), 2024. — https://arxiv.org/abs/2401.18059

Query Rewriting и оптимизация запросов

Ma, X., Gong, Y., He, P., Zhao, H., Duan, N. Query Rewriting for Retrieval-Augmented Large Language Models // arXiv preprint arXiv:2305.14283, 2023. — https://arxiv.org/abs/2305.14283
Gao, L., Ma, X., Lin, J., Callan, J. Precise Zero-Shot Dense Retrieval without Relevance Labels // Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL), 2023. — (HyDE — Hypothetical Document Embeddings) — https://arxiv.org/abs/2212.10496
Mao, S., Jiang, Y., Chen, B., Li, X., Wang, P., Wang, X., Xie, P., Huang, F., Chen, H., Zhang, N. RAFE: Ranking Feedback Improves Query Rewriting for RAG // arXiv preprint arXiv:2405.14431, 2024. — https://arxiv.org/abs/2405.14431
Wang, Y., Zhang, H., Pang, L., Zheng, H., Zheng, Z. MAFERW: Query Rewriting with Multi-Aspect Feedbacks for Retrieval-Augmented Large Language Models // arXiv preprint arXiv:2408.17072, 2024. — https://arxiv.org/abs/2408.17072
Sun, Z., Wang, Q., Yu, W., Zang, X., Zheng, K., Xu, J., Zhang, X., Song, Y., Li, H. Q-PRM: Adaptive Query Rewriting for Retrieval-Augmented Generation with Process Reward Model // Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP) — Findings, 2025. — https://aclanthology.org/2025.findings-emnlp.817.pdf

Гибридный поиск и query expansion

Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., Yih, W.-t. Dense Passage Retrieval for Open-Domain Question Answering // Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2020. — P. 6769–6781. — https://arxiv.org/abs/2004.04906
Xiong, L., Xiong, C., Li, Y., Tang, K.F., Liu, J., Bennett, P., Ahmed, J., Overwijk, A. Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval // Proceedings of the International Conference on Learning Representations (ICLR), 2021. — https://arxiv.org/abs/2007.00808
Gao, L., Callan, J. Unsupervised Corpus Aware Language Model Pre-training for Dense Passage Retrieval // Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL), 2022. — P. 2843–2853.
Ye, F., Fang, M., Li, S., Yilmaz, E. Corpus-Steered Query Expansion with Large Language Models // Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (EACL), 2024. — https://aclanthology.org/2024.eacl-short.34.pdf
Otero, D., et al. LLM-Assisted Pseudo-Relevance Feedback // Proceedings of the European Conference on Information Retrieval (ECIR), 2026. — https://arxiv.org/abs/2601.11238

Оценка качества и метрики

Liu, N.F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., Liang, P. Lost in the Middle: How Language Models Use Long Contexts // Transactions of the Association for Computational Linguistics (TACL), 2024. — Vol. 12. — P. 157–173. — https://arxiv.org/abs/2307.03172
Saad-Falcon, J., Khattab, O., Potts, C., Zaharia, M. ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems // Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL), 2024. — P. 338–354.
Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., Zhu, C. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 2511–2522. — https://arxiv.org/abs/2303.16634
Wang, L., Yang, N., Wei, F. Query2doc: Query Expansion with Large Language Models // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 9414–9423. — https://arxiv.org/abs/2303.07678
Chen, J., Lin, H., Han, X., Sun, L. Benchmarking Large Language Models in Retrieval-Augmented Generation // Proceedings of the AAAI Conference on Artificial Intelligence (AAAI), 2024. — Vol. 38. — P. 17754–17762.

Мультимодальный RAG и специализированные модели

Chen, W., He, H., Cheng, Y., Chang, M.W., Cohen, W.W., Wang, W.Y. MuRAG: Multimodal Retrieval-Augmented Generator for Open Question Answering over Images and Text // Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2022. — P. 5558–5570.
Patel, R.N., Dutta, S. ColBERT-Att: Late-Interaction Meets Attention for Enhanced Retrieval // arXiv preprint arXiv:2603.25248, 2026. — https://arxiv.org/abs/2603.25248

Обзоры

Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Guo, Q., Wang, M., Wang, H. Retrieval-Augmented Generation for Large Language Models: A Survey // arXiv preprint arXiv:2312.10997, 2023. — https://arxiv.org/abs/2312.10997
Mialon, G., Dessì, R., Lomeli, M., Nalmpantis, C., Pasunuru, R., Raileanu, R., Rozière, B., Schick, T., Dwivedi-Yu, J., Celikyilmaz, A., et al. Augmented Language Models: a Survey // Transactions on Machine Learning Research (TMLR), 2023.

---

## 9. Скрипт для проверки прохождения лабораторной (для преподавателя)

Преподаватель может запустить следующую команду для верификации:

```bash
python evaluation/auto_check.py
```

Ожидаемый вывод при успешном прохождении:

```
=== РЕЗУЛЬТАТЫ АВТОПРОВЕРКИ ===
Baseline Recall@5: 0.7234
Optimized Recall@5: 0.8912

✅ АВТОПРОВЕРКА ПРОЙДЕНА! Улучшение: 23.2%
  (Порог: +15% ИЛИ абсолютный Recall@5 >= 0.85)
```
