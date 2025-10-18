# Implementation Guide - Building the AI-Powered Blog

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Phase 1: Basic Blog Foundation](#phase-1-basic-blog-foundation)
4. [Phase 2: Database and Content Management](#phase-2-database-and-content-management)
5. [Phase 3: FastAPI AI Service](#phase-3-fastapi-ai-service)
6. [Phase 4: AI Assistant Integration](#phase-4-ai-assistant-integration)
7. [Phase 5: Production Deployment](#phase-5-production-deployment)
8. [Testing Strategy](#testing-strategy)
9. [Cost Optimization](#cost-optimization)
10. [Maintenance Guide](#maintenance-guide)

## Prerequisites

### Required Software
- **Node.js** 20+ LTS
- **Python** 3.11+
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- **pnpm** (for Node package management)

### Required Accounts (Free Tiers)
- **GitHub** - Code repository
- **Vercel** - Frontend hosting (optional)
- **Supabase** - PostgreSQL database (optional alternative to Docker)
- **OpenAI** - API access ($20 credit to start)

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/ai-blog-explorer.git
cd ai-blog-explorer

# Install Node.js dependencies manager
npm install -g pnpm

# Install Python package manager
pip install --upgrade pip
pip install poetry  # Alternative: use pip with requirements.txt
```

## Project Setup

### 1. Directory Structure

```bash
# Create project structure
mkdir -p ai-blog-explorer/{frontend,backend,docker,docs}
cd ai-blog-explorer

# Initialize git
git init
echo "node_modules/\n.env\n*.pyc\n__pycache__/\n.next/\nvenv/" > .gitignore

# Create environment file
cp .env.example .env
```

### 2. Docker Environment

```bash
# Start Docker services
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps

# Check PostgreSQL connection
docker-compose exec postgres psql -U bloguser -d blogdb -c "SELECT version();"

# Check Redis connection
docker-compose exec redis redis-cli ping
```

## Phase 1: Basic Blog Foundation

### Step 1.1: Initialize Next.js Application

```bash
cd frontend

# Create Next.js app with TypeScript and Tailwind
pnpm create next-app@latest . --typescript --tailwind --app --no-src-dir

# Install additional dependencies
pnpm add @prisma/client prisma
pnpm add @tiptap/react @tiptap/starter-kit @tiptap/extension-code-block-lowlight
pnpm add lucide-react clsx tailwind-merge
pnpm add next-auth
pnpm add -D @types/node
```

### Step 1.2: Configure Next.js

Create `next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost', 'res.cloudinary.com'],
  },
  experimental: {
    serverActions: true,
  },
  env: {
    DATABASE_URL: process.env.DATABASE_URL,
  }
}

module.exports = nextConfig
```

### Step 1.3: Create Basic Layout

Create `app/layout.tsx`:
```typescript
import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI-Powered Tech Blog',
  description: 'Technical articles with AI assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold">Tech Blog</h1>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
```

### Step 1.4: Create Home Page

Create `app/page.tsx`:
```typescript
export default function Home() {
  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">Welcome to My Tech Blog</h1>
      <p className="text-lg text-gray-600">
        Exploring Machine Learning and LLM Operations
      </p>
    </div>
  )
}
```

### Step 1.5: Add Health Check Endpoint

Create `app/api/health/route.ts`:
```typescript
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'next-app'
  })
}
```

### Step 1.6: Test Basic Setup

```bash
# Run development server
pnpm dev

# In another terminal, test endpoints
curl http://localhost:3000/api/health

# Build for production
pnpm build
```

## Phase 2: Database and Content Management

### Step 2.1: Initialize Prisma

```bash
# Initialize Prisma with PostgreSQL
pnpm prisma init

# Set DATABASE_URL in .env
# DATABASE_URL="postgresql://bloguser:blogpass@localhost:5432/blogdb?schema=public"
```

### Step 2.2: Define Database Schema

Create `prisma/schema.prisma`:
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  role      String   @default("admin")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  articles Article[]
}

model Article {
  id          String   @id @default(uuid())
  slug        String   @unique
  title       String
  content     String   @db.Text
  excerpt     String?
  coverImage  String?
  tags        String[]
  status      String   @default("draft")
  publishedAt DateTime?
  viewCount   Int      @default(0)
  readTime    Int?

  authorId String
  author   User   @relation(fields: [authorId], references: [id])

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  embeddings ArticleEmbedding[]

  @@index([slug])
  @@index([publishedAt])
  @@index([status])
}

model ArticleEmbedding {
  id          String   @id @default(uuid())
  articleId   String
  article     Article  @relation(fields: [articleId], references: [id], onDelete: Cascade)
  chunkIndex  Int
  chunkText   String   @db.Text
  chunkType   String   @default("content")
  embedding   Float[]
  metadata    Json?

  createdAt DateTime @default(now())

  @@unique([articleId, chunkIndex])
  @@index([articleId])
}

model ChatSession {
  id        String   @id @default(uuid())
  sessionId String   @unique
  ipAddress String?
  messages  Json     @default("[]")
  expiresAt DateTime @default(dbgenerated("NOW() + INTERVAL '24 hours'"))

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([sessionId])
  @@index([expiresAt])
}
```

### Step 2.3: Run Database Migrations

```bash
# Create migration
pnpm prisma migrate dev --name init

# Generate Prisma client
pnpm prisma generate

# Seed database (optional)
pnpm prisma db seed
```

### Step 2.4: Create Database Connection

Create `lib/prisma.ts`:
```typescript
import { PrismaClient } from '@prisma/client'

const globalForPrisma = global as unknown as { prisma: PrismaClient }

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

export default prisma
```

### Step 2.5: Create Article API Endpoints

Create `app/api/articles/route.ts`:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const articles = await prisma.article.findMany({
      where: { status: 'published' },
      orderBy: { publishedAt: 'desc' },
      include: { author: true }
    })

    return NextResponse.json(articles)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch articles' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const article = await prisma.article.create({
      data: {
        ...body,
        authorId: 'user-id', // Get from session
      }
    })

    // Trigger embedding generation (async)
    fetch(`${process.env.FASTAPI_URL}/api/embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_id: article.id })
    })

    return NextResponse.json(article)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create article' },
      { status: 500 }
    )
  }
}
```

## Phase 3: FastAPI AI Service

### Step 3.1: Initialize FastAPI Backend

```bash
cd ../backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
openai==1.3.0
langchain==0.0.350
numpy==1.24.3
pydantic==2.5.0
redis==5.0.1
asyncpg==0.29.0
sqlalchemy==2.0.23
pgvector==0.2.3
websockets==12.0
python-multipart==0.0.6
httpx==0.25.2
EOF

# Install dependencies
pip install -r requirements.txt
```

### Step 3.2: Create FastAPI Application

Create `app/main.py`:
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up FastAPI service...")
    yield
    # Shutdown
    print("Shutting down FastAPI service...")

app = FastAPI(
    title="Blog AI Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Assistant API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-ai"
    }
```

### Step 3.3: Create Embedding Service

Create `app/services/embeddings.py`:
```python
import openai
from typing import List
import numpy as np
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

class EmbeddingService:
    def __init__(self):
        self.model = "text-embedding-3-small"

    async def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a list of texts"""
        try:
            response = await openai.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [np.array(item.embedding) for item in response.data]
            return embeddings

        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for embedding"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks
```

### Step 3.4: Create Chat WebSocket Handler

Create `app/api/chat.py`:
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    session_id = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "query":
                # Process query and stream response
                await process_query(websocket, message["content"])

    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def process_query(websocket: WebSocket, query: str):
    """Process user query and stream response"""
    # This is a simplified version
    # In production, integrate with RAG pipeline

    # Send initial acknowledgment
    await websocket.send_json({
        "type": "status",
        "message": "Processing your query..."
    })

    # Simulate streaming response
    response = "This is a simulated response to your query about: " + query

    for char in response:
        await websocket.send_json({
            "type": "stream",
            "content": char,
            "finished": False
        })
        await asyncio.sleep(0.01)  # Simulate typing

    # Send completion
    await websocket.send_json({
        "type": "stream",
        "content": "",
        "finished": True
    })
```

### Step 3.5: Run FastAPI Service

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Phase 4: AI Assistant Integration

### Step 4.1: Create RAG Pipeline

Create `backend/app/services/rag.py`:
```python
from typing import List, Dict
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import PGVector
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

class RAGPipeline:
    def __init__(self, connection_string: str):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        self.vector_store = PGVector(
            connection_string=connection_string,
            embedding_function=self.embeddings,
            collection_name="article_embeddings"
        )

        self.llm = OpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            streaming=True
        )

    async def query(self, question: str, k: int = 5) -> str:
        """Query the RAG pipeline"""
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(question, k=k)

        # Build context
        context = "\n\n".join([doc.page_content for doc in docs])

        # Generate response
        prompt = f"""
        Based on the following context from blog articles, answer the question.
        If the answer is not in the context, say "I don't have information about that."

        Context:
        {context}

        Question: {question}

        Answer:
        """

        response = await self.llm.agenerate([prompt])
        return response.generations[0][0].text

    async def add_article(self, article_id: str, content: str):
        """Add article to vector store"""
        # Chunk the content
        chunks = self.chunk_text(content)

        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                "page_content": chunk,
                "metadata": {
                    "article_id": article_id,
                    "chunk_index": i
                }
            }
            documents.append(doc)

        # Add to vector store
        await self.vector_store.aadd_documents(documents)
```

### Step 4.2: Create Chat UI Component

Create `frontend/components/ChatWidget.tsx`:
```typescript
'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, X, MessageCircle } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (isOpen && !wsRef.current) {
      // Connect to WebSocket
      const ws = new WebSocket('ws://localhost:8000/ws/chat')

      ws.onopen = () => {
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'stream') {
          if (data.finished) {
            setIsStreaming(false)
          } else {
            setMessages(prev => {
              const last = prev[prev.length - 1]
              if (last?.role === 'assistant') {
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: last.content + data.content }
                ]
              }
              return [...prev, { role: 'assistant', content: data.content }]
            })
          }
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
      }

      wsRef.current = ws
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [isOpen])

  const sendMessage = () => {
    if (input.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
      const message = input.trim()
      setMessages(prev => [...prev, { role: 'user', content: message }])
      setInput('')
      setIsStreaming(true)

      wsRef.current.send(JSON.stringify({
        type: 'query',
        content: message
      }))
    }
  }

  return (
    <>
      {/* Chat button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 right-4 bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 transition-colors"
        >
          <MessageCircle size={24} />
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-xl flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="font-semibold">AI Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${
                  msg.role === 'user' ? 'text-right' : 'text-left'
                }`}
              >
                <div
                  className={`inline-block p-3 rounded-lg max-w-[80%] ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {isStreaming && (
              <div className="text-left">
                <div className="inline-block p-3 rounded-lg bg-gray-100">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about the articles..."
                className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                disabled={!isConnected || isStreaming}
              />
              <button
                onClick={sendMessage}
                disabled={!isConnected || isStreaming || !input.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={20} />
              </button>
            </div>
            {!isConnected && (
              <p className="text-xs text-red-500 mt-2">
                Connecting to AI assistant...
              </p>
            )}
          </div>
        </div>
      )}
    </>
  )
}
```

### Step 4.3: Integrate Chat Widget

Update `frontend/app/layout.tsx`:
```typescript
import ChatWidget from '@/components/ChatWidget'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {/* ... existing layout ... */}
        {children}
        <ChatWidget />
      </body>
    </html>
  )
}
```

## Phase 5: Production Deployment with Railway

### Step 5.1: Setup Railway Account and CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init
# Select "Empty Project"
# Name it: ai-blog-explorer
```

### Step 5.2: Configure Railway Services

```bash
# Link your GitHub repository
railway link

# Create services via Railway Dashboard or CLI
# Go to dashboard.railway.app and add:
# 1. PostgreSQL (from template)
# 2. Redis (from template)
# 3. Empty Service for Next.js (blog-frontend)
# 4. Empty Service for FastAPI (blog-api)
```

### Step 5.3: Configure Environment Variables

```bash
# Set shared project variables
railway variables set ENVIRONMENT=production
railway variables set INTERNAL_API_KEY=$(openssl rand -hex 32)
railway variables set NEXTAUTH_SECRET=$(openssl rand -hex 32)
railway variables set OPENAI_API_KEY=your-openai-key

# Configure service-specific variables for blog-frontend
railway service blog-frontend
railway variables set NEXT_PUBLIC_SITE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
railway variables set NEXT_PUBLIC_API_URL=https://${{blog-api.RAILWAY_PUBLIC_DOMAIN}}
railway variables set DATABASE_URL=${{blog-db.DATABASE_PRIVATE_URL}}
railway variables set REDIS_URL=${{blog-cache.REDIS_PRIVATE_URL}}

# Configure service-specific variables for blog-api
railway service blog-api
railway variables set DATABASE_URL=${{blog-db.DATABASE_PRIVATE_URL}}
railway variables set REDIS_URL=${{blog-cache.REDIS_PRIVATE_URL}}
```

### Step 5.4: Deploy Services

```bash
# Deploy frontend service
railway service blog-frontend
railway up

# Deploy API service
railway service blog-api
railway up

# Or deploy all services at once from root
railway up
```

### Step 5.5: Configure Custom Domains

```bash
# Add custom domain via Railway Dashboard
# 1. Go to Settings > Domains for each service
# 2. Add custom domain
# 3. Configure DNS with provided CNAME

# Or use Railway-provided domains
# Frontend: ai-blog-explorer.up.railway.app
# API: ai-blog-explorer-api.up.railway.app
```

### Step 5.6: Initialize Database

```bash
# Run migrations on Railway
railway run --service blog-frontend pnpm prisma migrate deploy

# Seed initial data (optional)
railway run --service blog-frontend pnpm prisma db seed
```

### Step 5.7: Verify Deployment

```bash
# Check service status
railway status

# View logs
railway logs --service blog-frontend
railway logs --service blog-api

# Test endpoints
curl https://your-app.railway.app/api/health
curl https://your-api.railway.app/health

# Open in browser
railway open
```

### Step 5.8: Setup Monitoring

Railway provides built-in monitoring, but you can add additional monitoring:

```bash
# View metrics in Railway Dashboard
# Metrics > Select Service

# Set up alerts (via Dashboard)
# Settings > Notifications > Add webhook/email

# Connect external monitoring (optional)
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d "api_key=YOUR_API_KEY" \
  -d "friendly_name=Blog Health" \
  -d "url=https://your-app.railway.app/api/health" \
  -d "type=1"
```

## Testing Strategy

### Unit Tests

Create `frontend/__tests__/api.test.ts`:
```typescript
import { GET } from '@/app/api/health/route'

describe('Health API', () => {
  it('should return healthy status', async () => {
    const response = await GET()
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.status).toBe('healthy')
  })
})
```

### Integration Tests

Create `backend/tests/test_chat.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_websocket_chat():
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({
            "type": "query",
            "content": "Hello"
        })
        data = websocket.receive_json()
        assert data["type"] in ["status", "stream"]
```

### End-to-End Tests

```bash
# Test full flow
npm run test:e2e

# Manual testing checklist
- [ ] Homepage loads
- [ ] Articles display correctly
- [ ] Admin can create/edit articles
- [ ] Chat widget connects
- [ ] AI responds to queries
- [ ] Rate limiting works
- [ ] Error handling works
```

## Cost Optimization

### Monitor Usage

```python
# backend/app/utils/cost_tracker.py
class CostTracker:
    def __init__(self):
        self.costs = {
            'openai_tokens': 0,
            'db_queries': 0,
            'cache_hits': 0
        }

    def track_openai_usage(self, tokens: int, model: str):
        """Track OpenAI API usage"""
        cost_per_1k = {
            'gpt-4o-mini': 0.00015,  # Input tokens
            'text-embedding-3-small': 0.00002
        }

        cost = (tokens / 1000) * cost_per_1k.get(model, 0)
        self.costs['openai_tokens'] += cost

    def get_monthly_estimate(self):
        """Estimate monthly costs"""
        return {
            'openai': self.costs['openai_tokens'] * 30,
            'railway_hosting': 25,  # Railway all services
            'total': self.costs['openai_tokens'] * 30 + 25
        }
```

### Optimization Tips

1. **Cache Aggressively**
   - Cache AI responses for similar queries
   - Cache embeddings to avoid regeneration
   - Use Redis for session management

2. **Optimize Token Usage**
   - Use GPT-4o-mini for most queries
   - Limit context window size
   - Implement smart chunking

3. **Database Optimization**
   - Add appropriate indexes
   - Use connection pooling
   - Implement query caching

4. **Rate Limiting**
   - Implement per-IP limits
   - Progressive pricing tiers
   - Graceful degradation

## Maintenance Guide

### Daily Tasks (Railway)

```bash
# Check service health
railway status
curl https://your-app.railway.app/api/health

# Check logs for errors
railway logs --service blog-frontend --filter ERROR
railway logs --service blog-api --filter ERROR

# Monitor resource usage (via Dashboard)
# dashboard.railway.app > Project > Metrics
```

### Weekly Tasks (Railway)

```bash
# Database backup (automatic, but can trigger manual)
railway run --service blog-db pg_dump -U postgres blogdb > backup-$(date +%Y%m%d).sql

# Update dependencies
railway run --service blog-frontend pnpm update
railway run --service blog-api pip install --upgrade -r requirements.txt

# Clean up old sessions
railway run --service blog-db psql -U postgres -d blogdb \
  -c "DELETE FROM chat_sessions WHERE expires_at < NOW()"

# Check Railway usage
railway usage
```

### Monthly Tasks (Railway)

```bash
# Review costs
# dashboard.railway.app > Project > Usage

# Update base images (rebuild services)
railway service blog-frontend
railway up --build

railway service blog-api
railway up --build

# Security updates
railway run --service blog-frontend npm audit fix
railway run --service blog-api pip-audit --fix

# Performance review
# dashboard.railway.app > Project > Metrics > Last 30 days
```

### Railway-Specific Maintenance

```bash
# Rollback to previous deployment if needed
railway rollback --service blog-frontend

# Scale services
# Via Dashboard: Settings > Replicas

# Environment variable updates
railway variables set KEY=value --service blog-frontend

# Database maintenance
railway connect blog-db
# Then run PostgreSQL commands

# Clear Redis cache
railway connect blog-cache
# Then run: FLUSHALL
```

### Troubleshooting

#### Common Issues and Solutions

1. **WebSocket Connection Failed**
```bash
# Check FastAPI service
docker-compose logs api
# Restart service
docker-compose restart api
```

2. **Database Connection Error**
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready
# Check connections
docker-compose exec postgres psql -U bloguser -d blogdb \
  -c "SELECT count(*) FROM pg_stat_activity"
```

3. **High Memory Usage**
```bash
# Identify memory-hungry service
docker stats
# Restart specific service
docker-compose restart [service_name]
# Clear caches
docker-compose exec redis redis-cli FLUSHALL
```

## Conclusion

This implementation guide provides a complete roadmap for building your AI-powered blog from scratch. Key milestones:

- ✅ **Phase 1**: Basic blog with Next.js
- ✅ **Phase 2**: Database and content management
- ✅ **Phase 3**: FastAPI AI service
- ✅ **Phase 4**: AI assistant integration
- ✅ **Phase 5**: Production deployment

### Next Steps

1. **Enhance Features**
   - Add image optimization pipeline
   - Implement newsletter system
   - Add comment system

2. **Improve AI**
   - Fine-tune prompts
   - Add more context sources
   - Implement feedback loop

3. **Scale Up**
   - Move to Kubernetes
   - Add CDN
   - Implement multi-region deployment

Remember to iterate based on user feedback and monitor costs closely to stay within budget!