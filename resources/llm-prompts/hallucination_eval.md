## Исходные данные (контекст)
"""
{{ source_context }}
"""

## Запрос к модели
{{ user_query }}

## Ответ версии A
"""
{{ response_a }}
"""

## Ответ версии B
"""
{{ response_b }}
"""

## Задача
Проанализируй каждый ответ и выяви галлюцинации — утверждения, которые:
1. Отсутствуют в исходном контексте
2. Противоречат исходному контексту
3. Являются выдуманными фактами, цифрами, именами
4. Логически не следуют из контекста

## Типы галлюцинаций
- **Intrinsic** — противоречит собственному ответу
- **Extrinsic** — противоречит исходному контексту
- **Logical** — логическая ошибка в рассуждениях
- **Factual** — выдуманные факты

## Формат вывода
```json
{
  "hallucination_analysis": {
    "A": {
      "claims": [
        {
          "claim": "утверждение из ответа",
          "supported_by_context": true/false,
          "evidence": "цитата из контекста или 'отсутствует'",
          "hallucination_type": "none | intrinsic | extrinsic | logical | factual"
        }
      ],
      "total_claims": <число>,
      "supported_claims": <число>,
      "hallucination_rate": <0.0-1.0>,
      "severity": "none | low | medium | high | critical"
    },
    "B": { ... аналогично ... }
  },
  "winner": "A | B | tie",
  "recommendation": "promote_B | keep_A | iterate_both"
}
```
