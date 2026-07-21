# LLM-сервисы и промпты

| Название | Аннотация | Связанные КИМ | Доступ | Лицензия / условия | Дата проверки |
|---|---|---|---|---|---|
| Базовый A/B-компаратор (универсальный) |Базовый A/B-компаратор (универсальный)| [КИМ 1.02 ](/M1-Prompt-Engineering/lesson_1.01/kim_02_mini-case.md),[КИМ  1.03](/M1-Prompt-Engineering/lesson_1.01/kim_03_mini-case.md) ,[КИМ  1.04](/M1-Prompt-Engineering/lesson_1.01/kim_04_mini-case.md), ,[КИМ  1.05](/M1-Prompt-Engineering/lesson_1.01/kim_05_mini-case.md),[КИМ  1.06](/M1-Prompt-Engineering/lesson_1.01/kim_06_mini-case.md),[КИМ  1.07](/M1-Prompt-Engineering/lesson_1.01/kim_07_mini-case.md)| [ссылка или путь](/resources/llm-prompts/ab_compare.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Оценка качества JSON-вывода |Оценка качества JSON-вывода| [КИМ 02](/M1-Prompt-Engineering/lesson_1.01/kim_02_mini-case.md),[КИМ 10](/M1-Prompt-Engineering/lesson_1.03/kim_10_iw.md), [КИМ 17](/M1-Prompt-Engineering/lesson_1.04/kim_17_iw.md) | [ссылка или путь](/resources/llm-prompts/json_check.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Оценка извлечения сущностей (NER) |Оценка извлечения сущностей (NER)| [ссылка](/M1-Prompt-Engineering/lesson_1.01/kim_02_mini-case.md),[КИМ  1.04](/M1-Prompt-Engineering/lesson_1.01/kim_04_mini-case.md) ,[КИМ  1.11](/M1-Prompt-Engineering/lesson_1.03/kim_11_iw.md), [КИМ  1.17](/M1-Prompt-Engineering/lesson_1.04/kim_17_iw.md) | [ссылка или путь](/resources/llm-prompts/ner.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Оценка мультимодальных промптов |Оценка мультимодальных промптов| [КИМ  1.10](/M1-Prompt-Engineering/lesson_1.03/kim_10_pt.md),[КИМ  1.13](/M1-Prompt-Engineering/lesson_1.03/kim_13_iw.md) ,[КИМ  1.15](/M1-Prompt-Engineering/lesson_1.03/kim_15_iw.md), [КИМ  1.19](/M1-Prompt-Engineering/lesson_1.04/kim_19_iw.md) | [ссылка или путь](/resources/llm-prompts/multimodal.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Оценка условных пайплайнов | Оценка условных пайплайнов | [КИМ  1.10](/M1-Prompt-Engineering/lesson_1.03/kim_10_pt.md),[КИМ  1.12](/M1-Prompt-Engineering/lesson_1.03/kim_12_iw.md) ,[КИМ 14](/M1-Prompt-Engineering/lesson_1.03/kim_14_iw.md), [КИМ  1.18](/M1-Prompt-Engineering/lesson_1.04/kim_18_iw.md) | [ссылка или путь](/resources/llm-prompts/pipeline_eval.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Оценка безопасности (защита от инъекций) | Оценка безопасности (защита от инъекций) | [КИМ  1.16](/M1-Prompt-Engineering/lesson_1.04/kim_16_code-review.md),[КИМ  1.21](/M1-Prompt-Engineering/lesson_1.04/kim_21_iw.md) | [ссылка или путь](/resources/llm-prompts/prompt_injection.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Оценка галлюцинаций | Оценка галлюцинаций | [КИМ  1.16](/M1-Prompt-Engineering/lesson_1.04/kim_16_code-review.md),[КИМ 19](/M1-Prompt-Engineering/lesson_1.04/kim_19_iw.md) | [ссылка или путь](/resources/llm-prompts/hallucination_eval.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |
| Комплексный судья для финальной защиты | Комплексный судья для финальной защиты | [КИМ 16](/M1-Prompt-Engineering/lesson_1.04/kim_16_code-review.md), [КИМ  1.21](/M1-Prompt-Engineering/lesson_1.04/kim_21_iw.md) | [ссылка или путь](/resources/llm-prompts/final_judge.md) | [ЗАПОЛНИТЬ] | [ГГГГ-ММ-ДД] |

Шаблоны предназначены для использования в качестве **LLM-as-a-judge** — автоматической оценки качества промптов при сравнении двух версий (A и B) в рамках A/B-тестирования.

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



