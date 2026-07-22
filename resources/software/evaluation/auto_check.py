import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline_baseline import BaselineRAGPipeline
from src.pipeline_optimized import OptimizedRAGPipeline
from evaluation.metrics import evaluate_retriever

# 1. Загрузка тестовых запросов
with open('evaluation/test_queries.json', 'r') as f:
    test_queries = json.load(f)

# 2. Инициализация пайплайнов (загрузка индекса)
from src.vector_store import FAISSVectorStore
from src.embeddings import EmbeddingModel
from src.hybrid_retriever import BM25Retriever

# Загрузка подготовленных данных
vector_store = FAISSVectorStore.load('index/')
embedder = EmbeddingModel()
bm25 = BM25Retriever()
bm25.fit(vector_store.metadata)  # Загружаем чанки

baseline = BaselineRAGPipeline(vector_store, embedder)
optimized = OptimizedRAGPipeline(vector_store, bm25)

# 3. Оценка Baseline (чистый Dense)
print("Оценка Baseline (Dense only)...")
def baseline_retriever(query, k):
    return baseline.retrieve(query, top_k=k)
baseline_metrics = evaluate_retriever(baseline_retriever, test_queries, k=5)

# 4. Оценка Optimized (Hybrid + Rerank + Rewrite)
print("Оценка Optimized (Hybrid + Rerank + Rewrite)...")
def optimized_retriever(query, k):
    return optimized.retrieve(query, top_k=k)
optimized_metrics = evaluate_retriever(optimized_retriever, test_queries, k=5)

# 5. Сравнение и проверка порогов
print("\n=== РЕЗУЛЬТАТЫ АВТОПРОВЕРКИ ===")
print(f"Baseline Recall@5: {baseline_metrics['recall@k']:.4f}")
print(f"Optimized Recall@5: {optimized_metrics['recall@k']:.4f}")

improvement = (optimized_metrics['recall@k'] - baseline_metrics['recall@k']) / baseline_metrics['recall@k'] * 100

# ПРОВЕРКА: улучшение должно быть ≥ 15% ИЛИ абсолютный Recall@5 ≥ 0.85
threshold_improvement = 15.0
threshold_absolute = 0.85

# Сохранение результатов в JSON
results = {
    "baseline": baseline_metrics,
    "optimized": optimized_metrics,
    "improvement_percent": improvement,
    "pass": (improvement >= threshold_improvement) or (optimized_metrics['recall@k'] >= threshold_absolute)
}

with open('experiments/evaluation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Вывод результата автопроверки
if results["pass"]:
    print(f"\n✅ АВТОПРОВЕРКА ПРОЙДЕНА! Улучшение: {improvement:.1f}%")
    print("   (Порог: +15% ИЛИ абсолютный Recall@5 ≥ 0.85)")
    sys.exit(0)
else:
    print(f"\n❌ АВТОПРОВЕРКА НЕ ПРОЙДЕНА. Улучшение: {improvement:.1f}%")
    print("   Рекомендации: проверьте реализацию RRF, реранкинга и query rewriting.")
    sys.exit(1)
