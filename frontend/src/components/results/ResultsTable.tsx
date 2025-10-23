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
  FileText,
  Users,
  Loader2,
} from "lucide-react";

interface ResultsTableProps {
  results: any[];
  selectedPosts: number[];
  onSelectionChange: (selected: number[]) => void;
  businessContext?: {
    companyType: string;
    specialty: string;
    blogFocus: string;
    targetAudience: string;
    interests: string[];
  };
  onResultsUpdate?: (results: any[]) => void;
}

export function ResultsTable({
  results,
  selectedPosts,
  onSelectionChange,
  businessContext,
  onResultsUpdate,
}: ResultsTableProps) {
  const [analyzingPosts, setAnalyzingPosts] = useState<Set<number>>(new Set());
  const [expandedAccordions, setExpandedAccordions] = useState<Set<number>>(
    new Set()
  );

  // Sort posts: fresh posts first, then stale posts at the bottom
  const sortedResults = [...results].sort((a, b) => {
    if (a.is_stale && !b.is_stale) return 1;
    if (!a.is_stale && b.is_stale) return -1;
    return 0;
  });

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

  const handleAnalyzePost = async (postIndex: number) => {
    if (!businessContext) return;

    // Add to analyzing set
    setAnalyzingPosts((prev) => new Set(prev).add(postIndex));

    try {
      const postToAnalyze = results[postIndex];

      const analysisResponse = await fetch("/api/analysis/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          posts: [postToAnalyze],
          business_context: {
            company_type: businessContext.companyType,
            specialty: businessContext.specialty,
            blog_focus: businessContext.blogFocus,
            target_audience: businessContext.targetAudience,
            interests: businessContext.interests,
          },
          analysis_type: "detailed",
        }),
      });

      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        const analyzedPost = analysisData.analyzed_posts[0];

        // Update the results with analyzed data
        const updatedResults = [...results];
        updatedResults[postIndex] = analyzedPost;

        onResultsUpdate?.(updatedResults);

        // Expand the accordion for this post after successful analysis
        setExpandedAccordions((prev) => new Set(prev).add(postIndex));
      }
    } catch (error) {
      console.error("Analysis error:", error);
    } finally {
      // Remove from analyzing set
      setAnalyzingPosts((prev) => {
        const newSet = new Set(prev);
        newSet.delete(postIndex);
        return newSet;
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between flex-col sm:flex-row">
          <div>
            <CardTitle>Search Results</CardTitle>
            <CardDescription>
              {results.length} posts found • {selectedPosts.length} selected
            </CardDescription>
          </div>
          {/* <div className="flex space-x-2 mt-4 sm:mt-0">
            <Button variant="outline" onClick={handleSelectAll}>
              {selectedPosts.length === results.length
                ? "Deselect All"
                : "Select All"}
            </Button>
          </div> */}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedResults.map((post, index) => (
            <Card
              key={index}
              className={`p-3 sm:p-4 border-2 ${
                post.is_stale ? "opacity-60" : ""
              }`}
            >
              <div className="flex items-start space-x-2 sm:space-x-3">
                {/* <Checkbox
                  checked={selectedPosts.includes(index)}
                  onCheckedChange={() => handleSelectPost(index)}
                  className="w-4 h-4 sm:w-5 sm:h-5"
                /> */}
                <div className="flex-1 space-y-2">
                  {/* Title and Stats - Mobile Optimized */}
                  <div className="space-y-2">
                    <h3 className="font-semibold text-base sm:text-lg leading-tight break-all">
                      {post.title}
                    </h3>

                    {/* Stats Row */}
                    <div className="flex sm:items-center justify-between text-xs text-muted-foreground flex-col sm:flex-row gap-2">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-1">
                          <TrendingUp className="h-3 w-3" />
                          <span>{post.score}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageSquare className="h-3 w-3" />
                          <span>{post.num_comments}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge
                          variant="secondary"
                          className="text-xs px-1.5 py-0.5"
                        >
                          r/{post.subreddit}
                        </Badge>
                        {post.is_stale && (
                          <Badge
                            variant="outline"
                            className="text-xs px-1.5 py-0.5 text-muted-foreground"
                          >
                            stale
                          </Badge>
                        )}
                        <span className="text-xs">{post.created}</span>
                      </div>
                    </div>
                  </div>

                  {/* Content and Keywords - Mobile Layout */}
                  <div className="space-y-2">
                    {post.selftext && (
                      <p className="text-xs text-muted-foreground line-clamp-3 break-all">
                        {post.selftext}
                      </p>
                    )}

                    <div className="flex flex-wrap gap-1">
                      {post.keywords.map((keyword: string, i: number) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="text-xs px-1.5 py-0.5"
                        >
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <Button
                      variant="outline"
                      size="sm"
                      asChild
                      className="text-xs"
                    >
                      <a
                        href={post.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View Post
                      </a>
                    </Button>
                  </div>

                  {/* AI Analysis Section */}
                  {post.relevance_score !== undefined && (
                    <div className="space-y-2">
                      {/* Simple relevance display for non-analyzed posts */}
                      {!post.reasoning && !post.business_opportunity && (
                        <div className="flex items-center justify-between space-x-2 p-2 bg-muted/30 rounded-lg">
                          <div className="flex items-center space-x-2">
                            <Target className="h-3 w-3 text-blue-500" />
                            <span className="text-xs font-medium">
                              Relevance:
                            </span>
                            <Badge
                              variant={
                                post.relevance_score >= 70
                                  ? "default"
                                  : post.relevance_score >= 40
                                  ? "secondary"
                                  : "outline"
                              }
                              className="text-xs px-1.5 py-0.5"
                            >
                              {post.relevance_score}/100
                            </Badge>
                          </div>

                          {businessContext &&
                            !post.reasoning &&
                            !post.business_opportunity && (
                              <Button
                                variant="default"
                                size="sm"
                                onClick={() => handleAnalyzePost(index)}
                                disabled={analyzingPosts.has(index)}
                                className="text-xs"
                              >
                                {analyzingPosts.has(index) ? (
                                  <>
                                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                                    Analyzing...
                                  </>
                                ) : (
                                  <>
                                    <Brain className="h-3 w-3 mr-1" />
                                    Analyze
                                  </>
                                )}
                              </Button>
                            )}
                        </div>
                      )}

                      {/* Full analysis accordion for analyzed posts */}
                      {(post.reasoning || post.business_opportunity) && (
                        <Accordion
                          type="single"
                          collapsible
                          className="w-full"
                          value={
                            expandedAccordions.has(index) ? "analysis" : ""
                          }
                          onValueChange={(value) => {
                            if (value === "analysis") {
                              setExpandedAccordions((prev) =>
                                new Set(prev).add(index)
                              );
                            } else {
                              setExpandedAccordions((prev) => {
                                const newSet = new Set(prev);
                                newSet.delete(index);
                                return newSet;
                              });
                            }
                          }}
                        >
                          <AccordionItem value="analysis">
                            <AccordionTrigger className="text-xs sm:text-sm font-medium">
                              <Brain className="h-3 w-3 sm:h-4 sm:w-4" />
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
                                  className="text-xs px-1.5 py-0.5"
                                >
                                  {post.relevance_score}/100
                                </Badge>
                              )}
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="space-y-2 p-3 bg-muted/50 rounded-lg">
                                <div className="flex flex-col gap-2 text-xs">
                                  {post.relevance_score && (
                                    <div className="flex items-center space-x-1">
                                      <Target className="h-3 w-3 text-blue-500" />
                                      <span className="font-medium">
                                        Relevance:
                                      </span>
                                      <span>{post.relevance_score}/100</span>
                                    </div>
                                  )}

                                  {post.content_type && (
                                    <div className="flex items-center space-x-1">
                                      <FileText className="h-3 w-3 text-green-500" />
                                      <span className="font-medium">Type:</span>
                                      <Badge
                                        variant="outline"
                                        className="text-xs px-1.5 py-0.5"
                                      >
                                        {post.content_type}
                                      </Badge>
                                    </div>
                                  )}

                                  {post.target_audience_match && (
                                    <div className="flex items-center space-x-1">
                                      <Users className="h-3 w-3 text-purple-500" />
                                      <span className="font-medium">
                                        Audience:
                                      </span>
                                      <span>
                                        {post.target_audience_match}/100
                                      </span>
                                    </div>
                                  )}
                                </div>

                                {post.reasoning && (
                                  <div className="text-xs">
                                    <div className="flex items-center space-x-1 mb-1">
                                      <Brain className="h-3 w-3 text-orange-500" />
                                      <span className="font-medium">
                                        Reasoning:
                                      </span>
                                    </div>
                                    <p className="text-muted-foreground break-all">
                                      {post.reasoning}
                                    </p>
                                  </div>
                                )}

                                {post.business_opportunity && (
                                  <div className="text-xs">
                                    <div className="flex items-center space-x-1 mb-1">
                                      <Lightbulb className="h-3 w-3 text-yellow-500" />
                                      <span className="font-medium">
                                        Opportunity:
                                      </span>
                                    </div>
                                    <p className="text-muted-foreground break-all">
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
