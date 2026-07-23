# 📘 Лекционное занятие 2.1. Основы RAG, KAG, CAG и векторный поиск. Архитектуры ретривера и считывателя

**Продолжительность:** 2 академических часа  
**Форма проведения:** лекция с элементами интерактива (опросы, разбор кейсов)

---

## 📌 Оглавление

1. [Цели занятия](#-цели-занятия)
2. [Содержание лекции](#-содержание-лекции)
   - [2.1. Введение: проблема контекста в LLM](#21-введение-проблема-контекста-в-llm)
   - [2.2. RAG: базовый архитектурный паттерн](#22-rag-базовый-архитектурный-паттерн)
   - [2.3. Эволюция RAG (2020–2025)](#23-эволюция-rag-20202025)
   - [2.4. Альтернативные подходы: KAG и CAG](#24-альтернативные-подходы-kag-и-cag)
   - [2.5. Эмбеддинги и векторные представления](#25-эмбеддинги-и-векторные-представления)
   - [2.6. Векторные базы данных](#26-векторные-базы-данных)
   - [2.7. Чанкинг (разбиение документов)](#27-чанкинг-разбиение-документов)
   - [2.8. Гибридный поиск (Hybrid Search)](#28-гибридный-поиск-hybrid-search)
   - [2.9. Query Rewriting (переформулировка запроса)](#29-query-rewriting-переформулировка-запроса)
   - [2.10. Реранкинг (Reranking) с cross-encoder](#210-реранкинг-reranking-с-cross-encoder)
3. [Планируемые результаты (индикаторы компетенций)](#-планируемые-результаты-индикаторы-компетенций)
4. [Связь с практическими занятиями модуля](#-связь-с-практическими-занятиями-модуля)
5. [Структура занятия (90 минут)](#-структура-занятия-90-минут)
6. [Рекомендуемая литература](#-рекомендуемая-литература)

---

## 🎯 Цели занятия

- Сформировать понимание **архитектурных принципов RAG** и его роли в преодолении ограничений БЯМ.
- Познакомить с **эволюцией подходов** к расширению контекста: от Naive RAG до модульных архитектур, включая KAG и CAG.
- Объяснить принципы работы **векторных представлений** (эмбеддингов) и **векторных баз данных** (FAISS, Qdrant).
- Дать представление о **стратегиях чанкинга** и их влиянии на качество ретривала и генерации.
- Сформулировать критерии выбора архитектуры ретривера и модели эмбеддингов под конкретную задачу.
- Познакомить с **продвинутыми техниками** оптимизации RAG: гибридный поиск, query rewriting, reranking.

---

## 📖 Содержание лекции

### 2.1. Введение: проблема контекста в LLM

**Ключевые вопросы:**

- **Ограничения БЯМ:** языковые модели имеют «точку отсечения» знаний (knowledge cutoff) и не имеют доступа к актуальным или корпоративным данным.
- **Галлюцинации** — следствие отсутствия релевантной информации в параметрической памяти модели.
- **Дилемма:** дообучение каждой модели под каждую предметную область — дорого и медленно; нужен механизм **непараметрического** доступа к знаниям.
- **Решение RAG:** извлечение релевантного контекста из внешней базы знаний, дополнение им промпта и генерация ответа, «заземлённого» на извлечённых фактах.

> 💡 **Ключевая идея:** RAG позволяет «подключать» к LLM внешние знания без переобучения, обеспечивая актуальность и достоверность ответов.

---

### 2.2. RAG: базовый архитектурный паттерн

**Архитектура «retriever → reader»:**  
RAG — это конвейерная архитектура, где сначала выполняется поиск релевантных документов, а затем на их основе генерируется ответ.

**Две фазы работы RAG-системы:**

| Фаза | Этап | Описание |
|------|------|----------|
| **Offline (индексация)** | Chunking | Разбиение документов на фрагменты (chunks) |
| | Embedding | Преобразование чанков в векторные представления |
| | Хранение | Сохранение векторов в векторной БД с метаданными |
| **Online (запрос)** | Query Embedding | Преобразование пользовательского запроса в вектор |
| | Similarity Search | Поиск top‑k наиболее похожих векторов в БД |
| | Prompt Construction | Формирование промпта: инструкция + контекст + вопрос |
| | Generation | Генерация ответа LLM на основе обогащённого промпта |

---

### 2.3. Эволюция RAG (2020–2025)

**Четыре поколения RAG-архитектур:**

| Поколение | Период | Характеристика |
|-----------|--------|----------------|
| **Naive RAG** | 2020–2021 | Простой поиск + генерация. Минимальная точность. |
| **Advanced RAG** | 2022–2023 | Добавлены реранкинг, гибридный поиск, пред- и пост-обработка. |
| **Modular RAG** | 2024 | Многостадийные пайплайны с взаимозаменяемыми модулями. |
| **Agentic RAG** | 2025 | Самоулучшающиеся, адаптивные системы с агентным управлением поиском. |

**Тренды последних лет:**

- Гибридный поиск (векторный + ключевой) стал стандартом.
- Реранкинг обязателен для production-качества.
- Graph RAG даёт до 35% прироста точности на сложных рассуждениях.
- Внедряются реальная наблюдаемость (observability) и автоматическая оценка качества.

---

### 2.4. Альтернативные подходы: KAG и CAG

- **KAG (Knowledge‑Augmented Generation)** — использование графов знаний для структурированного извлечения информации. В отличие от RAG, где поиск идёт по векторной близости, KAG оперирует семантическими связями между сущностями, что даёт преимущество в задачах, требующих многошаговых рассуждений (multi‑hop reasoning).

- **CAG (Cache‑Augmented Generation)** — кэширование контекста для многократно повторяющихся запросов. Стратегия: при первом обращении к документу весь его контекст (или его ключевая часть) сохраняется в кэше; при повторных запросах контекст подаётся в LLM без повторного поиска, что радикально снижает latency и затраты на токены.

---

### 2.5. Эмбеддинги и векторные представления

**Что такое эмбеддинг?**  
Векторное представление смысла текста в многомерном пространстве. Чем ближе векторы по косинусному расстоянию, тем семантически ближе тексты.

**Модель BGE‑M3** — одна из лучших открытых мультиязычных моделей эмбеддингов:

- Размерность: **1024 измерения**.
- Контекстное окно: **8K токенов**.
- Три функции одновременно: плотный ретривал, мультивекторный ретривал и разреженный ретривал.
- Превосходная производительность на бенчмарках MIRACL, MTEB, SEB.

**Сравнение подходов:**

| Подход | Сильные стороны | Слабые стороны |
|--------|----------------|----------------|
| **Dense (плотные) векторы** | Семантический поиск, устойчивость к синонимам и переформулировкам | «Слеп» к точным терминам, кодам, редким словам |
| **Sparse (разреженные) векторы (BM25/TF‑IDF)** | Точное совпадение терминов, работа с кодами и идентификаторами | Не понимает смысла, зависит от точного вхождения слов |

---

### 2.6. Векторные базы данных

**Назначение:** хранение и эффективный поиск многомерных векторов с поддержкой ANN (приближённый поиск ближайших соседей).

**FAISS (Facebook AI Similarity Search):**

- **Лучшее для:** локальных setup‑ов, прототипирования, высокопроизводительного поиска.
- **Плюсы:** экстремально быстрый поиск, поддержка GPU, множество типов индексов.
- **Минусы:** нет встроенной персистентности, нет масштабирования, слабая фильтрация по метаданным.

**Qdrant:**

- **Лучшее для:** production‑систем с сильной фильтрацией по метаданным.
- **Плюсы:** быстрый ANN‑поиск, мощная фильтрация, поддержка гибридного поиска (dense + sparse), open‑source с облачной версией.
- **Минусы:** сложнее в настройке, чем FAISS.

**Правило выбора:**

| Сценарий | Рекомендуемая БД |
|----------|------------------|
| Прототипирование | FAISS / Chroma |
| Production и масштаб | Pinecone / Milvus |
| Сложная бизнес‑логика + фильтрация | Weaviate / Qdrant |

---

### 2.7. Чанкинг (разбиение документов)

**Почему чанкинг критичен?**  
Способ разбиения документов влияет на качество ретривала больше, чем почти любой другой параметр RAG‑пайплайна.

**«Проблема Златовласки»:**

- **Слишком маленькие чанки** — вектор представляет лишь фрагмент мысли; ответ «размазан» по множеству чанков.
- **Слишком большие чанки** — вектор усредняет множество тем; релевантность «размывается», в контекст попадает нерелевантный материал.

**Основные стратегии чанкинга:**

| Стратегия | Размер | Перекрытие | Лучшее для |
|-----------|--------|------------|------------|
| **Fixed‑size** | 512 токенов | 10–20% | Общие цели, быстрая индексация |
| **Sliding Window** | Переменный | 10–20% | Контекстно‑критичные запросы, юридические/медицинские тексты |
| **Sentence‑based** | Переменный (1–2 предложения) | 1–2 предложения | Семантическая связность, FAQ |
| **Recursive** | Иерархический | Контекстно‑зависимый | Сложные, структурированные документы |

> 📌 **Sliding Window** — специальная техника, при которой окно фиксированного размера движется по документу с перекрытием (обычно 10–20%). Перекрытие гарантирует, что ключевое предложение не будет «разорвано» на границе двух чанков.

---

### 2.8. Гибридный поиск (Hybrid Search)

**Определение:** класс методов информационного поиска, объединяющих лексические (sparse) и семантические (dense) сигналы для повышения полноты и точности выдачи.

**Мотивация:**

- Преодоление «терминологического разрыва» (синонимы, переформулировки).
- Устойчивость к опечаткам и морфологическим вариациям.
- Точное извлечение кодов, идентификаторов (где BM25 силён).
- Семантическое обобщение при переносе на новые домены (где dense‑модели сильны).

**Архитектура:**

1. **Лексический канал:** BM25/TF‑IDF — точное совпадение терминов по инвертированному индексу.
2. **Семантический канал:** dense‑поиск по векторной близости.
3. **Слияние ранжировок:** **Reciprocal Rank Fusion (RRF)** — устойчивый к разномасштабным скорингам метод объединения результатов.

---

### 2.9. Query Rewriting (переформулировка запроса)

**Зачем?** Пользовательский запрос часто неоптимален для векторного поиска: содержит местоимения, аббревиатуры, двусмысленности или слишком разговорную формулировку.

**Техники:**

- Сохранение естественного языка и поисково‑дружественных формулировок для sparse‑ретривала.
- Максимизация семантической фокусировки и плотности ключевых слов для dense‑ретривала.
- Завершение неполных высказываний (Incomplete Utterance Rewriting) в диалоговых сценариях.
- Генерация семантически разнообразных подзапросов для повышения полноты поиска.

> ⚠️ **Компромисс:** query rewriting улучшает качество поиска, но добавляет latency (особенно при использовании LLM для переформулировки).

---

### 2.10. Реранкинг (Reranking) с cross‑encoder

**Проблема:** bi‑encoder (используемый для первичного поиска) кодирует запрос и документ независимо — быстро, но не идеально точно.

**Решение: двухстадийный пайплайн:**

| Стадия | Метод | Задача | Скорость | Точность |
|--------|-------|--------|----------|----------|
| **1‑я (retrieval)** | Bi‑encoder (dense/sparse) | Быстрый поиск top‑N кандидатов | Высокая | Средняя |
| **2‑я (reranking)** | Cross‑encoder | Точное ранжирование query‑документ пар | Низкая | Высокая |

**Cross‑encoder** — модель, которая принимает пару (запрос, документ) и выдаёт скоре совместной релевантности. Это медленнее векторного поиска, но значительно точнее.

**Популярные модели cross‑encoder:**

- `cross-encoder/ms-marco-MiniLM-L-12-v2`
- `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Применение в RAG:**

1. После первичного поиска (например, top‑100) реранкер заново оценивает релевантность каждого документа.
2. Документы сортируются по новым скорам.
3. В LLM подаются только top‑k (например, top‑5) наиболее релевантных документов.

---

## 🎯 Планируемые результаты (индикаторы компетенций)

| Компетенция | Индикатор | Уровень |
|-------------|-----------|---------|
| **LLM-3** | 3.1. Проектирует и применяет техники RAG | Б |
| **LLM-3** | 3.2. Работает с векторными хранилищами | Б |
| **LLM-3** | 3.3. Выбирает архитектуры ретривера и считывателя | Б |

**По окончании лекции студент должен:**

- **Знать:** архитектуру RAG (retriever → reader), эволюцию подходов, принципы работы эмбеддингов (BGE‑M3), различия FAISS и Qdrant, стратегии чанкинга (включая sliding window), компоненты гибридного поиска, назначение query rewriting и reranking.
- **Уметь:** обоснованно выбирать модель эмбеддингов, векторную БД и стратегию чанкинга для заданного кейса.
- **Владеть:** терминологией в области контекстной инженерии (RAG, KAG, CAG, hybrid search, RRF, cross‑encoder).

---

## 🔗 Связь с практическими занятиями модуля

| Практическое занятие | Что использует из лекции |
|----------------------|---------------------------|
| **2.2. Реализация пайплайна извлечение→чтение** | Архитектура RAG, выбор модели эмбеддингов, чанкинг, работа с FAISS/Qdrant |
| **2.3. Оптимизация и интеграция RAG** | Гибридный поиск (BM25+dense, RRF), реранкинг (cross‑encoder), query rewriting |
| **2.4. Продвинутые техники и баланс качества** | KAG/CAG, multi‑hop, оптимизация latency |

---

## 🗓️ Структура занятия (90 минут)

| Время | Этап | Содержание | Методические приёмы |
|-------|------|------------|----------------------|
| 0–5 мин | **Организационный момент** | Приветствие, объявление темы, целей и структуры занятия. Актуализация связи с Модулем 1 (Prompt Engineering). | Краткий опрос: «Какие проблемы промпт‑инжиниринга не решает?» |
| 5–15 мин | **Блок 1. Введение: проблема контекста в LLM** | Ограничения БЯМ, галлюцинации, различие параметрической и непараметрической памяти. | Проблемный вопрос: «Почему GPT‑4 не может ответить на вопрос о событиях вчерашнего дня?» Демонстрация примера галлюцинации. |
| 15–30 мин | **Блок 2. RAG: базовый архитектурный паттерн** | Архитектура «retriever → reader». Offline‑фаза (индексация) и Online‑фаза (запрос). | Схема на доске/слайде. Сравнение с работой библиотекаря: «сначала находим книгу, потом читаем и отвечаем». |
| 30–40 мин | **Блок 3. Эволюция RAG. KAG и CAG** | Naive → Advanced → Modular → Agentic RAG. KAG (графы знаний) и CAG (кэширование). | Визуальная временная шкала. Кейс: «Когда CAG лучше RAG?» (повторяющиеся запросы). |
| 40–55 мин | **Блок 4. Эмбеддинги и векторные БД** | Принцип плотных векторных представлений. Модель BGE‑M3. FAISS vs Qdrant: критерии выбора. | Сравнительная таблица. Демонстрация поиска в Qdrant (если возможно). |
| 55–70 мин | **Блок 5. Чанкинг и гибридный поиск** | Стратегии чанкинга, sliding window. Гибридный поиск (BM25 + dense), RRF. | «Проблема Златовласки» — метафора для выбора размера чанка. Сравнение Recall@k для разных стратегий. |
| 70–80 мин | **Блок 6. Query rewriting и reranking** | Зачем переформулировать запрос. Cross‑encoder vs bi‑encoder. Двухстадийный пайплайн. | Сравнение скорости и точности. Пример: как реранкинг исправляет ошибки первичного поиска. |
| 80–85 мин | **Блок 7. Связь с практикой** | Как знания лекции будут применяться в лабораторных работах 2.2–2.5. Обзор требований к практическим заданиям. | Анонс практических работ. Ответы на вопросы. |
| 85–90 мин | **Заключение** | Резюме ключевых выводов. Ответы на вопросы студентов. | Краткий опрос‑рефлексия: «Что было самым важным сегодня?» |

---

## 📚 Рекомендуемая литература

Фундаментальные работы по RAG

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.-t., Rocktäschel, T., Riedel, S., Kiela, D. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks // Advances in Neural Information Processing Systems (NeurIPS), 2020. — Vol. 33. — P. 9459–9474. — https://arxiv.org/abs/2005.11401
2. Guu, K., Lee, K., Tung, Z., Pasupat, P., Chang, M.W. REALM: Retrieval-Augmented Language Model Pre-Training // Proceedings of the 37th International Conference on Machine Learning (ICML), 2020. — P. 3929–3938. — https://arxiv.org/abs/2002.08909
3. Izacard, G., Lewis, P., Lomeli, M., Hosseini, L., Petroni, F., Schick, T., Dwivedi-Yu, J., Joulin, A., Riedel, S., Grave, E. Atlas: Few-shot Learning with Retrieval Augmented Language Models // Journal of Machine Learning Research (JMLR), 2023. — Vol. 24. — P. 1–43. — https://arxiv.org/abs/2208.03299
4. Asai, A., Wu, Z., Wang, Y., Sil, A., Hajishirzi, H. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection // Proceedings of the International Conference on Learning Representations (ICLR), 2024. — https://arxiv.org/abs/2310.11511
5. Jiang, Z., Xu, F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y., Callan, J., Neubig, G. Active Retrieval Augmented Generation // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 7969–7992. — https://arxiv.org/abs/2305.06983
6. Sarthi, P., Abdullah, S., Tuli, A., Khanna, S., Goldie, A., Manning, C.D. RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval // Proceedings of the International Conference on Learning Representations (ICLR), 2024. — https://arxiv.org/abs/2401.18059

Эмбеддинги и векторные представления

7. Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., Liu, Z. BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation // arXiv preprint arXiv:2402.03216, 2024. — https://arxiv.org/abs/2402.03216 | https://huggingface.co/BAAI/bge-m3
8. Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., Yih, W.-t. Dense Passage Retrieval for Open-Domain Question Answering // Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2020. — P. 6769–6781. — https://arxiv.org/abs/2004.04906
9. Xiong, L., Xiong, C., Li, Y., Tang, K.F., Liu, J., Bennett, P., Ahmed, J., Overwijk, A. Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval // Proceedings of the International Conference on Learning Representations (ICLR), 2021. — https://arxiv.org/abs/2007.00808
10. Gao, L., Callan, J. Unsupervised Corpus Aware Language Model Pre-training for Dense Passage Retrieval // Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL), 2022. — P. 2843–2853.
    
Векторный поиск и similarity search

11. Johnson, J., Douze, M., Jégou, H. Billion-Scale Similarity Search with GPUs // IEEE Transactions on Big Data, 2021. — Vol. 7, No. 3. — P. 535–547. — https://ieeexplore.ieee.org/document/8733051 | https://github.com/facebookresearch/faiss
12. Khattab, O., Zaharia, M. ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT // Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR), 2020. — https://arxiv.org/abs/2004.12832

Гибридный поиск и ранжирование

13. Robertson, S., Zaragoza, H. The Probabilistic Relevance Framework: BM25 and Beyond // Foundations and Trends in Information Retrieval, 2009. — Vol. 3, No. 4. — P. 333–389. — DOI: 10.1561/1500000019 — https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf
14. Cormack, G.V., Clarke, C.L.A., Buettcher, S. Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods // Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR), 2009. — P. 758–759. — DOI: 10.1145/1571941.1572114 — https://dl.acm.org/doi/10.1145/1571941.1572114
15. Nogueira, R., Cho, K. Passage Re-ranking with BERT // arXiv preprint arXiv:1901.04085, 2019. — https://arxiv.org/abs/1901.04085
16. Nogueira, R., Yang, W., Cho, K., Lin, J. Multi-Stage Document Ranking with BERT // Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2020. — https://arxiv.org/abs/1910.14424
    
KAG — Knowledge-Augmented Generation

17. Guan, X., Liu, Y., Lin, H., Lu, Y., He, B., Han, X., Sun, L. Mitigating Large Language Model Hallucinations via Autonomous Knowledge Graph-based Retrofitting // Proceedings of the AAAI Conference on Artificial Intelligence (AAAI), 2024. — P. 18126–18134. — https://ojs.aaai.org/index.php/AAAI/article/view/29879
18. Hu, Z., Xu, Y., Yu, W., Wang, S., Yang, Z., Zhu, C., Chang, K.-W., Sun, Y. Empowering Language Models with Knowledge Graph Reasoning for Question Answering // Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2022. — P. 9562–9581.
19. Hu, Y., Lei, Z., Zhang, Z., Pan, B., Ling, C., Zhao, L. GRAG: Graph Retrieval-Augmented Generation // arXiv preprint arXiv:2405.16506, 2024. — https://arxiv.org/abs/2405.16506

CAG — Cache-Augmented Generation

20. Gim, J., Park, J., Jeong, S., Kim, S. Prompt Cache: Modular Attention Reuse for Low-Latency Inference // Proceedings of the 2024 Annual Meeting of the Association for Computational Linguistics (ACL), 2024.
21. Liu, Z., Desai, A., Liao, F., Sivashunmugam, V., Lu, B., Khandelwal, D., Chellappa, R., Krishnamurthy, A. RAGCache: Efficient Knowledge Caching for Retrieval-Augmented Generation // arXiv preprint arXiv:2404.12457, 2024. — https://arxiv.org/abs/2404.12457

Query Rewriting

22. Ma, X., Gong, Y., He, P., Zhao, H., Duan, N. Query Rewriting for Retrieval-Augmented Large Language Models // arXiv preprint arXiv:2305.14283, 2023. — https://arxiv.org/abs/2305.14283
23. Gao, L., Ma, X., Lin, J., Callan, J. Precise Zero-Shot Dense Retrieval without Relevance Labels // Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL), 2023. — (HyDE — Hypothetical Document Embeddings) — https://arxiv.org/abs/2212.10496
24. Wang, L., Yang, N., Wei, F. Query2doc: Query Expansion with Large Language Models // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 9414–9423. — https://arxiv.org/abs/2303.07678

Оценка качества и метрики

25. Liu, N.F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., Liang, P. Lost in the Middle: How Language Models Use Long Contexts // Transactions of the Association for Computational Linguistics (TACL), 2024. — Vol. 12. — P. 157–173. — https://arxiv.org/abs/2307.03172
26. Saad-Falcon, J., Khattab, O., Potts, C., Zaharia, M. ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems // Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL), 2024. — P. 338–354.
27. Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., Zhu, C. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment // Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP), 2023. — P. 2511–2522. — https://arxiv.org/abs/2303.16634
28. Chen, J., Lin, H., Han, X., Sun, L. Benchmarking Large Language Models in Retrieval-Augmented Generation // Proceedings of the AAAI Conference on Artificial Intelligence (AAAI), 2024. — Vol. 38. — P. 17754–17762.
