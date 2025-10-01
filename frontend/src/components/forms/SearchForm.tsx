"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Search, Loader2, Plus, X } from "lucide-react";

interface SearchFormProps {
  onSearch: (results: any[]) => void;
  isSearching: boolean;
  setIsSearching: (searching: boolean) => void;
  keywords?: string[];
  subreddits?: string[];
  onKeywordsChange?: (keywords: string[]) => void;
  onSubredditsChange?: (subreddits: string[]) => void;
  businessContext?: {
    companyType: string;
    specialty: string;
    blogFocus: string;
    targetAudience: string;
    interests: string[];
  };
}

export function SearchForm({
  onSearch,
  isSearching,
  setIsSearching,
  keywords: externalKeywords,
  subreddits: externalSubreddits,
  onKeywordsChange,
  onSubredditsChange,
  businessContext,
}: SearchFormProps) {
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>(
    externalKeywords || []
  );
  const [selectedSubreddits, setSelectedSubreddits] = useState<string[]>(
    externalSubreddits || []
  );
  const [customKeyword, setCustomKeyword] = useState("");
  const [customSubreddit, setCustomSubreddit] = useState("");
  const [daysBack, setDaysBack] = useState(30);

  // Update local state when external props change
  React.useEffect(() => {
    if (externalKeywords !== undefined) {
      setSelectedKeywords(externalKeywords);
    }
  }, [externalKeywords]);

  React.useEffect(() => {
    if (externalSubreddits !== undefined) {
      setSelectedSubreddits(externalSubreddits);
    }
  }, [externalSubreddits]);

  const handleKeywordToggle = (keyword: string) => {
    const newKeywords = selectedKeywords.includes(keyword)
      ? selectedKeywords.filter((k) => k !== keyword)
      : [...selectedKeywords, keyword];
    setSelectedKeywords(newKeywords);
    onKeywordsChange?.(newKeywords);
  };

  const handleSubredditToggle = (subreddit: string) => {
    const newSubreddits = selectedSubreddits.includes(subreddit)
      ? selectedSubreddits.filter((s) => s !== subreddit)
      : [...selectedSubreddits, subreddit];
    setSelectedSubreddits(newSubreddits);
    onSubredditsChange?.(newSubreddits);
  };

  const addCustomKeyword = () => {
    if (
      customKeyword.trim() &&
      !selectedKeywords.includes(customKeyword.trim())
    ) {
      const newKeywords = [...selectedKeywords, customKeyword.trim()];
      setSelectedKeywords(newKeywords);
      onKeywordsChange?.(newKeywords);
      setCustomKeyword("");
    }
  };

  const addCustomSubreddit = () => {
    if (
      customSubreddit.trim() &&
      !selectedSubreddits.includes(customSubreddit.trim())
    ) {
      const newSubreddits = [...selectedSubreddits, customSubreddit.trim()];
      setSelectedSubreddits(newSubreddits);
      onSubredditsChange?.(newSubreddits);
      setCustomSubreddit("");
    }
  };

  const removeKeyword = (keyword: string) => {
    const newKeywords = selectedKeywords.filter((k) => k !== keyword);
    setSelectedKeywords(newKeywords);
    onKeywordsChange?.(newKeywords);
  };

  const removeSubreddit = (subreddit: string) => {
    const newSubreddits = selectedSubreddits.filter((s) => s !== subreddit);
    setSelectedSubreddits(newSubreddits);
    onSubredditsChange?.(newSubreddits);
  };

  const handleSearch = async () => {
    if (selectedKeywords.length === 0) return;

    setIsSearching(true);
    try {
      // First, search Reddit
      const searchResponse = await fetch("/api/reddit/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keywords: selectedKeywords,
          subreddits:
            selectedSubreddits.length > 0 ? selectedSubreddits : ["all"],
          days_back: daysBack,
        }),
      });

      if (!searchResponse.ok) {
        throw new Error("Search failed");
      }

      const searchData = await searchResponse.json();
      const posts = searchData.posts;

      // If we have business context, analyze the posts
      if (businessContext && posts.length > 0) {
        try {
          const analysisResponse = await fetch("/api/analysis/analyze", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              posts: posts,
              business_context: {
                company_type: businessContext.companyType,
                specialty: businessContext.specialty,
                blog_focus: businessContext.blogFocus,
                target_audience: businessContext.targetAudience,
                interests: businessContext.interests,
              },
            }),
          });

          if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json();
            onSearch(analysisData.analyzed_posts);
          } else {
            // If analysis fails, use original posts
            onSearch(posts);
          }
        } catch (analysisError) {
          console.error("Analysis error:", analysisError);
          // If analysis fails, use original posts
          onSearch(posts);
        }
      } else {
        // No business context or no posts, use original results
        onSearch(posts);
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Keywords</Label>
        <div className="space-y-2">
          {selectedKeywords.map((keyword) => (
            <div key={keyword} className="flex items-center space-x-2">
              <Checkbox
                id={`keyword-${keyword}`}
                checked={true}
                onCheckedChange={() => removeKeyword(keyword)}
              />
              <Label htmlFor={`keyword-${keyword}`} className="flex-1">
                {keyword}
              </Label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeKeyword(keyword)}
                className="h-6 w-6 p-0"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
          <div className="flex space-x-2">
            <Input
              placeholder="Add custom keyword"
              value={customKeyword}
              onChange={(e) => setCustomKeyword(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addCustomKeyword()}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addCustomKeyword}
              disabled={!customKeyword.trim()}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Subreddits</Label>
        <div className="space-y-2">
          {selectedSubreddits.map((subreddit) => (
            <div key={subreddit} className="flex items-center space-x-2">
              <Checkbox
                id={`subreddit-${subreddit}`}
                checked={true}
                onCheckedChange={() => removeSubreddit(subreddit)}
              />
              <Label htmlFor={`subreddit-${subreddit}`} className="flex-1">
                {subreddit}
              </Label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeSubreddit(subreddit)}
                className="h-6 w-6 p-0"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
          <div className="flex space-x-2">
            <Input
              placeholder="Add custom subreddit"
              value={customSubreddit}
              onChange={(e) => setCustomSubreddit(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addCustomSubreddit()}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addCustomSubreddit}
              disabled={!customSubreddit.trim()}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="days">Days to search back: {daysBack}</Label>
        <input
          id="days"
          type="range"
          min="1"
          max="90"
          value={daysBack}
          onChange={(e) => setDaysBack(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
        />
      </div>

      <Button
        onClick={handleSearch}
        disabled={isSearching || selectedKeywords.length === 0}
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
  );
}
