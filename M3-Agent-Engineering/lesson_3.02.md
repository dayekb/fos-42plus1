# МЕТОДИЧЕСКИЕ УКАЗАНИЯ ДЛЯ ВЫПОЛНЕНИЯ ЛАБОРАТОРНОЙ РАБОТЫ 3.2

## «Реализация агента с памятью и обработкой ошибок»

### с метрической автопроверкой качества

по дисциплине **«Инженерия систем на базе больших языковых моделей»**

**Модуль 3. Harness Engineering (Агенты, инструменты и адаптация)**

---

## 01. Общие сведения

**КИМ-3.2** — лабораторная работа, направленная на реализацию LLM-агента с краткосрочной и долгосрочной памятью, журналированием и обработкой ошибок. Работа является развитием КИМ-3.1: студенты берут за основу свой прототип агента и расширяют его системой памяти.

**Форма контроля:** Рубежная
**Время выполнения:** 2 академических часа + самостоятельная работа
**Проверяемые индикаторы:** LLM-4 (4.1, 4.2, 4.4)

---

## 02. Цели и задачи работы

### 2.1. Цели
- Научиться реализовывать системы памяти для LLM-агентов
- Освоить техники журналирования и обработки ошибок в агентных системах
- Получить опыт автоматической проверки качества через метрические скрипты

### 2.2. Задачи
1. Реализовать краткосрочную память (conversation history) с управлением размером окна
2. Реализовать долгосрочную память на основе векторного хранилища (Qdrant/ChromaDB)
3. Настроить журналирование (structured logging) всех шагов агента
4. Реализовать обработку ошибок (retry с экспоненциальной задержкой, fallback)
5. Запустить метрическую автопроверку (скрипт `test_memory.py`)
6. Подготовить отчёт с демонстрацией работы

---

## 03. Теоретическое введение

### 3.1. Типы памяти агента

**Краткосрочная память (Short-term Memory):**
- Хранит текущий диалог (последние N сообщений)
- Позволяет агенту поддерживать контекст беседы
- Реализуется как список или буфер с фиксированным размером

**Долгосрочная память (Long-term Memory):**
- Хранит важную информацию между сессиями
- Позволяет агенту «вспоминать» прошлый опыт
- Реализуется через векторные хранилища (semantic search)

**Рабочая память (Working Memory):**
- Хранит промежуточные результаты текущего рассуждения
- Очищается после завершения задачи
- Включает scratchpad для заметок агента

### 3.2. Стратегии управления памятью

**Sliding Window:** хранить только последние K сообщений (простая стратегия)

**Summarization:** периодически суммаризировать старые сообщения (экономия токенов)

**Semantic Retrieval:** извлекать из долгосрочной памяти только релевантные фрагменты

**Hybrid:** комбинировать несколько стратегий

### 3.3. Обработка ошибок

**Retry с экспоненциальной задержкой:**
```python
import time

def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
```

**Fallback-стратегии:**
- При ошибке LLM — использовать более дешёвую модель
- При недоступности API — вернуть кэшированный ответ
- При превышении таймаута — вернуть частичный результат

### 3.4. Структурированное логирование

```python
import logging
import json

logger = logging.getLogger("agent")

def log_agent_step(step_type, data):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "step_type": step_type,  # "thought", "action", "observation"
        "data": data
    }
    logger.info(json.dumps(log_entry))
```

---

## 04. Требования к программному обеспечению

### 4.1. Дополнительные зависимости
```bash
pip install qdrant-client chromadb langchain-community
pip install tenacity  # для retry с backoff
```

### 4.2. Структура проекта (дополнение к КИМ-3.1)
```
agent_with_memory/
├── main.py
├── agent.py             # Расширенная реализация агента
├── memory/
│   ├── __init__.py
│   ├── short_term.py    # Краткосрочная память
│   ├── long_term.py     # Долгосрочная память (vector store)
│   └── manager.py       # Менеджер памяти
├── tools.py
├── prompts.py
├── logging_config.py    # Настройка логирования
├── error_handling.py    # Обработка ошибок
├── test_memory.py       # Скрипт метрической автопроверки
├── architecture.pdf
└── README.md
```

### 4.3. Тестовый датасет

Для проверки памяти подготовьте набор из 20 тестовых сценариев:
- 10 сценариев на краткосрочную память (многоходовые диалоги)
- 10 сценариев на долгосрочную память (вопросы о прошлых событиях)

---

## 05. Пошаговая инструкция выполнения

### Шаг 1. Реализация краткосрочной памяти

```python
class ShortTermMemory:
    def __init__(self, max_size=10):
        self.messages = []
        self.max_size = max_size
    
    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]
    
    def get_context(self):
        return self.messages.copy()
    
    def summarize_old_messages(self, llm, keep_last=3):
        if len(self.messages) <= keep_last:
            return
        old = self.messages[:-keep_last]
        summary_prompt = f"Summarize the following conversation: {old}"
        summary = llm.invoke(summary_prompt)
        self.messages = [{"role": "system", "content": f"Summary: {summary}"}] + self.messages[-keep_last:]
```

### Шаг 2. Реализация долгосрочной памяти

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class LongTermMemory:
    def __init__(self, collection_name="agent_memory"):
        self.client = QdrantClient(":memory:")  # или URL сервера
        self.collection_name = collection_name
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
    
    def store(self, content, embedding):
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": self._get_next_id(),
                "vector": embedding,
                "payload": {"content": content, "timestamp": time.time()}
            }]
        )
    
    def retrieve(self, query_embedding, top_k=3):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        return [r.payload["content"] for r in results]
```

### Шаг 3. Менеджер памяти

```python
class MemoryManager:
    def __init__(self, llm, embedder):
        self.short_term = ShortTermMemory(max_size=10)
        self.long_term = LongTermMemory()
        self.llm = llm
        self.embedder = embedder
    
    def add_message(self, role, content):
        self.short_term.add(role, content)
        # Сохраняем важные сообщения в долгосрочную память
        if self._is_important(content):
            embedding = self.embedder.embed(content)
            self.long_term.store(content, embedding)
    
    def get_context(self, query):
        short_context = self.short_term.get_context()
        query_embedding = self.embedder.embed(query)
        long_context = self.long_term.retrieve(query_embedding, top_k=3)
        return short_context, long_context
    
    def _is_important(self, content):
        # Эвристика: важные сообщения содержат конкретные факты
        keywords = ["запомни", "важно", "предпочитаю", "аллергия", "не люблю"]
        return any(kw in content.lower() for kw in keywords)
```

### Шаг 4. Реализация журналирования

```python
import logging
import json
from datetime import datetime

class AgentLogger:
    def __init__(self, log_file="agent_logs.jsonl"):
        self.log_file = log_file
        self.logger = logging.getLogger("agent")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_step(self, step_type, data, metadata=None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step_type": step_type,
            "data": data,
            "metadata": metadata or {}
        }
        self.logger.info(json.dumps(entry, ensure_ascii=False))
    
    def log_error(self, error, context):
        self.log_step("error", str(error), {"context": context})
```

### Шаг 5. Обработка ошибок

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ErrorHandler:
    def __init__(self, logger):
        self.logger = logger
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def call_with_retry(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.log_error(e, {"func": func.__name__})
            raise
    
    def fallback(self, error, context):
        # Возвращаем безопасный ответ по умолчанию
        return {
            "answer": "Извините, произошла ошибка. Попробуйте ещё раз.",
            "error_type": type(error).__name__,
            "context": context
        }
```

### Шаг 6. Интеграция в агента

Обновите класс агента из КИМ-3.1, добавив:
- Вызов `memory_manager.add_message()` на каждом шаге
- Вызов `memory_manager.get_context()` перед генерацией ответа
- Вызов `agent_logger.log_step()` для каждого действия
- Обёртку вызовов инструментов через `error_handler.call_with_retry()`

### Шаг 7. Метрическая автопроверка

Создайте скрипт `test_memory.py`:

```python
def test_short_term_memory(agent, test_cases):
    """Проверяет, что агент помнит последние сообщения"""
    score = 0
    for case in test_cases:
        for msg in case["messages"]:
            agent.run(msg["user"])
        response = agent.run(case["question"])
        if case["expected"] in response:
            score += 1
    return score / len(test_cases)

def test_long_term_memory(agent, test_cases):
    """Проверяет, что агент вспоминает информацию из прошлых сессий"""
    score = 0
    for case in test_cases:
        # Сохраняем информацию
        agent.run(case["store_message"])
        # Спрашиваем позже
        response = agent.run(case["query"])
        if case["expected"] in response:
            score += 1
    return score / len(test_cases)

def test_error_handling(agent, test_cases):
    """Проверяет, что агент не падает при ошибках"""
    success = 0
    for case in test_cases:
        try:
            response = agent.run(case["input"])
            if response is not None:
                success += 1
        except Exception:
            pass
    return success / len(test_cases)

if __name__ == "__main__":
    # Загружаем тестовые случаи
    short_term_cases = [...]  # 10 кейсов
    long_term_cases = [...]   # 10 кейсов
    error_cases = [...]       # 10 кейсов
    
    short_score = test_short_term_memory(agent, short_term_cases)
    long_score = test_long_term_memory(agent, long_term_cases)
    error_score = test_error_handling(agent, error_cases)
    
    print(f"Short-term memory accuracy: {short_score:.2%}")
    print(f"Long-term memory accuracy: {long_score:.2%}")
    print(f"Error handling success rate: {error_score:.2%}")
    
    # Порог для зачёта: каждый показатель >= 0.85
    assert short_score >= 0.85, f"Short-term memory: {short_score:.2%} < 85%"
    assert long_score >= 0.85, f"Long-term memory: {long_score:.2%} < 85%"
    assert error_score >= 0.85, f"Error handling: {error_score:.2%} < 85%"
    print("ALL TESTS PASSED")
```

---

## 06. Отчёт по лабораторной работе

### 6.1. Требования к отчёту

**Формат:** PDF, 8-12 страниц

**Структура:**
1. Титульный лист
2. Архитектура системы памяти (блок-схема, 1-2 стр.)
3. Реализация краткосрочной памяти (код + описание стратегии, 2 стр.)
4. Реализация долгосрочной памяти (код + описание, 2 стр.)
5. Логирование и обработка ошибок (примеры логов, 2 стр.)
6. Результаты метрической проверки (таблицы, 1-2 стр.)
7. Примеры работы (3+ сценария с логами, 2-3 стр.)
8. Выводы

**Код:** ссылка на GitHub

### 6.2. Критерии оценки

| Критерий | Вес | Описание |
|----------|-----|----------|
| Краткосрочная память | 20% | Корректная реализация, управление размером |
| Долгосрочная память | 25% | Векторный поиск, релевантность извлечения |
| Журналирование | 15% | Структурированные логи, удобство анализа |
| Обработка ошибок | 15% | Retry, fallback, корректная обработка |
| Метрическая проверка | 15% | Автопроверка пройдена, результаты задокументированы |
| Отчёт и код | 10% | Качество документации и кода |

**Требование для зачёта:** метрическая автопроверка (`test_memory.py`) должна пройти с показателями ≥ 85% по всем трём категориям.

---

## 07. Типичные ошибки и рекомендации

**Ошибка 1:** Память переполняется, агент теряет контекст
**Рекомендация:** Реализуйте суммаризацию старых сообщений или используйте semantic retrieval вместо хранения всех сообщений.

**Ошибка 2:** Долгосрочная память возвращает нерелевантные результаты
**Рекомендация:** Используйте качественные эмбеддинги и настройте threshold для косинусного расстояния.

**Ошибка 3:** Retry без backoff приводит к перегрузке API
**Рекомендация:** Всегда используйте экспоненциальную задержку и джиттер (случайную добавку).

**Ошибка 4:** Логи нечитаемы
**Рекомендация:** Используйте структурированный формат (JSON) и добавляйте контекст (session_id, user_id).

---

## 08. Литература и источники

1. Park, J.S., et al. "Generative Agents: Interactive Simulacra of Human Behavior." UIST 2023.
2. MemGPT: Towards LLMs as Operating Systems. arXiv:2310.08560.
3. Qdrant Documentation: https://qdrant.tech/documentation/
4. Tenacity Library: https://tenacity.readthedocs.io/

---

## 09. Варианты заданий к лабораторной работе

### Общая структура (для всех вариантов)
1. Реализация краткосрочной памяти
2. Реализация долгосрочной памяти
3. Настройка логирования
4. Обработка ошибок
5. Метрическая проверка

### Вариант 1. Базовая память (Sliding Window + Vector Store)
- Краткосрочная: sliding window с max_size=10
- Долгосрочная: Qdrant in-memory, топ-3 релевантных
- Обработка: простой retry (3 попытки)

### Вариант 2. Суммаризация + Qdrant
- Краткосрочная: суммаризация через LLM (оставлять 3 последних)
- Долгосрочная: Qdrant с кастомным порогом релевантности
- Обработка: retry с exponential backoff

### Вариант 3. ChromaDB + Redis
- Краткосрочная: Redis (in-memory cache)
- Долгосрочная: ChromaDB с метаданными (тип, важность)
- Обработка: retry + fallback на кэш

### Вариант 4. Мульти-память (Episodic + Semantic + Procedural)
- Episodic: конкретные события (vector store)
- Semantic: общие факты (key-value store)
- Procedural: навыки (skill library)
- Обработка: полная с fallback-логикой

### Вариант 5. Полная реализация + Ablation Study (продвинутый)
- Реализовать 3 стратегии памяти
- Сравнить их эффективность (ablation study)
- Обосновать выбор лучшей стратегии

### Сравнительная таблица вариантов

| Вариант | Сложность | Векторное хранилище | Стратегия | Особенности |
|---------|-----------|---------------------|-----------|-------------|
| 1 | Базовая | Qdrant | Sliding Window | Простая реализация |
| 2 | Средняя | Qdrant | Summarization | Экономия токенов |
| 3 | Средняя | ChromaDB | Redis cache | Быстрый доступ |
| 4 | Высокая | Mixed | Multi-type | 3 типа памяти |
| 5 | Продвинутая | Qdrant | Ablation | Сравнительный анализ |

