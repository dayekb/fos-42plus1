### Структура защиты

#### Этап 1. Презентация библиотеки промптов

**Что продемонстрировать:**

**Структура хранилища:**
1. Дерево каталогов.
2. Система версионирования (semver: MAJOR.MINOR.PATCH).
3. Метаданные и теги.
4. Документация (README, примеры).

**Демонстрация 5+ промптов разных типов:**
1. Системный промпт (роль агента).
2. Пользовательский промпт (шаблон запроса).
3. Условный промпт (ветвление логики).
4. Мультимодальный промпт (работа с изображениями).
5. Оценочный промпт (evaluation / judge).

**Обоснование архитектурных решений:**
1. Почему выбрана такая структура.
2. Как обеспечивается переиспользование.
3. Как работает версионирование.
4. Как организовано тестирование.

**Пример структуры презентации:**

> **Библиотека промптов MedRocket**
> 
> **Архитектура**
> - Модульная структура по типам задач
> - Семантическое версионирование (semver)
> - YAML-формат с метаданными
> - Git-based хранение
> 
> **Примеры промптов**
> 1. `classifier/document_type_v1.3.yaml`
> 2. `extractor/medical_entities_v2.1.yaml`
> 3. `conditional/route_by_doc_type_v1.0.yaml`
> 4. `multimodal/image_quality_v1.1.yaml`
> 5. `evaluator/confidence_score_v1.0.yaml`
> 
> **Тестирование**
> - 47 тестовых кейсов
> - Покрытие: 94%
> - Quality score: 0.91

---

#### Этап 2. Демонстрация условного пайплайна

**Что продемонстрировать:**

**Работа пайплайна с активными Feature Flags:**
1. Показать live-демо обработки запроса.
2. Переключить Feature Flag → показать изменение поведения.
3. Объяснить механизм динамического переключения.

**Обработка ошибок и fallback-сценарии:**
1. Симулировать ошибку API.
2. Показать срабатывание fallback-модели.
3. Продемонстрировать circuit breaker.

**Логирование и трассировка:**
1. Показать логи выполнения.
2. Трассировка принятия решений агентом.
3. Метрики производительности.

**Пример демонстрации:**
```python
# Демонстрация работы с Feature Flags
print("=== Сценарий 1: Мультимодальная обработка ===")
feature_flags.enable("multimodal_processing")
result = pipeline.process(image)
print(f"Использована модель: {result.model_used}")
# Вывод: Использована модель: gpt-4-vision

print("\n=== Сценарий 2: Fallback при ошибке ===")
feature_flags.disable("multimodal_processing")
feature_flags.enable("fallback_to_gpt35")
result = pipeline.process(image)
print(f"Использована модель: {result.model_used}")
# Вывод: Использована модель: gpt-3.5-turbo (fallback)

print("\n=== Сценарий 3: Circuit Breaker ===")
# Симулируем 5 ошибок подряд
for i in range(5):
    simulate_api_error()
print(f"Circuit state: {circuit_breaker.state}")
# Вывод: Circuit state: OPEN (временно отключено)
```

---

#### Этап 3. Код-ревью

**Что продемонстрировать:**

**Качество кода:**
1. Читаемость и именование.
2. Модульность (SRP — Single Responsibility Principle).
3. Отсутствие дублирования.
4. Комментарии и docstrings.

**Автоматические тесты:**
1. Минимум 5 тест-кейсов.
2. Unit-тесты для промптов.
3. Интеграционные тесты для пайплайнов.
4. Покрытие кода.

**CI/CD-пайплайн:**
1. Автоматические проверки при commit.
2. Тестирование на тестовых кейсах.
3. Canary-развертывание.
4. Откат при падении метрик.

**Пример тест-кейса:**
```python
def test_document_classifier():
    """Тест классификации медицинского документа"""
    prompt = load_prompt("classifier/document_type_v1.3")
    test_cases = [
        {
            "input": "image_recipe.jpg",
            "expected": "recipe",
            "min_confidence": 0.85
        },
        {
            "input": "image_conclusion.jpg",
            "expected": "conclusion",
            "min_confidence": 0.80
        },
        {
            "input": "image_analyses.jpg",
            "expected": "analyses",
            "min_confidence": 0.90
        }
    ]
    for case in test_cases:
        result = execute_prompt(prompt, case["input"])
        assert result["document_type"] == case["expected"]
        assert result["confidence"] >= case["min_confidence"]
```

**Пример CI/CD конфигурации:**
```yaml
# .github/workflows/prompt-ci.yml
name: Prompt CI/CD
on:
  push:
    paths:
      - 'prompts/**'
      - 'tests/**'
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate prompt syntax
        run: python scripts/validate_prompts.py
      - name: Run prompt tests
        run: pytest tests/ -v --cov=prompts
      - name: Check quality metrics
        run: python scripts/check_quality.py --threshold 0.85
  canary:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to canary
        run: python scripts/deploy_canary.py
      - name: A/B test metrics
        run: python scripts/ab_test.py --duration 1h
      - name: Promote or rollback
        run: python scripts/promote_or_rollback.py
```

---

#### Этап 4. Ответы на вопросы

**Типичные вопросы комиссии:**

**Архитектурные решения:**
1. Почему выбрана такая структура библиотеки?
2. Как обеспечивается масштабируемость?
3. Какие альтернативы рассматривались?

**Безопасность:**
1. Как обеспечивается защита от промпт-инъекций?
2. Как изолируются пользовательские данные?
3. Какие меры приняты против утечек?

**Качество:**
1. Как оценивается качество промптов?
2. Какие метрики используются?
3. Как обнаруживаются деградации?

**Галлюцинации:**
1. Как решается проблема галлюцинаций?
2. Какие техники валидации применяются?
3. Как обрабатываются неуверенные ответы?

**Производительность:**
1. Какая latency пайплайна?
2. Как оптимизирован расход токенов?
3. Как обеспечивается cost-efficiency?
