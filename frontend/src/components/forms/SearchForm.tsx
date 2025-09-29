'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Search, Loader2 } from 'lucide-react'

interface SearchFormProps {
  onSearch: (results: any[]) => void
  isSearching: boolean
  setIsSearching: (searching: boolean) => void
}

export function SearchForm({ onSearch, isSearching, setIsSearching }: SearchFormProps) {
  const [keywords, setKeywords] = useState('')
  const [subreddits, setSubreddits] = useState('all')
  const [daysBack, setDaysBack] = useState(30)

  const handleSearch = async () => {
    if (!keywords.trim()) return

    setIsSearching(true)
    try {
      const keywordsList = keywords.split(',').map(k => k.trim()).filter(k => k)
      const subredditsList = subreddits.split(',').map(s => s.trim()).filter(s => s)

      const response = await fetch('/api/reddit/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: keywordsList,
          subreddits: subredditsList,
          days_back: daysBack
        }),
      })

      if (!response.ok) {
        throw new Error('Search failed')
      }

      const data = await response.json()
      onSearch(data.posts)
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="keywords">Keywords</Label>
        <Input
          id="keywords"
          placeholder="Enter keywords (comma-separated)"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="subreddits">Subreddits</Label>
        <Input
          id="subreddits"
          placeholder="all, programming, datascience"
          value={subreddits}
          onChange={(e) => setSubreddits(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="days">Days to search back</Label>
        <Input
          id="days"
          type="number"
          min="1"
          max="90"
          value={daysBack}
          onChange={(e) => setDaysBack(Number(e.target.value))}
        />
      </div>

      <Button 
        onClick={handleSearch} 
        disabled={isSearching || !keywords.trim()}
        className="w-full"
      >
        {isSearching ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Searching...
          </>
        ) : (
          <>
            <Search className="mr-2 h-4 w-4" />
            Start Search
          </>
        )}
      </Button>
    </div>
  )
}
