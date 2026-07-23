# МЕТОДИЧЕСКИЕ УКАЗАНИЯ ДЛЯ ВЫПОЛНЕНИЯ ЗАЩИТНОЙ РАБОТЫ 3.3

## «Оптимизированная агентная система с human-in-the-loop и оценкой стабильности»

### с метрической автопроверкой качества

по дисциплине **«Инженерия систем на базе больших языковых моделей»**

**Модуль 3. Harness Engineering (Агенты, инструменты и адаптация)**

---

## 01. Общие сведения

**КИМ-3.3** — итоговая защитная работа модуля 3. Студенты дорабатывают агентную систему из КИМ-3.1 и КИМ-3.2, добавляя механизмы оптимизации (кэширование, batch-обработка), безопасности (human-in-the-loop) и оценки стабильности в стресс-сценариях. Работа завершается защитой перед комиссией.

**Форма контроля:** Промежуточная
**Время выполнения:** 4 академических часа + самостоятельная работа
**Проверяемые индикаторы:** LLM-4 (4.1–4.5)

---

## 02. Цели и задачи работы

### 2.1. Цели
- Научиться оптимизировать агентные системы для промышленной эксплуатации
- Освоить механизмы human-in-the-loop для контроля критических действий
- Получить опыт оценки стабильности системы в стресс-сценариях
- Развить навыки презентации технического решения перед комиссией

### 2.2. Задачи
1. Реализовать механизм кэширования для повторяющихся запросов
2. Внедрить human-in-the-loop для критических действий (утверждение перед выполнением)
3. Провести нагрузочное тестирование и оценить стабильность (latency, success rate, error rate)
4. Выполнить ablation study (сравнение baseline vs optimized)
5. Подготовить отчёт (10-15 стр.) и презентацию (до 10 слайдов)
6. Защитить работу перед комиссией

---

## 03. Теоретическое введение

### 3.1. Оптимизация агентных систем

**Кэширование:**
- Semantic cache — кэширование по семантическому сходству запросов
- Result cache — кэширование результатов вызовов инструментов
- Prompt cache — кэширование промптов для LLM

**Batch-обработка:**
- Объединение нескольких запросов в один batch для LLM
- Параллельное выполнение независимых инструментов

**Модельный routing:**
- Направление простых запросов к маленькой/дешёвой модели
- Сложные запросы — к большой модели

### 3.2. Human-in-the-loop

**Паттерны утверждения:**
- **Pre-action approval** — агент запрашивает разрешение перед выполнением критического действия
- **Post-action review** — результаты проверяются человеком после выполнения
- **Escalation** — передача управления человеку при превышении порога неуверенности

**Реализация:**
```python
def requires_approval(action, confidence):
    critical_actions = ["delete", "send_email", "payment", "update_record"]
    if action in critical_actions and confidence < 0.8:
        return True
    return False

def get_human_approval(action_details):
    # В реальном приложении — запрос через UI/чат
    response = input(f"Утвердить действие: {action_details}? (y/n): ")
    return response.lower() == 'y'
```

### 3.3. Оценка стабильности

**Метрики:**
- **Latency** — время ответа агента (p50, p95, p99)
- **Success rate** — процент успешно выполненных задач
- **Error rate** — процент ошибок (по типам: timeout, API error, LLM error)
- **Token usage** — потребление токенов (cost per query)
- **Stability score** — комбинация метрик

**Стресс-сценарии:**
- Таймауты API
- Недоступность инструментов
- Некорректный ввод пользователя
- Высокая параллельная нагрузка

---

## 04. Требования к программному обеспечению

### 4.1. Дополнительные зависимости
```bash
pip install redis  # для кэширования
pip install locust  # для нагрузочного тестирования
pip install matplotlib pandas  # для визуализации метрик
```

### 4.2. Структура проекта (финальная)
```
production_agent/
├── main.py
├── agent.py
├── memory/
├── tools.py
├── prompts.py
├── optimization/
│   ├── __init__.py
│   ├── cache.py            # Semantic cache
│   ├── model_router.py     # Модельный routing
│   └── batch_processor.py  # Batch-обработка
├── safety/
│   ├── __init__.py
│   ├── human_in_loop.py    # Human-in-the-loop
│   ├── confidence.py       # Оценка уверенности
│   └── guardrails.py       # Guardrails
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py          # Сбор метрик
│   └── stress_test.py      # Нагрузочное тестирование
├── logging_config.py
├── error_handling.py
├── test_memory.py
├── stress_test_report.py   # Генерация отчёта
├── report.pdf
├── presentation.pdf
└── README.md
```

---

## 05. Пошаговая инструкция выполнения

### Шаг 1. Реализация кэширования

```python
import hashlib
from redis import Redis

class SemanticCache:
    def __init__(self, embedder, redis_url="redis://localhost:6379", ttl=3600):
        self.embedder = embedder
        self.redis = Redis.from_url(redis_url)
        self.ttl = ttl
        self.similarity_threshold = 0.95
    
    def get(self, query):
        query_embedding = self.embedder.embed(query)
        # Ищем похожие запросы в кэше
        cached = self._find_similar(query_embedding)
        if cached:
            return cached
        return None
    
    def set(self, query, response):
        key = hashlib.md5(query.encode()).hexdigest()
        self.redis.setex(key, self.ttl, json.dumps({
            "query": query,
            "response": response,
            "timestamp": time.time()
        }))
    
    def _find_similar(self, query_embedding):
        # Упрощённая реализация — в реальности нужен векторный поиск
        for key in self.redis.scan_iter():
            cached_data = json.loads(self.redis.get(key))
            cached_embedding = self.embedder.embed(cached_data["query"])
            similarity = self._cosine_similarity(query_embedding, cached_embedding)
            if similarity >= self.similarity_threshold:
                return cached_data["response"]
        return None
```

### Шаг 2. Human-in-the-loop

```python
class HumanInTheLoop:
    def __init__(self, critical_actions=None, confidence_threshold=0.8):
        self.critical_actions = critical_actions or [
            "delete", "send_email", "payment", "update_record", "send_message"
        ]
        self.confidence_threshold = confidence_threshold
    
    def should_approve(self, action, confidence, context):
        if action not in self.critical_actions:
            return True  # Не требует утверждения
        if confidence >= self.confidence_threshold:
            return True  # Высокая уверенность
        return self._request_approval(action, context)
    
    def _request_approval(self, action, context):
        # В учебной версии — input(); в production — UI/чат
        print(f"\n⚠️  ТРЕБУЕТСЯ УТВЕРЖДЕНИЕ")
        print(f"Действие: {action}")
        print(f"Контекст: {context}")
        response = input("Утвердить? (y/n): ")
        return response.lower() in ['y', 'yes', 'д', 'да']
    
    def escalate_to_human(self, reason, context):
        print(f"\n🚨 ЭСКАЛАЦИЯ К ЧЕЛОВЕКУ")
        print(f"Причина: {reason}")
        print(f"Контекст: {context}")
        return "ESCALATED"
```

### Шаг 3. Нагрузочное тестирование

Создайте `stress_test.py` на базе Locust:

```python
from locust import HttpUser, task, between
import random

class AgentStressTest(HttpUser):
    wait_time = between(0.5, 2)
    
    test_queries = [
        "Какая погода сегодня?",
        "Найди информацию о компании X",
        "Отправь email клиенту",
        "Удали запись из базы данных",
        "Что было вчера на встрече?",
        # ... 20+ запросов
    ]
    
    @task(3)
    def simple_query(self):
        query = random.choice(self.test_queries[:10])  # Простые запросы
        self.client.post("/agent/query", json={"query": query})
    
    @task(1)
    def critical_query(self):
        query = random.choice(self.test_queries[10:])  # Критические запросы
        self.client.post("/agent/query", json={"query": query})
```

Запуск:
```bash
locust -f stress_test.py --host http://localhost:8000
```

### Шаг 4. Сбор и визуализация метрик

```python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_stress_test_results(results_file):
    df = pd.read_json(results_file)
    
    # Latency
    latency_stats = {
        "p50": df["latency"].quantile(0.5),
        "p95": df["latency"].quantile(0.95),
        "p99": df["latency"].quantile(0.99),
        "mean": df["latency"].mean()
    }
    
    # Success rate
    success_rate = (df["status"] == "success").mean()
    error_rate = 1 - success_rate
    
    # Error breakdown
    error_types = df[df["status"] == "error"]["error_type"].value_counts()
    
    # Token usage
    avg_tokens = df["tokens_used"].mean()
    
    print(f"Latency (p50/p95/p99): {latency_stats['p50']:.0f}/{latency_stats['p95']:.0f}/{latency_stats['p99']:.0f} ms")
    print(f"Success rate: {success_rate:.1%}")
    print(f"Error rate: {error_rate:.1%}")
    print(f"Avg tokens per query: {avg_tokens:.0f}")
    
    # Графики
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Latency distribution
    axes[0, 0].hist(df["latency"], bins=50)
    axes[0, 0].set_title("Latency Distribution")
    axes[0, 0].set_xlabel("Latency (ms)")
    
    # Latency over time
    axes[0, 1].plot(df["timestamp"], df["latency"])
    axes[0, 1].set_title("Latency Over Time")
    
    # Error types
    error_types.plot(kind='bar', ax=axes[1, 0])
    axes[1, 0].set_title("Error Types")
    
    # Token usage
    axes[1, 1].hist(df["tokens_used"], bins=50)
    axes[1, 1].set_title("Token Usage Distribution")
    
    plt.tight_layout()
    plt.savefig("stress_test_report.png")
    
    return latency_stats, success_rate, error_types
```

### Шаг 5. Ablation Study

Сравните baseline (без оптимизаций) и optimized версию:

```python
def ablation_study(test_queries, baseline_agent, optimized_agent):
    results = {"baseline": [], "optimized": []}
    
    for query in test_queries:
        # Baseline
        start = time.time()
        baseline_response = baseline_agent.run(query)
        baseline_time = time.time() - start
        results["baseline"].append({
            "time": baseline_time,
            "tokens": count_tokens(baseline_response),
            "success": baseline_response is not None
        })
        
        # Optimized
        start = time.time()
        optimized_response = optimized_agent.run(query)
        optimized_time = time.time() - start
        results["optimized"].append({
            "time": optimized_time,
            "tokens": count_tokens(optimized_response),
            "success": optimized_response is not None
        })
    
    # Сравнение
    baseline_avg_time = sum(r["time"] for r in results["baseline"]) / len(results["baseline"])
    optimized_avg_time = sum(r["time"] for r in results["optimized"]) / len(results["optimized"])
    
    speedup = baseline_avg_time / optimized_avg_time
    print(f"Speedup: {speedup:.2f}x")
    print(f"Baseline avg time: {baseline_avg_time:.2f}s")
    print(f"Optimized avg time: {optimized_avg_time:.2f}s")
```

---

## 06. Отчёт по защитной работе

### 6.1. Требования к отчёту

**Формат:** PDF, 10-15 страниц

**Структура:**
1. Титульный лист
2. Обзор архитектуры (1-2 стр.)
3. Оптимизации (кэш, routing, batch) — описание и код (2-3 стр.)
4. Human-in-the-loop — реализация и примеры (2 стр.)
5. Стресс-тестирование — методология и результаты (2-3 стр.)
6. Ablation study — сравнение baseline vs optimized (2 стр.)
7. Экономический анализ (стоимость, ROI оптимизаций) (1 стр.)
8. Выводы и roadmap развития (1 стр.)

### 6.2. Презентация

**Формат:** PDF/PPTX, до 10 слайдов

**Структура:**
1. Титульный слайд
2. Проблема и подход (1 слайд)
3. Архитектура системы (1 слайд)
4. Ключевые оптимизации (1-2 слайда)
5. Результаты стресс-теста (1-2 слайда)
6. Ablation study (1 слайд)
7. Экономика (1 слайд)
8. Выводы (1 слайд)

### 6.3. Защита

**Регламент:**
- Презентация: 5-7 минут
- Живая демонстрация: 3-5 минут (включая стресс-сценарии)
- Вопросы комиссии: 5-10 минут

**Демонстрация должна включать:**
1. Обычный запрос → ответ агента
2. Критическое действие → human-in-the-loop утверждение
3. Стресс-сценарий (timeout API) → graceful degradation
4. Кэширование → повторный запрос из кэша

### 6.4. Критерии оценки

| Критерий | Вес | Описание |
|----------|-----|----------|
| Корректность реализации | 25% | Все механизмы работают корректно |
| Качество экспериментов | 20% | Репрезентативные тесты, корректные метрики |
| Анализ компромиссов | 20% | Понимание trade-offs (latency vs accuracy vs cost) |
| Инженерное мышление | 15% | Обоснованность решений, учёт production-требований |
| Оформление | 10% | Качество отчёта и презентации |
| Код | 10% | Чистота, тесты, документация |

---

## 07. Типичные ошибки и рекомендации

**Ошибка 1:** Кэш возвращает устаревшие данные
**Рекомендация:** Используйте TTL (time-to-live) и инвалидацию кэша при изменении данных.

**Ошибка 2:** Human-in-the-loop замедляет все запросы
**Рекомендация:** Применяйте утверждение только к критическим действиям с низкой уверенностью.

**Ошибка 3:** Стресс-тест не репрезентативен
**Рекомендация:** Используйте реалистичные паттерны нагрузки и разнообразные запросы.

**Ошибка 4:** Ablation study некорректна
**Рекомендация:** Тестируйте baseline и optimized на одинаковом датасете, фиксируйте все переменные.

---

## 08. Литература и источники

1. Gao, L., et al. "Making Language Models Better Tool Learners with Execution Feedback." ACL 2023.
2. Shinn, N., et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023.
3. Locust Documentation: https://docs.locust.io/
4. LangChain Human-in-the-loop: https://python.langchain.com/docs/expression_language/cookbook/human_in_the_loop

---

## 09. Варианты заданий

### Общая структура
1. Оптимизация (кэш + routing)
2. Human-in-the-loop
3. Стресс-тестирование
4. Ablation study
5. Защита

### Вариант 1. Базовая оптимизация
- Кэш: simple key-value (Redis)
- HITL: pre-action approval для 3 критических действий
- Стресс-тест: 10 пользователей, 5 минут

### Вариант 2. Semantic cache
- Кэш: semantic similarity (cosine > 0.95)
- HITL: pre-action + confidence threshold
- Стресс-тест: 20 пользователей, 10 минут

### Вариант 3. Полный оптимизированный агент (продвинутый)
- Кэш: semantic + result + prompt
- Model routing: gpt-3.5 для простых, gpt-4 для сложных
- HITL: все три паттерна
- Стресс-тест: 50 пользователей, 15 минут, с инъекциями ошибок
- Ablation study: 4 конфигурации
