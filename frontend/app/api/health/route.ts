import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET() {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'ai-blog-frontend',
    version: '0.1.0',
    checks: {
      database: 'unknown',
      redis: 'unknown',
      api: 'unknown'
    }
  }

  // Check database connection
  try {
    await prisma.$queryRaw`SELECT 1`
    health.checks.database = 'healthy'
  } catch (error) {
    health.checks.database = 'unhealthy'
    health.status = 'degraded'
  }

  // Check backend API (use internal Docker network URL)
  try {
    const apiUrl = process.env.NODE_ENV === 'production'
      ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
      : 'http://backend:8000'
    const response = await fetch(`${apiUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    })
    if (response.ok) {
      health.checks.api = 'healthy'
    } else {
      health.checks.api = 'unhealthy'
      health.status = 'degraded'
    }
  } catch (error) {
    health.checks.api = 'unhealthy'
    health.status = 'degraded'
  }

  const statusCode = health.status === 'healthy' ? 200 : 503

  return NextResponse.json(health, { status: statusCode })
}