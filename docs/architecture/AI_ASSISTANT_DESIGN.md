# AI Assistant Design - Technical Specification

## Table of Contents
1. [Overview](#overview)
2. [Core Capabilities](#core-capabilities)
3. [RAG Pipeline Architecture](#rag-pipeline-architecture)
4. [Embedding Strategy](#embedding-strategy)
5. [Retrieval and Ranking](#retrieval-and-ranking)
6. [Prompt Engineering](#prompt-engineering)
7. [Real-time Chat Implementation](#real-time-chat-implementation)
8. [Context Management](#context-management)
9. [Performance Optimization](#performance-optimization)
10. [Safety and Rate Limiting](#safety-and-rate-limiting)

## Overview

The AI Assistant is designed to be an intelligent companion for blog readers, providing deep understanding of technical content, making connections between articles, and offering insights about the author's expertise. Built on a Retrieval-Augmented Generation (RAG) architecture, it combines the power of large language models with specific knowledge from the blog's content.

### Design Goals
- **Accurate**: Provide factually correct information from articles
- **Contextual**: Understand relationships between different topics
- **Responsive**: Stream responses in real-time
- **Personal**: Answer questions about the author's expertise
- **Efficient**: Optimize for cost and performance

### Technical Requirements
- Response latency: <2 seconds for first token
- Context window: Up to 8,000 tokens
- Concurrent users: Support 10 simultaneous conversations
- Cost target: <$20/month for AI operations
- Accuracy: 95%+ relevance for retrieved content

## Core Capabilities

### 1. Article Understanding
The assistant can comprehend and explain technical concepts from articles:
- **Summarization**: Provide concise summaries of complex articles
- **Explanation**: Break down technical concepts for different expertise levels
- **Code Analysis**: Explain code snippets and their purpose
- **Concept Extraction**: Identify and explain key technical concepts

### 2. Cross-Article Intelligence
Connect information across multiple articles:
- **Topic Mapping**: Identify related articles on similar topics
- **Learning Paths**: Suggest reading order for topic mastery
- **Evolution Tracking**: Show how concepts evolved across articles
- **Dependency Understanding**: Identify prerequisite knowledge

### 3. Author Expertise
Provide insights about the author:
- **Skills and Experience**: Answer questions about technical expertise
- **Project History**: Discuss past projects and achievements
- **Writing Focus**: Explain areas of specialization
- **Professional Background**: Share relevant career information

### 4. Interactive Learning
Facilitate deeper understanding:
- **Q&A**: Answer specific questions about article content
- **Examples**: Provide additional code examples
- **Clarification**: Explain unclear passages
- **Deep Dives**: Elaborate on briefly mentioned topics

## RAG Pipeline Architecture

### High-Level Pipeline

```mermaid
graph LR
    A[User Query] --> B[Query Processing]
    B --> C[Embedding Generation]
    C --> D[Vector Search]
    D --> E[Context Retrieval]
    E --> F[Reranking]
    F --> G[Prompt Construction]
    G --> H[LLM Generation]
    H --> I[Response Streaming]
    I --> J[User Interface]
```

### Detailed Component Design

#### 1. Query Processing

```python
class QueryProcessor:
    def process(self, query: str) -> ProcessedQuery:
        """
        Transform raw user query for optimal retrieval
        """
        # Clean and normalize
        query = self.normalize_text(query)

        # Detect query intent
        intent = self.classify_intent(query)

        # Extract entities (article names, technical terms)
        entities = self.extract_entities(query)

        # Expand with synonyms and related terms
        expanded = self.expand_query(query, entities)

        return ProcessedQuery(
            original=query,
            normalized=query,
            intent=intent,
            entities=entities,
            expanded=expanded
        )

    def classify_intent(self, query: str) -> Intent:
        """
        Identify user's intention
        """
        intents = {
            'explanation': ['explain', 'what is', 'how does'],
            'code': ['code', 'example', 'implementation'],
            'comparison': ['difference', 'compare', 'vs'],
            'author': ['you', 'your experience', 'author'],
            'navigation': ['articles about', 'where can I find']
        }
        # Intent classification logic
        return detected_intent
```

#### 2. Embedding Generation

```python
class EmbeddingService:
    def __init__(self):
        self.model = "text-embedding-3-small"  # OpenAI's efficient model
        self.dimension = 1536

    async def embed_query(self, text: str) -> np.ndarray:
        """
        Generate query embedding with caching
        """
        # Check cache first
        cached = await self.cache.get(f"embed:{hash(text)}")
        if cached:
            return cached

        # Generate embedding
        response = await openai.embeddings.create(
            model=self.model,
            input=text
        )
        embedding = response.data[0].embedding

        # Cache for 1 hour
        await self.cache.set(
            f"embed:{hash(text)}",
            embedding,
            expire=3600
        )

        return np.array(embedding)
```

#### 3. Vector Search

```python
class VectorSearchService:
    def __init__(self, index_name: str):
        self.index_name = index_name
        self.top_k = 10  # Retrieve more than needed for reranking

    async def search(
        self,
        query_vector: np.ndarray,
        filters: dict = None
    ) -> List[SearchResult]:
        """
        Perform similarity search using pgvector
        """
        query = """
            SELECT
                id,
                article_id,
                chunk_text,
                chunk_metadata,
                1 - (embedding <=> %s::vector) as similarity
            FROM article_embeddings
            WHERE 1=1
        """

        # Apply filters if provided
        if filters:
            if 'article_id' in filters:
                query += f" AND article_id = '{filters['article_id']}'"
            if 'published_after' in filters:
                query += f" AND created_at > '{filters['published_after']}'"

        query += """
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        results = await self.db.fetch(
            query,
            query_vector,
            query_vector,
            self.top_k
        )

        return [SearchResult(**r) for r in results]
```

## Embedding Strategy

### Document Processing Pipeline

```python
class DocumentProcessor:
    def process_article(self, article: Article) -> List[Chunk]:
        """
        Convert article into optimized chunks for embedding
        """
        chunks = []

        # 1. Extract and process main content
        content_chunks = self.chunk_content(article.content)

        # 2. Process code blocks separately
        code_chunks = self.extract_code_blocks(article.content)

        # 3. Create metadata-enriched chunks
        for chunk in content_chunks + code_chunks:
            enriched = self.enrich_chunk(chunk, article)
            chunks.append(enriched)

        return chunks

    def chunk_content(self, content: str) -> List[Chunk]:
        """
        Smart chunking that respects content boundaries
        """
        chunks = []

        # Split by headers first (maintain structure)
        sections = self.split_by_headers(content)

        for section in sections:
            # Use sliding window with overlap
            section_chunks = self.sliding_window_chunk(
                text=section.text,
                chunk_size=800,  # tokens
                overlap=200       # tokens
            )

            for chunk_text in section_chunks:
                chunks.append(Chunk(
                    text=chunk_text,
                    type='content',
                    metadata={
                        'section': section.title,
                        'level': section.level
                    }
                ))

        return chunks
```

### Chunk Optimization

```python
class ChunkOptimizer:
    def optimize_for_retrieval(self, chunk: Chunk) -> Chunk:
        """
        Enhance chunk for better retrieval
        """
        # Add contextual information
        chunk.enhanced_text = self.add_context(chunk)

        # Generate title for chunk
        chunk.title = self.generate_chunk_title(chunk)

        # Extract key terms
        chunk.keywords = self.extract_keywords(chunk.text)

        # Add semantic tags
        chunk.tags = self.generate_semantic_tags(chunk)

        return chunk

    def add_context(self, chunk: Chunk) -> str:
        """
        Prepend context for better understanding
        """
        context_parts = []

        if chunk.metadata.get('article_title'):
            context_parts.append(f"Article: {chunk.metadata['article_title']}")

        if chunk.metadata.get('section'):
            context_parts.append(f"Section: {chunk.metadata['section']}")

        context = " | ".join(context_parts)
        return f"{context}\n\n{chunk.text}" if context else chunk.text
```

### Embedding Storage Schema

```sql
CREATE TABLE article_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_type VARCHAR(50), -- 'content', 'code', 'metadata'
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}',

    -- Metadata fields for filtering
    article_title TEXT,
    article_slug VARCHAR(255),
    section_title TEXT,
    published_at TIMESTAMP,

    -- Search optimization
    keywords TEXT[],
    semantic_tags TEXT[],

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(article_id, chunk_index)
);

-- Indexes for performance
CREATE INDEX idx_embeddings_vector ON article_embeddings
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_embeddings_article ON article_embeddings(article_id);
CREATE INDEX idx_embeddings_published ON article_embeddings(published_at DESC);
CREATE INDEX idx_embeddings_keywords ON article_embeddings USING GIN(keywords);
```

## Retrieval and Ranking

### Multi-Stage Retrieval

```python
class HybridRetriever:
    async def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Document]:
        """
        Combine multiple retrieval strategies
        """
        # Stage 1: Vector similarity search
        vector_results = await self.vector_search(query, top_k=20)

        # Stage 2: Keyword search (BM25)
        keyword_results = await self.keyword_search(query, top_k=20)

        # Stage 3: Combine and rerank
        combined = self.combine_results(
            vector_results,
            keyword_results,
            weights={'vector': 0.7, 'keyword': 0.3}
        )

        # Stage 4: Cross-encoder reranking
        reranked = await self.rerank_with_cross_encoder(
            query,
            combined[:15]  # Rerank top 15
        )

        return reranked[:top_k]

    async def rerank_with_cross_encoder(
        self,
        query: str,
        documents: List[Document]
    ) -> List[Document]:
        """
        Use a cross-encoder for precise relevance scoring
        """
        pairs = [(query, doc.text) for doc in documents]

        scores = await self.cross_encoder.predict(pairs)

        # Sort by relevance score
        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, score in ranked]
```

### Context Window Management

```python
class ContextManager:
    def __init__(self, max_tokens: int = 6000):
        self.max_tokens = max_tokens

    def build_context(
        self,
        retrieved_docs: List[Document],
        query: str
    ) -> str:
        """
        Optimize context for LLM consumption
        """
        context_parts = []
        total_tokens = 0

        # Priority order for inclusion
        for doc in retrieved_docs:
            doc_tokens = self.count_tokens(doc.text)

            if total_tokens + doc_tokens <= self.max_tokens:
                context_parts.append(
                    self.format_document(doc)
                )
                total_tokens += doc_tokens
            else:
                # Truncate if necessary
                remaining = self.max_tokens - total_tokens
                if remaining > 100:  # Only include if meaningful
                    truncated = self.truncate_text(doc.text, remaining)
                    context_parts.append(
                        self.format_document(doc, truncated)
                    )
                break

        return "\n\n---\n\n".join(context_parts)

    def format_document(
        self,
        doc: Document,
        text: str = None
    ) -> str:
        """
        Format document for context
        """
        text = text or doc.text

        return f"""
[Source: {doc.article_title} - {doc.section_title}]
Published: {doc.published_at}

{text}
        """.strip()
```

## Prompt Engineering

### System Prompts

```python
SYSTEM_PROMPTS = {
    'default': """
You are an AI assistant for a technical blog focused on machine learning and LLM operations.
You have access to all published articles and deep knowledge about their content.

Your capabilities:
1. Explain technical concepts clearly and accurately
2. Provide code examples and explanations
3. Make connections between different articles
4. Share insights about the author's expertise
5. Guide readers to relevant content

Guidelines:
- Always cite specific articles when referencing content
- Be technically accurate and precise
- Adapt explanations to the user's apparent expertise level
- If unsure about something, acknowledge limitations
- Suggest related articles for further reading

Context about the blog:
- Author: {author_name}
- Focus: {blog_focus}
- Total articles: {article_count}
""",

    'code_focused': """
You are a code-focused assistant for a technical blog. When discussing code:
- Provide clear, well-commented examples
- Explain the reasoning behind implementation choices
- Highlight best practices and potential pitfalls
- Suggest improvements or alternatives when relevant
""",

    'author_info': """
You have detailed knowledge about the blog author:
{author_bio}

Professional experience:
{experience}

Areas of expertise:
{expertise}

When answering questions about the author, be informative but maintain appropriate boundaries.
"""
}
```

### Dynamic Prompt Construction

```python
class PromptBuilder:
    def build_prompt(
        self,
        query: str,
        context: str,
        conversation_history: List[Message] = None
    ) -> str:
        """
        Construct optimal prompt for the LLM
        """
        prompt_parts = []

        # Add conversation history if exists
        if conversation_history:
            history = self.format_conversation_history(
                conversation_history[-4:]  # Last 4 exchanges
            )
            prompt_parts.append(f"Previous conversation:\n{history}")

        # Add retrieved context
        prompt_parts.append(f"Relevant content from articles:\n{context}")

        # Add user query with instructions
        prompt_parts.append(f"""
Current user question: {query}

Please provide a comprehensive answer based on the article content above.
If the content doesn't fully address the question, acknowledge this and
provide the best answer possible with available information.
        """)

        return "\n\n".join(prompt_parts)

    def add_citations(self, response: str, sources: List[Document]) -> str:
        """
        Add citations to the response
        """
        # Extract article references
        cited_articles = self.extract_cited_articles(response, sources)

        if cited_articles:
            citations = "\n\n**Sources:**\n"
            for article in cited_articles:
                citations += f"- [{article.title}](/articles/{article.slug})\n"

            return response + citations

        return response
```

## Real-time Chat Implementation

### WebSocket Handler

```python
class ChatWebSocketHandler:
    async def handle_connection(self, websocket: WebSocket):
        """
        Manage WebSocket lifecycle for chat
        """
        await websocket.accept()
        session_id = str(uuid.uuid4())

        try:
            # Initialize session
            session = await self.create_session(session_id, websocket)

            # Handle messages
            async for message in websocket.iter_text():
                await self.handle_message(session, message)

        except WebSocketDisconnect:
            await self.cleanup_session(session_id)

    async def handle_message(self, session: ChatSession, message: str):
        """
        Process incoming chat message
        """
        try:
            # Parse message
            data = json.loads(message)

            # Rate limiting check
            if not await self.check_rate_limit(session.id):
                await session.websocket.send_json({
                    'type': 'error',
                    'message': 'Rate limit exceeded. Please wait.'
                })
                return

            # Process based on message type
            if data['type'] == 'query':
                await self.process_query(session, data['content'])
            elif data['type'] == 'feedback':
                await self.process_feedback(session, data)

        except Exception as e:
            await self.send_error(session, str(e))
```

### Streaming Response

```python
class StreamingResponseHandler:
    async def stream_response(
        self,
        session: ChatSession,
        query: str
    ):
        """
        Stream LLM response to client
        """
        # Retrieve context
        context = await self.retriever.retrieve(query)

        # Build prompt
        prompt = self.prompt_builder.build_prompt(
            query,
            context,
            session.history
        )

        # Stream from LLM
        async for chunk in self.llm.stream_completion(prompt):
            # Send each chunk immediately
            await session.websocket.send_json({
                'type': 'stream',
                'content': chunk.content,
                'finished': False
            })

            # Store for context
            session.current_response += chunk.content

        # Send completion signal
        await session.websocket.send_json({
            'type': 'stream',
            'content': '',
            'finished': True,
            'sources': self.format_sources(context)
        })

        # Update conversation history
        session.history.append(
            Message(role='user', content=query)
        )
        session.history.append(
            Message(role='assistant', content=session.current_response)
        )
```

### Frontend Integration

```typescript
// React component for chat interface
export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Establish WebSocket connection
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'stream') {
        if (data.finished) {
          setIsStreaming(false);
          // Add sources if provided
          if (data.sources) {
            setMessages(prev => [...prev, {
              type: 'sources',
              content: data.sources
            }]);
          }
        } else {
          // Append to current message
          setMessages(prev => {
            const last = prev[prev.length - 1];
            if (last?.type === 'assistant') {
              last.content += data.content;
              return [...prev.slice(0, -1), last];
            }
            return [...prev, {
              type: 'assistant',
              content: data.content
            }];
          });
        }
      }
    };

    wsRef.current = ws;

    return () => ws.close();
  }, []);

  const sendMessage = (content: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'query',
        content
      }));
      setIsStreaming(true);
      setMessages(prev => [...prev, {
        type: 'user',
        content
      }]);
    }
  };

  return (
    <ChatInterface
      messages={messages}
      onSendMessage={sendMessage}
      isStreaming={isStreaming}
      isConnected={isConnected}
    />
  );
}
```

## Context Management

### Conversation Memory

```python
class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.memories = {}  # session_id -> memory

    async def get_context(
        self,
        session_id: str,
        include_turns: int = 4
    ) -> List[Message]:
        """
        Retrieve relevant conversation history
        """
        if session_id not in self.memories:
            return []

        memory = self.memories[session_id]

        # Get recent turns
        recent = memory.messages[-include_turns * 2:]

        # Summarize older context if exists
        if len(memory.messages) > include_turns * 2:
            summary = await self.summarize_history(
                memory.messages[:-include_turns * 2]
            )
            return [Message(role='system', content=summary)] + recent

        return recent

    async def summarize_history(
        self,
        messages: List[Message]
    ) -> str:
        """
        Summarize older conversation for context
        """
        conversation = self.format_messages(messages)

        prompt = f"""
        Summarize the key points from this conversation:
        {conversation}

        Focus on: user's questions, topics discussed, any unresolved items.
        Keep it concise (2-3 sentences).
        """

        summary = await self.llm.complete(prompt, max_tokens=150)
        return f"Previous discussion summary: {summary}"
```

### Author Context Injection

```python
class AuthorContextProvider:
    def __init__(self):
        self.author_info = self.load_author_info()

    def inject_author_context(self, query: str) -> dict:
        """
        Add author information when relevant
        """
        if self.is_author_query(query):
            return {
                'bio': self.author_info['bio'],
                'expertise': self.author_info['expertise'],
                'experience': self.author_info['experience'],
                'projects': self.author_info['recent_projects']
            }
        return {}

    def is_author_query(self, query: str) -> bool:
        """
        Detect if query is about the author
        """
        author_keywords = [
            'you', 'your experience', 'author', 'writer',
            'your background', 'your expertise', 'tell me about yourself'
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in author_keywords)
```

## Performance Optimization

### Caching Strategy

```python
class CacheManager:
    def __init__(self):
        self.cache_layers = {
            'embedding': TTLCache(maxsize=1000, ttl=3600),
            'search': TTLCache(maxsize=500, ttl=1800),
            'response': TTLCache(maxsize=200, ttl=900)
        }

    async def get_cached_response(
        self,
        query: str
    ) -> Optional[str]:
        """
        Check if we have a cached response
        """
        # Normalize query for cache key
        cache_key = self.generate_cache_key(query)

        # Check response cache
        cached = self.cache_layers['response'].get(cache_key)
        if cached:
            return cached

        # Check for semantically similar cached queries
        similar = await self.find_similar_cached(query)
        if similar and similar.similarity > 0.95:
            return similar.response

        return None

    def generate_cache_key(self, text: str) -> str:
        """
        Generate deterministic cache key
        """
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
```

### Batch Processing

```python
class BatchEmbeddingProcessor:
    async def process_articles_batch(
        self,
        articles: List[Article]
    ):
        """
        Efficiently process multiple articles
        """
        all_chunks = []

        # Step 1: Chunk all articles
        for article in articles:
            chunks = self.chunker.chunk_article(article)
            all_chunks.extend(chunks)

        # Step 2: Batch embed chunks
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]

            # Generate embeddings in parallel
            texts = [chunk.text for chunk in batch]
            embeddings = await self.generate_embeddings_batch(texts)

            # Store in database
            await self.store_embeddings_batch(
                chunks=batch,
                embeddings=embeddings
            )

    async def generate_embeddings_batch(
        self,
        texts: List[str]
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently
        """
        response = await openai.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        return [np.array(item.embedding) for item in response.data]
```

## Safety and Rate Limiting

### Rate Limiting Implementation

```python
class RateLimiter:
    def __init__(self):
        self.limits = {
            'chat_message': {'rate': 10, 'per': 60},      # 10 per minute
            'embedding_generation': {'rate': 100, 'per': 3600},  # 100 per hour
            'article_search': {'rate': 30, 'per': 60}     # 30 per minute
        }

    async def check_rate_limit(
        self,
        identifier: str,
        action: str
    ) -> bool:
        """
        Check if action is within rate limits
        """
        key = f"ratelimit:{action}:{identifier}"
        limit = self.limits.get(action, {'rate': 10, 'per': 60})

        # Get current count
        current = await self.redis.incr(key)

        # Set expiry on first request
        if current == 1:
            await self.redis.expire(key, limit['per'])

        # Check if exceeded
        if current > limit['rate']:
            return False

        return True

    async def get_remaining(
        self,
        identifier: str,
        action: str
    ) -> dict:
        """
        Get remaining rate limit info
        """
        key = f"ratelimit:{action}:{identifier}"
        limit = self.limits.get(action)

        current = await self.redis.get(key) or 0
        ttl = await self.redis.ttl(key)

        return {
            'limit': limit['rate'],
            'remaining': max(0, limit['rate'] - int(current)),
            'reset_in': ttl if ttl > 0 else 0
        }
```

### Content Safety

```python
class ContentSafetyFilter:
    async def filter_query(self, query: str) -> tuple[bool, str]:
        """
        Check if query is safe to process
        """
        # Check for prompt injection attempts
        if self.detect_prompt_injection(query):
            return False, "Query contains potentially harmful content"

        # Check for PII
        if self.contains_pii(query):
            return False, "Please avoid sharing personal information"

        # Check content appropriateness
        if not self.is_appropriate(query):
            return False, "Query contains inappropriate content"

        return True, "ok"

    def detect_prompt_injection(self, text: str) -> bool:
        """
        Detect potential prompt injection attempts
        """
        injection_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "forget everything",
            "system: ",
            "admin: ",
            "sudo "
        ]

        text_lower = text.lower()
        return any(pattern in text_lower for pattern in injection_patterns)
```

### Error Handling

```python
class ErrorHandler:
    async def handle_error(
        self,
        error: Exception,
        context: dict
    ) -> dict:
        """
        Gracefully handle various error scenarios
        """
        if isinstance(error, RateLimitException):
            return {
                'type': 'rate_limit',
                'message': 'Too many requests. Please wait.',
                'retry_after': error.retry_after
            }

        elif isinstance(error, OpenAIException):
            # Log for monitoring
            await self.log_error(error, context)

            return {
                'type': 'service_error',
                'message': 'AI service temporarily unavailable.',
                'fallback': await self.get_fallback_response(context)
            }

        elif isinstance(error, DatabaseException):
            return {
                'type': 'retrieval_error',
                'message': 'Unable to retrieve content. Please try again.',
            }

        else:
            # Unknown error - log and return generic message
            await self.log_error(error, context)

            return {
                'type': 'unknown_error',
                'message': 'An unexpected error occurred.'
            }

    async def get_fallback_response(self, context: dict) -> str:
        """
        Provide fallback when AI service fails
        """
        query = context.get('query', '')

        # Try to provide basic help
        if 'article' in query.lower():
            return "I'm having trouble accessing the AI service, but you can browse articles directly from the homepage."

        return "I'm temporarily unable to process your request. Please try again in a moment."
```

## Monitoring and Analytics

### Performance Metrics

```python
class AIMetricsCollector:
    def __init__(self):
        self.metrics = {
            'query_latency': [],
            'retrieval_relevance': [],
            'response_quality': [],
            'cache_hit_rate': 0,
            'error_rate': 0
        }

    async def record_query(
        self,
        query: str,
        response_time: float,
        retrieved_docs: List[Document],
        cache_hit: bool
    ):
        """
        Record metrics for analysis
        """
        # Latency
        self.metrics['query_latency'].append(response_time)

        # Cache performance
        if cache_hit:
            self.metrics['cache_hit_rate'] += 1

        # Log to monitoring service
        await self.send_to_monitoring({
            'event': 'ai_query',
            'latency': response_time,
            'cache_hit': cache_hit,
            'doc_count': len(retrieved_docs),
            'timestamp': datetime.utcnow().isoformat()
        })

    async def analyze_performance(self) -> dict:
        """
        Analyze collected metrics
        """
        return {
            'avg_latency': np.mean(self.metrics['query_latency']),
            'p95_latency': np.percentile(self.metrics['query_latency'], 95),
            'cache_hit_rate': self.metrics['cache_hit_rate'] / len(self.metrics['query_latency']),
            'queries_processed': len(self.metrics['query_latency'])
        }
```

## Conclusion

This AI Assistant design provides a robust, scalable, and cost-effective solution for enhancing the blog reading experience. Key strengths include:

1. **Comprehensive RAG Pipeline**: Efficient retrieval and generation with multiple optimization layers
2. **Real-time Interaction**: WebSocket-based streaming for responsive user experience
3. **Smart Context Management**: Maintains conversation context while managing token limits
4. **Performance Optimized**: Multi-level caching and batch processing for efficiency
5. **Safety First**: Rate limiting, content filtering, and error handling
6. **Cost Effective**: Designed to operate within $20/month budget using efficient models

The modular architecture allows for incremental improvements and easy maintenance while providing a powerful AI assistant that truly understands and can discuss the blog's content intelligently.