'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { ExternalLink, MessageSquare, TrendingUp } from 'lucide-react'

interface ResultsTableProps {
  results: any[]
  selectedPosts: number[]
  onSelectionChange: (selected: number[]) => void
}

export function ResultsTable({ results, selectedPosts, onSelectionChange }: ResultsTableProps) {
  const handleSelectAll = () => {
    if (selectedPosts.length === results.length) {
      onSelectionChange([])
    } else {
      onSelectionChange(results.map((_, index) => index))
    }
  }

  const handleSelectPost = (index: number) => {
    if (selectedPosts.includes(index)) {
      onSelectionChange(selectedPosts.filter(i => i !== index))
    } else {
      onSelectionChange([...selectedPosts, index])
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Search Results</CardTitle>
            <CardDescription>
              {results.length} posts found • {selectedPosts.length} selected
            </CardDescription>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleSelectAll}>
              {selectedPosts.length === results.length ? 'Deselect All' : 'Select All'}
            </Button>
            <Button disabled={selectedPosts.length === 0}>
              Export Selected ({selectedPosts.length})
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {results.map((post, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-start space-x-3">
                <Checkbox
                  checked={selectedPosts.includes(index)}
                  onCheckedChange={() => handleSelectPost(index)}
                />
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between">
                    <h3 className="font-semibold text-lg leading-tight">{post.title}</h3>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="h-4 w-4" />
                        <span>{post.score}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>{post.num_comments}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <Badge variant="secondary">r/{post.subreddit}</Badge>
                    <span>{post.created}</span>
                  </div>
                  
                  {post.selftext && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {post.selftext}
                    </p>
                  )}
                  
                  <div className="flex flex-wrap gap-1">
                    {post.keywords.map((keyword: string, i: number) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" asChild>
                      <a href={post.url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-1" />
                        View Post
                      </a>
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
