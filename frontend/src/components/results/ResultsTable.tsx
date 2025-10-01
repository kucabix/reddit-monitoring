"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  ExternalLink,
  MessageSquare,
  TrendingUp,
  Brain,
  Target,
  Lightbulb,
} from "lucide-react";

interface ResultsTableProps {
  results: any[];
  selectedPosts: number[];
  onSelectionChange: (selected: number[]) => void;
}

export function ResultsTable({
  results,
  selectedPosts,
  onSelectionChange,
}: ResultsTableProps) {
  const handleSelectAll = () => {
    if (selectedPosts.length === results.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(results.map((_, index) => index));
    }
  };

  const handleSelectPost = (index: number) => {
    if (selectedPosts.includes(index)) {
      onSelectionChange(selectedPosts.filter((i) => i !== index));
    } else {
      onSelectionChange([...selectedPosts, index]);
    }
  };

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
              {selectedPosts.length === results.length
                ? "Deselect All"
                : "Select All"}
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
                  className="w-5 h-5"
                />
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between">
                    <h3 className="font-semibold text-lg leading-tight">
                      {post.title}
                    </h3>
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
                      <a
                        href={post.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        View Post
                      </a>
                    </Button>
                  </div>

                  {/* AI Analysis Section */}
                  {post.relevance_score !== undefined && (
                    <Accordion type="single" collapsible className="w-full">
                      <AccordionItem value="analysis">
                        <AccordionTrigger className="text-sm font-medium">
                          <Brain className="h-4 w-4" />
                          <span>AI Analysis</span>
                          {post.relevance_score && (
                            <Badge
                              variant={
                                post.relevance_score >= 70
                                  ? "default"
                                  : post.relevance_score >= 40
                                  ? "secondary"
                                  : "outline"
                              }
                              className="text-xs"
                            >
                              {post.relevance_score}/100
                            </Badge>
                          )}
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-3 p-4 bg-muted/50 rounded-lg">
                            {post.relevance_score && (
                              <div className="flex items-center space-x-2">
                                <Target className="h-4 w-4 text-muted-foreground" />
                                <span className="text-sm font-medium">
                                  Relevance Score:
                                </span>
                                <span className="text-sm">
                                  {post.relevance_score}/100
                                </span>
                              </div>
                            )}

                            {post.content_type && (
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-medium">
                                  Content Type:
                                </span>
                                <Badge variant="outline" className="text-xs">
                                  {post.content_type}
                                </Badge>
                              </div>
                            )}

                            {post.target_audience_match && (
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-medium">
                                  Audience Match:
                                </span>
                                <span className="text-sm">
                                  {post.target_audience_match}/100
                                </span>
                              </div>
                            )}

                            {post.reasoning && (
                              <div>
                                <span className="text-sm font-medium">
                                  Reasoning:
                                </span>
                                <p className="text-sm text-muted-foreground mt-1">
                                  {post.reasoning}
                                </p>
                              </div>
                            )}

                            {post.business_opportunity && (
                              <div>
                                <div className="flex items-center space-x-2 mb-2">
                                  <Lightbulb className="h-4 w-4 text-yellow-500" />
                                  <span className="text-sm font-medium">
                                    Business Opportunity:
                                  </span>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                  {post.business_opportunity}
                                </p>
                              </div>
                            )}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
