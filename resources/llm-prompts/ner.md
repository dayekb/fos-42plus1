# User Prompt Template

````makdowm
## Задача извлечения сущностей
Из текста документа необходимо извлечь следующие типы сущностей:
{{ entity_types }}

## Исходный текст
"""
{{ source_text }}
"""

## Эталонные сущности (ground truth)
{{ ground_truth_entities }}

## Извлечённые сущности (версия A)
{{ entities_a }}

## Извлечённые сущности (версия B)
{{ entities_b }}

## Метрики для расчёта
Для каждого типа сущности рассчитай:
- Precision = TP / (TP + FP) — доля корректно извлечённых
- Recall = TP / (TP + FN) — доля найденных от всех существующих
- F1-score = гармоническое среднее precision и recall

## Формат вывода
```json
{
  "metrics": {
    "A": {
      "per_entity_type": {
        "patient_name": {"precision": 0.0-1.0, "recall": 0.0-1.0, "f1": 0.0-1.0},
        "diagnosis": {"precision": 0.0-1.0, "recall": 0.0-1.0, "f1": 0.0-1.0},
        "medication": {"precision": 0.0-1.0, "recall": 0.0-1.0, "f1": 0.0-1.0}
      },
      "macro_f1": <среднее F1 по всем типам>,
      "false_positives": [{"type": "...", "value": "...", "reason": "..."}],
      "false_negatives": [{"type": "...", "expected": "..."}]
    },
    "B": { ... аналогично ... }
  },
  "winner": "A | B | tie",
  "statistical_significance": "да / нет (если разница > 5% F1)",
  "recommendation": "promote_B | keep_A | iterate_both"
}
```
````
