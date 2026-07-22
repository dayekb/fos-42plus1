from src.hybrid_retriever import HybridRetriever
from src.reranker import CrossEncoderReranker
from src.query_rewriter import QueryRewriter
from src.embeddings import EmbeddingModel
from src.vector_store import FAISSVectorStore
from src.chunking import load_documents, chunk_text
from typing import Dict, List

class OptimizedRAGPipeline:
    def __init__(self, dense_store, bm25_retriever):
        self.dense_store = dense_store
        self.bm25_retriever = bm25_retriever
        self.hybrid_retriever = HybridRetriever(dense_store, bm25_retriever)
        self.reranker = CrossEncoderReranker()
        self.rewriter = QueryRewriter(use_llm=True)
        self.embedder = EmbeddingModel()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Полный пайплайн ретривала с оптимизациями."""
        # 1. Переформулировка запроса
        rewritten_query = self.rewriter.rewrite(query)
        
        # 2. Гибридный поиск (возвращает top-20 для реранкинга)
        candidates = self.hybrid_retriever.search(rewritten_query, k=20)
        
        # 3. Реранкинг cross-encoder
        reranked = self.reranker.rerank(rewritten_query, candidates, top_k=top_k)
        
        # 4. Возвращаем метаданные
        return [meta for meta, score in reranked]
    
    def answer(self, query: str, llm_model: str = "gpt-4o-mini") -> Dict:
        """Полный ответ с генерацией."""
        from src.generation import generate_answer
        from src.retrieval import retrieve_context
        
        # Получаем контекст
        context, sources = retrieve_context(query, self.embedder, self.dense_store, k=5)
        
        # Но используем оптимизированный поиск для контекста
        optimized_context_chunks = self.retrieve(query, top_k=5)
        optimized_context = "\n\n".join([chunk['text'] for chunk in optimized_context_chunks])
        optimized_sources = [{'source': c['source'], 'index': i} for i, c in enumerate(optimized_context_chunks)]
        
        # Генерация ответа
        result = generate_answer(query, optimized_context, optimized_sources)
        return result
