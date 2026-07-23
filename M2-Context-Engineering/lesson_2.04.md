# 🧪 Индивидуальный проект 2.4  
## Продвинутые техники и баланс качества: KAG, CAG, Multi‑Hop, оптимизация latency

по дисциплине **«Инженерия систем на базе больших языковых моделей»**

**Модуль 2. Context Engineering (Расширение контекста и RAG)**

---

## 📌 Оглавление

1. [Общие сведения](#-общие-сведения)
2. [Цели и задачи проекта](#-цели-и-задачи-проекта)
3. [Теоретическое введение (краткий обзор техник)](#-теоретическое-введение-краткий-обзор-техник)
4. [Общие требования к выполнению проекта](#-общие-требования-к-выполнению-проекта)
5. [Индивидуальные задания (20 вариантов)](#-индивидуальные-задания-20-вариантов)
6. [Методические рекомендации по выполнению](#-методические-рекомендации-по-выполнению)
7. [Требования к отчёту](#-требования-к-отчёту)
8. [Критерии оценки](#-критерии-оценки)
9. [Порядок сдачи](#-порядок-сдачи)
10. [Рекомендуемая литература](#-рекомендуемая-литература)
11. [Заключение](#-заключение)

---

# 📋 Общие сведения

| Параметр | Значение |
|----------|----------|
| **Номер работы** | 2.4 |
| **Название** | Продвинутые техники и баланс качества |
| **Трудоёмкость** | 2 академических часа (аудиторная работа) + самостоятельная доработка |
| **Форма проведения** | Индивидуальный проект (каждый студент получает уникальное задание) |
| **Компетенции** | LLM‑3 (3.5 — продвинутый уровень), LLM‑1 (1.2), PL‑1 (1.1) |
| **Уровень освоения** | Продвинутый (экспертный) |
| **Итоговый результат** | Модифицированный RAG-пайплайн с применением одной или нескольких продвинутых техник, сравнительный анализ качества и производительности, отчёт |

---

# 🎯 Цели и задачи проекта

## 2.1. Цели

- Освоить **передовые техники** контекстной инженерии, выходящие за рамки классического RAG:

  - **KAG (Knowledge‑Augmented Generation)** — использование графовых структур для семантического обогащения контекста.
  - **CAG (Cache‑Augmented Generation)** — интеллектуальное кэширование для снижения latency и затрат.
  - **Multi‑Hop RAG** — многошаговые рассуждения для сложных вопросов, требующих синтеза информации из нескольких источников.
  - **Оптимизация latency** — комплекс методов, направленных на сокращение времени ответа (кэширование, batch‑обработка, лёгкие модели, эвристики).

- Научиться **количественно оценивать** влияние каждой техники на качество (Recall, MRR, faithfulness) и производительность (latency, token usage).

- Сформировать **инженерный подход** к выбору компромиссов: *качество vs скорость vs стоимость*.

## 2.2. Задачи

1. Изучить теоретические основы выбранной техники (KAG/CAG/Multi‑Hop/Latency).
2. Реализовать модификацию существующего RAG-пайплайна (из лабораторных 2.2 и 2.3) с интеграцией этой техники.
3. Провести **экспериментальное сравнение** с эталонным пайплайном (baseline) на фиксированном тестовом наборе.
4. Измерить ключевые метрики: **Recall@k, MRR@k, средняя latency, количество потреблённых токенов**.
5. Оформить отчёт с выводами о достигнутых улучшениях и компромиссах.

---

# 📖 Теоретическое введение (краткий обзор техник)

## 3.1. KAG (Knowledge‑Augmented Generation)

**Идея:** Вместо поиска по фрагментам текста используется **граф знаний** (сущности и связи между ними). Это позволяет строить цепочки рассуждений и улучшать полноту ответа на сложные вопросы.

**Реализация (упрощённая):**
- Из документов извлекаются сущности (NER) и связи (relation extraction).
- Строится граф в памяти или в Neo4j.
- По запросу выполняется поиск по графу (SPARQL или обход графа) для получения релевантных подграфов.
- Подграфы преобразуются в текстовый контекст и подаются в LLM.

**Когда применять:** Задачи, требующие связывания нескольких фактов (например, *«В каких городах есть офисы компании X, и какие проекты там ведутся?»*).

---

## 3.2. CAG (Cache‑Augmented Generation)

**Идея:** Многие запросы повторяются (или очень похожи). Кэширование контекста, эмбеддингов или даже сгенерированных ответов позволяет **радикально снизить latency и затраты** для повторных запросов.

**Варианты кэширования:**
- **Кэш эмбеддингов** — сохраняем вектор запроса и результаты поиска для одинаковых запросов.
- **Кэш контекста** — для частых запросов храним готовый сформированный контекст (промпт).
- **Кэш ответа** — полный ответ LLM для идентичных вопросов (с контролем времени жизни).
- **Семантический кэш** — группировка похожих запросов по векторной близости.

**Когда применять:** Продуктовые системы с высокой долей повторяющихся пользовательских вопросов (FAQ, техподдержка).

---

## 3.3. Multi‑Hop RAG

**Идея:** Один запрос может требовать последовательного обращения к разным частям базы знаний. Многошаговый RAG разбивает задачу на подзапросы, где результат первого шага уточняет второй и т.д.

**Архитектура:**
1. Анализ запроса → генерация первого подзапроса.
2. Поиск по первому подзапросу → извлечение фактов.
3. На основе фактов генерируется следующий подзапрос (уточнение).
4. Повтор до достижения уверенности или заданного числа шагов.

**Когда применять:** Вопросы, требующие синтеза информации из нескольких независимых документов (например, сравнение характеристик двух продуктов).

---

## 3.4. Оптимизация latency — комплексный подход

**Основные источники задержки:**
- Query rewriting (LLM-вызов).
- Поиск в векторной БД (особенно при большом количестве документов).
- Реранкинг (cross-encoder).
- Генерация ответа (основной вклад).

**Методы снижения:**
- **Model racing** — запуск нескольких моделей параллельно, выбор быстрейшей.
- **Уменьшение k** — для ретривала и реранкинга.
- **Кэширование** (в том числе эмбеддингов и результатов поиска).
- **Использование более лёгких моделей** для вспомогательных задач (rewrite, rerank).
- **Batch‑обработка** запросов, если система работает в пакетном режиме.
- **Предварительное агрегирование** контекста для частых тем.

---

# ⚙️ Общие требования к выполнению проекта

1. **Исходная база:** каждый студент должен иметь работающий пайплайн из лабораторной 2.3 (гибридный поиск + реранкинг + query rewriting). Он будет служить **baseline**.
2. **Датасет:** студентам предоставляется единый тестовый набор из 100 вопросов с размеченными релевантными документами (для автоматической оценки). Датасет должен быть достаточно разнообразным, чтобы отражать разные типы вопросов.
3. **Метрики:** обязательные — **Recall@5, MRR@5, средняя latency (ms), количество токенов в контексте**. Дополнительно — **Faithfulness** (оценка достоверности ответа с помощью LLM-as-Judge).
4. **Эксперимент:** необходимо провести минимум 3 прогона для каждой конфигурации, чтобы усреднить результаты.
5. **Код:** все изменения должны быть закоммичены в личный репозиторий с тегами (`baseline`, `optimized`, `final`).

---

# 📋 Индивидуальные задания (20 вариантов)

Каждое задание представляет собой **комбинацию одной или нескольких продвинутых техник** с акцентом на баланс качества и производительности. Задания распределяются преподавателем или выбираются студентом случайно.

| № | Название задания | Описание задачи | Ожидаемый результат |
|---|------------------|-----------------|----------------------|
| 1 | **CAG — кэширование эмбеддингов** | Реализовать in‑memory кэш для векторов запросов. При повторном запросе возвращать сохранённые результаты поиска. Измерить снижение latency и влияние на качество. | Отчёт с графиками latency, сравнение recall с baseline. |
| 2 | **CAG — семантический кэш ответов** | Группировать похожие запросы по косинусной близости (порог 0.95). Для группы хранить один ответ, возвращать его для всех запросов группы. | Ускорение до 80% для повторяющихся тем, оценка потери качества. |
| 3 | **CAG — кэширование контекста** | Кэшировать сформированный промпт (контекст + инструкция) для запросов, имеющих одинаковые топ-5 релевантных чанков. При совпадении пропускать ретривал и сразу генерировать ответ. | Сравнение latency, экономия токенов (входных и выходных). |
| 4 | **CAG + TTL** | Внедрить кэширование контекста с временем жизни (TTL) для актуальных данных. Экспериментировать с разными TTL (1 час, 24 часа, 7 дней) и анализировать устаревание контекста. | Рекомендации по оптимальному TTL для заданного домена. |
| 5 | **KAG — построение простого графа из документов** | Извлечь сущности (люди, организации, продукты) и связи из корпуса. Построить граф в networkx. При запросе искать связанные сущности и добавлять их в контекст. | Улучшение Recall@5 для вопросов с упоминанием нескольких сущностей. |
| 6 | **KAG + Neo4j (внешняя БД)** | Развернуть Neo4j в Docker, загрузить граф знаний. Реализовать Cypher‑запросы для обогащения контекста. Сравнить с текстовым RAG. | Отчёт о приросте точности на multi‑hop вопросах. |
| 7 | **KAG — гибридный ретривал (текст + граф)** | Комбинировать результаты векторного поиска и графового обхода. Использовать RRF для слияния. Оценить вклад графовой части. | Ablation study: граф vs текст vs гибрид. |
| 8 | **Multi‑Hop — двухшаговый RAG** | Разбить запрос на два подзапроса: первый ищет общую информацию, второй — детали. Реализовать цепочку с использованием LLM для генерации второго запроса. | Улучшение MRR на сложных вопросах. |
| 9 | **Multi‑Hop — итеративный с остановкой по уверенности** | Добавить механизм оценки уверенности ответа на каждом шаге. Если уверенность низкая — делать следующий шаг. Иначе — остановиться. | Сравнение числа шагов vs качество. |
| 10 | **Multi‑Hop — параллельный поиск** | Генерировать несколько подзапросов параллельно (3–5), выполнять поиск одновременно, объединять результаты. | Снижение общего времени по сравнению с последовательным multi‑hop. |
| 11 | **Оптимизация latency — Model Racing** | Для вспомогательных задач (query rewriting, reranking) использовать две модели: лёгкую (быструю) и тяжёлую (точную). Запускать параллельно, брать результат от первой завершённой. | Снижение средней latency на 30% при незначительной потере качества. |
| 12 | **Оптимизация latency — уменьшение k** | Экспериментировать с k для ретривала (5, 10, 20, 50) и реранкинга. Найти оптимальное k, балансирующее recall и время. | График зависимости recall/latency от k. |
| 13 | **Оптимизация latency — замена cross‑encoder на лёгкий** | Заменить `ms-marco-MiniLM-L-12-v2` на `L-6-v2` и даже на `L-2-v2`. Оценить потерю качества vs прирост скорости. | Таблица сравнения моделей. |
| 14 | **Оптимизация latency — batch‑обработка** | Реализовать пакетную обработку запросов (batch size = 8, 16, 32) для эмбеддингов и реранкинга. Измерить ускорение и потерю качества (если есть). | Рекомендации по оптимальному batch size. |
| 15 | **Комбинированная: CAG + Multi‑Hop** | Применить кэширование для промежуточных результатов multi‑hop. Хранить в кэше результаты первого шага, чтобы использовать их для похожих запросов. | Экономия времени для multi‑hop на 50%+. |
| 16 | **Комбинированная: KAG + CAG** | Кэшировать результаты графовых запросов для часто используемых сущностей. | Ускорение графовой части, оценка качества. |
| 17 | **Комбинированная: Multi‑Hop + KAG** | Использовать граф знаний в качестве источника фактов для multi‑hop. На каждом шаге обогащать графовыми связями. | Сравнение с текстовым multi‑hop. |
| 18 | **Комбинированная: все техники** | Интегрировать KAG, CAG, Multi‑Hop и оптимизацию latency в один пайплайн. Провести полное исследование всех комбинаций (Ablation). | Итоговый оптимальный пайплайн с обоснованием. |
| 19 | **Анализ компромиссов — скорость vs качество** | Выбрать три конфигурации: (1) максимальное качество, (2) максимальная скорость, (3) баланс. Оценить метрики и затраты токенов. Построить Pareto‑фронт. | Рекомендации для разных сценариев использования. |
| 20 | **Наблюдаемость (Observability) + баланс** | Интегрировать логирование каждого шага (время, токены, scores). Визуализировать дашборд (Grafana/LangSmith). На основе логов предложить автоматическую оптимизацию параметров в рантайме. | Демонстрация дашборда, отчёт о влиянии на принятие решений. |

---

# 🛠️ Методические рекомендации по выполнению

## 6.1. Структура выполнения (для любого варианта)

1. **Изучение теории** — прочитать основную литературу по выбранной технике.
2. **Проектирование** — нарисовать схему модифицированного пайплайна с указанием добавляемых компонентов.
3. **Реализация** — написать код, используя существующие модули из лабораторных 2.2–2.3.
4. **Тестирование** — прогнать на небольшом наборе (10 запросов) для отладки.
5. **Эксперимент** — запуск на полном тестовом наборе (100 запросов), сбор метрик.
6. **Анализ** — сравнение с baseline, оценка компромиссов.
7. **Отчёт** — оформление результатов.

## 6.2. Инструменты и библиотеки

- Для **графов**: `networkx`, `rdflib`, `neo4j` (опционально).
- Для **кэширования**: `functools.lru_cache`, `redis` или просто `dict`.
- Для **измерения latency**: модуль `time` или `timeit`.
- Для **логирования**: `logging` + возможность интеграции с LangSmith.

## 6.3. Общие советы

- **Сначала отладьте на малом датасете** — чтобы убедиться в корректности.
- **Замеряйте не только среднюю latency, но и процентили (P95, P99)** — это критично для production.
- **Фиксируйте использованные токены** — модель OpenAI возвращает usage в ответе.
- **При использовании графов** — помните, что извлечение сущностей может быть неточным; ошибки редко можно игнорировать.
- **Для multi‑hop** — важно определить условие остановки (число шагов или уверенность).
- **При комбинировании техник** — документируйте порядок применения и взаимовлияние.

---

# 📝 Требования к отчёту

Отчёт должен содержать следующие разделы:

1. **Титульный лист** (название работы, ФИО, группа, вариант задания).
2. **Введение** — краткое описание выбранной техники и её актуальности.
3. **Архитектура** — схема модифицированного пайплайна с пояснениями.
4. **Реализация** — листинг ключевых классов/функций (не более 2 страниц кода).
5. **Экспериментальная часть**:
   - Описание тестового датасета.
   - Результаты для baseline и модифицированного пайплайна в таблице.
   - Графики (latency, recall, токены).
   - Анализ статистической значимости (если применимо).
6. **Обсуждение** — интерпретация результатов, какие компромиссы были выявлены, рекомендации.
7. **Выводы** — достигнуты ли цели, что удалось, что не удалось, дальнейшие направления.
8. **Список литературы** (минимум 5 источников).
9. **Дополнительные материалы:** ссылка на репозиторий с кодом (GitHub).

---

# 📊 Критерии оценки

| Критерий | Вес | Описание |
|----------|-----|----------|
| **Корректность реализации** | 25% | Код работает без ошибок, пайплайн выполняет задуманную функцию. |
| **Качество эксперимента** | 20% | Проведены замеры, данные воспроизводимы, использованы адекватные метрики. |
| **Анализ и интерпретация** | 20% | Глубокий анализ полученных результатов, обоснование компромиссов. |
| **Инженерное мышление** | 15% | Выбор эффективных инструментов, учёт реальных ограничений (cost, latency). |
| **Оформление отчёта** | 10% | Чёткость, структурированность, визуализация данных. |
| **Исходный код** | 10% | Чистота кода, комментарии, наличие README. |

> **Дополнительный бонус (+10%)** — если студент предложил и реализовал свою оригинальную технику, не описанную в задании, или провёл сравнение с альтернативным подходом.

---

# 📤 Порядок сдачи

1. Загрузить код в репозиторий (GitHub/GitLab) и указать теги версий.
2. Предоставить отчёт в формате PDF (не более 15 страниц).
3. Продемонстрировать работу пайплайна преподавателю на 3–5 произвольных запросах (живая демонстрация).
4. Ответить на вопросы по реализации и результатам.

---

# 📚 Рекомендуемая литература

Фундаментальные работы по RAG и генерации

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.-t., Rocktäschel, T., Riedel, S., Kiela, D. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks // Advances in Neural Information Processing Systems (NeurIPS), 2020. — Vol. 33. — P. 9459–9474. — https://arxiv.org/abs/2005.11401
2. Guu, K., Lee, K., Tung, Z., Pasupat, P., Chang, M.W. REALM: Retrieval-Augmented Language Model Pre-Training // Proceedings of the 37th International Conference on Machine Learning (ICML), 2020. — P. 3929–3938. — https://arxiv.org/abs/2002.08909
3. Izacard, G., Lewis, P., Lomeli, M., Hosseini, L., Petroni, F., Schick, T., Dwivedi-Yu, J., Joulin, A., Riedel, S., Grave, E. Atlas: Few-shot Learning with Retrieval Augmented Language Models // Journal of Machine Learning Research (JMLR), 2023. — Vol. 24. — P. 1–43. — https://arxiv.org/abs/2208.03299
4. Asai, A., Wu, Z., Wang, Y., Sil, A., Hajishirzi, H. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection // Proceedings of the International Conference on Learning Representations (ICLR), 2024. — https://arxiv.org/abs/2310.11511
5. Jiang, Z., Xu, F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y., Callan, J., Neubig, G. Active Retrieval Augmented Generation // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 7969–7992. — https://arxiv.org/abs/2305.06983
6. Sarthi, P., Abdullah, S., Tuli, A., Khanna, S., Goldie, A., Manning, C.D. RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval // Proceedings of the International Conference on Learning Representations (ICLR), 2024. — https://arxiv.org/abs/2401.18059

KAG — Knowledge-Augmented Generation (графы знаний)

7. Guan, X., Liu, Y., Lin, H., Lu, Y., He, B., Han, X., Sun, L. Mitigating Large Language Model Hallucinations via Autonomous Knowledge Graph-based Retrofitting // Proceedings of the AAAI Conference on Artificial Intelligence (AAAI), 2024. — P. 18126–18134. — https://ojs.aaai.org/index.php/AAAI/article/view/29879
8. Hu, Z., Xu, Y., Yu, W., Wang, S., Yang, Z., Zhu, C., Chang, K.-W., Sun, Y. Empowering Language Models with Knowledge Graph Reasoning for Question Answering // Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2022. — P. 9562–9581.
9. Hu, Y., Lei, Z., Zhang, Z., Pan, B., Ling, C., Zhao, L. GRAG: Graph Retrieval-Augmented Generation // arXiv preprint arXiv:2405.16506, 2024. — https://arxiv.org/abs/2405.16506
10. Ji, Y., Wu, K., Li, J., Chen, W., Zhong, M., Jia, X., Zhang, M. Retrieval and Reasoning on KGs: Integrate Knowledge Graphs into Large Language Models for Complex Question Answering // Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2024. — P. 7598–7610.
11. Huang, P., Liu, Z., Yan, Y., Yi, X., Chen, H., Liu, Z., Sun, M., Xiao, T., Yu, G., Xiong, C. PIP-KAG: Mitigating Knowledge Conflicts in Knowledge-Augmented Generation via Parametric Pruning // arXiv preprint arXiv:2502.15543, 2025. — https://arxiv.org/abs/2502.15543
12. Gao, Y., et al. Large Language Models Meet Knowledge Graphs for Question Answering: Synthesis and Opportunities // arXiv preprint arXiv:2505.20099, 2025. — https://arxiv.org/abs/2505.20099

Multi-Hop RAG и многошаговые рассуждения

13. Trivedi, H., Balasubramanian, N., Khot, T., Sabharwal, A. Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions // Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL), 2023. — P. 10014–10037. — https://arxiv.org/abs/2212.10509
14. Trivedi, H., Balasubramanian, N., Khot, T., Sabharwal, A. MuSiQue: Multihop Questions via Single-hop Question Composition // Transactions of the Association for Computational Linguistics (TACL), 2022. — Vol. 10. — P. 539–554.
15. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., Cao, Y. ReAct: Synergizing Reasoning and Acting in Language Models // Proceedings of the International Conference on Learning Representations (ICLR), 2023. — https://arxiv.org/abs/2210.03629
16. Lee, J., Kwon, D., Jin, K. GRADE: Generating multi-hop QA and fine-gRAined Difficulty matrix for RAG Evaluation // Findings of the Association for Computational Linguistics: EMNLP 2025, 2025. — P. 4405–4424. — https://aclanthology.org/2025.findings-emnlp.236/
17. Xiong, W., Li, X., Iyer, S., Du, J., Lewis, P., Wang, W.Y., Mehdad, Y., Yih, S., Riedel, S., Kiela, D., Oguz, B. Answering Complex Open-Domain Questions with Multi-hop Dense Retrieval // Proceedings of the International Conference on Learning Representations (ICLR), 2021.
    
Кэширование и оптимизация latency

18. Gim, J., Park, J., Jeong, S., Kim, S. Prompt Cache: Modular Attention Reuse for Low-Latency Inference // Proceedings of the 2024 Annual Meeting of the Association for Computational Linguistics (ACL), 2024.
19. Liu, Z., Desai, A., Liao, F., Sivashunmugam, V., Lu, B., Khandelwal, D., Chellappa, R., Krishnamurthy, A. RAGCache: Efficient Knowledge Caching for Retrieval-Augmented Generation // arXiv preprint arXiv:2404.12457, 2024. — https://arxiv.org/abs/2404.12457
20. Liu, Y., et al. CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion // Proceedings of the 18th European Conference on Computer Systems (EuroSys), 2024.
21. Zheng, L., Li, Z., Zhang, H., Zhuang, Y., Chen, Z., Huang, Y., Huang, Y., Wang, Y., Xu, Y., Zhuo, D., Gonzalez, J.E., Stoica, I. Efficiently Scaling Transformer Inference // Proceedings of Machine Learning and Systems (MLSys), 2023. — https://arxiv.org/abs/2211.05102
22. Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, C.H., Gonzalez, J.E., Zhang, H., Stoica, I. Efficient Memory Management for Large Language Model Serving with PagedAttention // Proceedings of the ACM SIGOPS 29th Symposium on Operating Systems Principles (SOSP), 2023. — https://arxiv.org/abs/2309.06180

Гибридный поиск, реранкинг и query rewriting

23. Robertson, S., Zaragoza, H. The Probabilistic Relevance Framework: BM25 and Beyond // Foundations and Trends in Information Retrieval, 2009. — Vol. 3, No. 4. — P. 333–389. — https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf
24. Cormack, G.V., Clarke, C.L.A., Buettcher, S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods // Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR), 2009. — P. 758–759. — https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/
25. Nogueira, R., Cho, K. Passage Re-ranking with BERT // arXiv preprint arXiv:1901.04085, 2019. — https://arxiv.org/abs/1901.04085
26. Khattab, O., Zaharia, M. ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT // Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR), 2020. — https://arxiv.org/abs/2004.12832
27. Ma, X., Gong, Y., He, P., Zhao, H., Duan, N. Query Rewriting for Retrieval-Augmented Large Language Models // arXiv preprint arXiv:2305.14283, 2023. — https://arxiv.org/abs/2305.14283
28. Gao, L., Ma, X., Lin, J., Callan, J. Precise Zero-Shot Dense Retrieval without Relevance Labels // Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL), 2023. — (HyDE — Hypothetical Document Embeddings) — https://arxiv.org/abs/2212.10496

Оценка качества и метрики

29. Liu, N.F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., Liang, P. Lost in the Middle: How Language Models Use Long Contexts // Transactions of the Association for Computational Linguistics (TACL), 2024. — Vol. 12. — P. 157–173. — https://arxiv.org/abs/2307.03172
30. Saad-Falcon, J., Khattab, O., Potts, C., Zaharia, M. ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems // Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL), 2024. — P. 338–354.
31. Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., Zhu, C. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 2511–2522. — https://arxiv.org/abs/2303.16634
32. Chen, J., Lin, H., Han, X., Sun, L. Benchmarking Large Language Models in Retrieval-Augmented Generation // Proceedings of the AAAI Conference on Artificial Intelligence (AAAI), 2024. — Vol. 38. — P. 17754–17762.

---

# 🏁 Заключение

Индивидуальный проект 2.4 является **завершающим этапом** модуля «Context Engineering». Он позволяет студентам выйти за рамки стандартного RAG и освоить передовые методы, которые активно внедряются в промышленных системах. Главная цель — не просто реализовать технику, а **научиться оценивать её практическую ценность** в контексте реальных ограничений (скорость, стоимость, качество). Успешное выполнение проекта демонстрирует готовность выпускника к роли **ML Engineer** или **AI Architect**, способного принимать обоснованные инженерные решения.

---
