# User Prompt Template

````markdown
## Архитектура пайплайна
{{ pipeline_description }}

## Тестовый сценарий
**Входные данные:** {{ input_data }}
**Ожидаемое поведение:** {{ expected_behavior }}

## Лог выполнения версии A
{{ execution_log_a }}

**Финальный результат A:**
{{ result_a }}

## Лог выполнения версии B
{{ execution_log_b }}

**Финальный результат B:**
{{ result_b }}

## Критерии оценки пайплайна
1. **Route Correctness (0-10)** — правильно ли выбраны ветки условной логики
2. **Context Passing (0-10)** — корректно ли передаётся контекст между этапами
3. **Error Handling (0-10)** — обработка ошибок и fallback-сценарии
4. **Final Output Quality (0-10)** — качество итогового результата
5. **Efficiency (0-10)** — оптимальность (минимум лишних вызовов)

## Проверка условной логики
Для каждого этапа определи:
1. Был ли выбран правильный промпт для данного типа входа
2. Были ли переданы все необходимые переменные
3. Была ли корректно обработана ошибка (если возникла)

## Формат вывода
```json
{
  "pipeline_evaluation": {
    "A": {
      "route_correctness": <0-10>,
      "context_passing": <0-10>,
      "error_handling": <0-10>,
      "final_output_quality": <0-10>,
      "efficiency": <0-10>,
      "route_trace": [
        {"stage": 1, "expected": "...", "actual": "...", "correct": true/false},
        {"stage": 2, "expected": "...", "actual": "...", "correct": true/false}
      ],
      "total_score": <0-10>
    },
    "B": { ... аналогично ... }
  },
  "winner": "A | B | tie",
  "bottlenecks": {
    "A": ["узкие места пайплайна A"],
    "B": ["узкие места пайплайна B"]
  },
  "recommendation": "promote_B | keep_A | iterate_both"
}
```
````
