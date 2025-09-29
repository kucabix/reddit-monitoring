'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BarChart3, Users, TrendingUp, Target } from 'lucide-react'

interface StatsCardsProps {
  results: any[]
  selectedPosts: number[]
}

export function StatsCards({ results, selectedPosts }: StatsCardsProps) {
  const totalPosts = results.length
  const selectedCount = selectedPosts.length
  const uniqueSubreddits = new Set(results.map(r => r.subreddit)).size
  const avgScore = results.length > 0 ? Math.round(results.reduce((sum, r) => sum + r.score, 0) / results.length) : 0
  
  // Calculate AI analysis metrics if available
  const analyzedPosts = results.filter(r => r.relevance_score !== undefined)
  const highRelevancePosts = analyzedPosts.filter(r => r.relevance_score >= 70)
  const avgRelevance = analyzedPosts.length > 0 
    ? Math.round(analyzedPosts.reduce((sum, r) => sum + r.relevance_score, 0) / analyzedPosts.length)
    : 0

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Posts</CardTitle>
          <BarChart3 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalPosts}</div>
          <p className="text-xs text-muted-foreground">
            Posts found in search
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Selected</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{selectedCount}</div>
          <p className="text-xs text-muted-foreground">
            Posts selected for export
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Subreddits</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{uniqueSubreddits}</div>
          <p className="text-xs text-muted-foreground">
            Unique subreddits
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Score</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{avgScore}</div>
          <p className="text-xs text-muted-foreground">
            Average Reddit score
          </p>
        </CardContent>
      </Card>

      {analyzedPosts.length > 0 && (
        <>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Relevance</CardTitle>
              <Badge variant="secondary">AI</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{highRelevancePosts.length}</div>
              <p className="text-xs text-muted-foreground">
                Posts with 70+ relevance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Relevance</CardTitle>
              <Badge variant="secondary">AI</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{avgRelevance}/100</div>
              <p className="text-xs text-muted-foreground">
                Average AI relevance score
              </p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
