import { Database, Globe, Cpu, Zap } from 'lucide-react'

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Hello World! 👋
        </h1>
        <p className="text-xl text-gray-600">
          Welcome to the AI-Powered Blog Platform
        </p>
        <p className="text-sm text-gray-500 mt-2">
          All systems operational • Railway-ready deployment
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ServiceCard
          icon={<Globe className="h-8 w-8" />}
          title="Next.js Frontend"
          status="Running"
          description="React-based UI with SSR"
          endpoint="http://localhost:3000"
        />

        <ServiceCard
          icon={<Cpu className="h-8 w-8" />}
          title="FastAPI Backend"
          status="Running"
          description="Python API with WebSocket"
          endpoint="http://localhost:8000"
        />

        <ServiceCard
          icon={<Database className="h-8 w-8" />}
          title="PostgreSQL"
          status="Running"
          description="Database with pgvector"
          endpoint="localhost:5432"
        />

        <ServiceCard
          icon={<Zap className="h-8 w-8" />}
          title="Redis Cache"
          status="Running"
          description="In-memory data store"
          endpoint="localhost:6379"
        />
      </div>

      <div className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-2">Quick Start</h2>
        <ol className="list-decimal list-inside space-y-1 text-gray-700">
          <li>All services are containerized and ready</li>
          <li>Database migrations will run automatically</li>
          <li>WebSocket support is enabled</li>
          <li>AI features can be enabled with OpenAI API key</li>
        </ol>
      </div>

      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-2">Test Endpoints</h2>
        <ul className="space-y-2 font-mono text-sm">
          <li>
            <span className="text-gray-600">Health Check:</span>{' '}
            <a href="/api/health" className="text-blue-600 hover:underline">
              /api/health
            </a>
          </li>
          <li>
            <span className="text-gray-600">FastAPI Docs:</span>{' '}
            <a href="http://localhost:8000/docs" className="text-blue-600 hover:underline" target="_blank">
              http://localhost:8000/docs
            </a>
          </li>
        </ul>
      </div>
    </div>
  )
}

function ServiceCard({
  icon,
  title,
  status,
  description,
  endpoint
}: {
  icon: React.ReactNode
  title: string
  status: string
  description: string
  endpoint: string
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="text-blue-600">{icon}</div>
        <span className="text-xs font-semibold text-green-600 bg-green-100 px-2 py-1 rounded">
          {status}
        </span>
      </div>
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600 mb-2">{description}</p>
      <p className="text-xs font-mono text-gray-500">{endpoint}</p>
    </div>
  )
}