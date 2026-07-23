import numpy as np
from typing import List, Dict, Set

def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Доля релевантных документов в top-k."""
    if not relevant_ids:
        return 0.0
    retrieved_set = set(retrieved_ids[:k])
    return len(retrieved_set & relevant_ids) / len(relevant_ids)

def mrr_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Обратный ранг первого релевантного документа."""
    for i, doc_id in enumerate(retrieved_ids[:k]):
        if doc_id in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0

def ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Normalized Discounted Cumulative Gain."""
    # Упрощённая версия: binary relevance
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k]):
        rel = 1.0 if doc_id in relevant_ids else 0.0
        dcg += rel / np.log2(i + 2)  # i+2 потому что log2(2)=1

    # IDCG (идеальный случай)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant_ids), k)))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_retriever(retriever_func, test_queries: List[Dict], k: int = 5) -> Dict:
    """Запускает оценку на тестовом наборе."""
    recalls, mrrs, ndcgs = [], [], []
    for test in test_queries:
        query = test['query']
        relevant = set(test['relevant_doc_ids'])
        # Получаем ID документов от ретривера
        retrieved_ids = retriever_func(query, k=k*3)  # берём с запасом
        retrieved_ids = [doc['source'] for doc in retrieved_ids]  # упрощённо
        recalls.append(recall_at_k(retrieved_ids, relevant, k))
        mrrs.append(mrr_at_k(retrieved_ids, relevant, k))
        ndcgs.append(ndcg_at_k(retrieved_ids, relevant, k))
    return {
        'recall@k': np.mean(recalls),
        'mrr@k': np.mean(mrrs),
        'ndcg@k': np.mean(ndcgs),
        'k': k
    }
