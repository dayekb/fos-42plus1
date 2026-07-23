# LLM-сервисы и промпты

Шаблоны предназначены для использования в качестве **LLM-as-a-judge** — автоматической оценки качества промптов при сравнении двух версий (A и B) в рамках A/B-тестирования.

| Название | Аннотация | Связанные КИМ | Доступ | Лицензия / условия | Дата проверки |
|---|---|---|---|---|---|
| Базовый A/B-компаратор (универсальный) | Универсальный шаблон для сравнения двух версий промпта по пяти критериям: точность, полнота, релевантность, структурированность и ясность. Возвращает JSON с оценками, победителем и рекомендацией. | [КИМ-1.02](/M1-Prompt-Engineering/lesson_1.01/kim_02_mini-case.md), [КИМ-1.03](/M1-Prompt-Engineering/lesson_1.01/kim_03_mini-case.md), [КИМ-1.04](/M1-Prompt-Engineering/lesson_1.01/kim_04_mini-case.md), [КИМ-1.05](/M1-Prompt-Engineering/lesson_1.01/kim_05_mini-case.md), [КИМ-1.06](/M1-Prompt-Engineering/lesson_1.01/kim_06_mini-case.md), [КИМ-1.07](/M1-Prompt-Engineering/lesson_1.01/kim_07_mini-case.md) | [/resources/llm-prompts/ab_compare.md](/resources/llm-prompts/ab_compare.md) |MIT License | 2026-07-22 |
| Оценка качества JSON-вывода | Специализированный шаблон для валидации структурированных данных: проверяет синтаксис JSON, соответствие схеме, заполненность полей, семантику и отсутствие галлюцинаций. | [КИМ-1.02](/M1-Prompt-Engineering/lesson_1.01/kim_02_mini-case.md), [КИМ-1.10](/M1-Prompt-Engineering/lesson_1.03/kim_10_pt.md), [КИМ-1.17](/M1-Prompt-Engineering/lesson_1.04/kim_17_iw.md) | [/resources/llm-prompts/json_check.md](/resources/llm-prompts/json_check.md) | MIT License | 2026-07-22 |
| Оценка извлечения сущностей (NER) | Оценивает точность извлечения именованных сущностей (ФИО, даты, диагнозы, препараты) с расчётом precision, recall и F1-меры для каждого типа сущностей. | [КИМ-1.02](/M1-Prompt-Engineering/lesson_1.01/kim_02_mini-case.md), [КИМ-1.04](/M1-Prompt-Engineering/lesson_1.01/kim_04_mini-case.md), [КИМ-1.11](/M1-Prompt-Engineering/lesson_1.03/kim_11_iw.md), [КИМ-1.17](/M1-Prompt-Engineering/lesson_1.04/kim_17_iw.md) | [/resources/llm-prompts/ner.md](/resources/llm-prompts/ner.md) | MIT License | 2026-07-22 |
| Оценка мультимодальных промптов | Шаблон для оценки работы с изображениями: учитывает точность OCR, понимание структуры документа, устойчивость к артефактам и калибровку уверенности. | [КИМ-1.10](/M1-Prompt-Engineering/lesson_1.03/kim_10_pt.md), [КИМ-1.13](/M1-Prompt-Engineering/lesson_1.03/kim_13_iw.md), [КИМ-1.15](/M1-Prompt-Engineering/lesson_1.03/kim_15_iw.md), [КИМ-1.19](/M1-Prompt-Engineering/lesson_1.04/kim_19_iw.md) | [/resources/llm-prompts/multimodal.md](/resources/llm-prompts/multimodal.md) | MIT License | 2026-07-22 |
| Оценка условных пайплайнов | Оценивает цепочки промптов с ветвлением логики: корректность выбора маршрута, передачу контекста, обработку ошибок и эффективность пайплайна. | [КИМ-1.10](/M1-Prompt-Engineering/lesson_1.03/kim_10_pt.md), [КИМ-1.12](/M1-Prompt-Engineering/lesson_1.03/kim_12_iw.md), [КИМ-1.14](/M1-Prompt-Engineering/lesson_1.03/kim_14_iw.md), [КИМ-1.18](/M1-Prompt-Engineering/lesson_1.04/kim_18_iw.md) | [/resources/llm-prompts/pipeline_eval.md](/resources/llm-prompts/pipeline_eval.md) | MIT License | 2026-07-22 |
| Оценка безопасности (защита от инъекций) | Тестирует устойчивость промпта к атакам: прямым и косвенным инъекциям, джейлбрейку, краже системного промпта и перехвату роли. Оценивает безопасность по пяти критериям. | [КИМ-1.16](/M1-Prompt-Engineering/lesson_1.04/kim_16_code-review.md), [КИМ-1.21](/M1-Prompt-Engineering/lesson_1.04/kim_21_iw.md) | [/resources/llm-prompts/prompt_injection.md](/resources/llm-prompts/prompt_injection.md) | MIT License | 2026-07-22 |
| Оценка галлюцинаций | Анализирует ответы на предмет выдуманных фактов, противоречий контексту и логических ошибок. Классифицирует галлюцинации по типам и рассчитывает их долю. | [КИМ-1.16](/M1-Prompt-Engineering/lesson_1.04/kim_16_code-review.md), [КИМ-1.19](/M1-Prompt-Engineering/lesson_1.04/kim_19_iw.md) | [/resources/llm-prompts/hallucination_eval.md](/resources/llm-prompts/hallucination_eval.md) | MIT License | 2026-07-22 |
| Комплексный судья для финальной защиты | Итоговый шаблон для оценки проекта по 100-балльной шкале: проверяет библиотеку промптов, условный пайплайн, качество кода, презентацию и ответы на вопросы. | [КИМ-1.16](/M1-Prompt-Engineering/lesson_1.04/kim_16_code-review.md), [КИМ-1.21](/M1-Prompt-Engineering/lesson_1.04/kim_21_iw.md) | [/resources/llm-prompts/final_judge.md](/resources/llm-prompts/final_judge.md) | MIT License | 2026-07-22 |

---

## 📋 Общая структура шаблонов

Каждый шаблон следует единой архитектуре:
```
┌─────────────────────────────────────────┐
│  System Prompt (роль судьи)             │
├─────────────────────────────────────────┤
│  Контекст (описание задачи)             │
├─────────────────────────────────────────┤
│  Вход A (ответ промпта версии A)        │
├─────────────────────────────────────────┤
│  Вход B (ответ промпта версии B)        │
├─────────────────────────────────────────┤
│  Ground Truth (эталон, если есть)       │
├─────────────────────────────────────────┤
│  Критерии оценки (rubric)               │
├─────────────────────────────────────────┤
│  Формат вывода (JSON)                   │
└─────────────────────────────────────────┘
```

### Рекомендуемые параметры API для judge-промптов

| Параметр | Значение | Обоснование |
| --- | --- | --- |
| `temperature` | 0.0–0.1 | Детерминированность критична |
| `top_p` | 0.8 | Баланс разнообразия и стабильности |
| `max_tokens` | 1000–2000 | Достаточно для полного разбора |
| `model` | gpt-4 / claude-3.5 | Судья должен быть сильнее оцениваемых |
