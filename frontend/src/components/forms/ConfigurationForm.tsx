"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Search, Loader2 } from "lucide-react";

interface ConfigurationFormProps {
  onKeywordsGenerated?: (keywords: string[]) => void;
  onSubredditsGenerated?: (subreddits: string[]) => void;
  onBusinessContextGenerated?: (context: {
    companyType: string;
    specialty: string;
    blogFocus: string;
    targetAudience: string;
    interests: string[];
  }) => void;
}

export function ConfigurationForm({
  onKeywordsGenerated,
  onSubredditsGenerated,
  onBusinessContextGenerated,
}: ConfigurationFormProps) {
  const [companyType, setCompanyType] = useState("software house");
  const [specialty, setSpecialty] = useState("data visualization");
  const [blogFocus, setBlogFocus] = useState("data visualization topics");
  const [targetAudience, setTargetAudience] = useState(
    "data professionals, analysts, developers"
  );
  const [interests, setInterests] =
    useState(`data visualization tools and techniques
business intelligence
dashboard design
data storytelling
analytics platforms
data science workflows
visualization libraries (D3.js, Plotly, etc.)
business data challenges
data-driven decision making
interactive dashboards
data visualization best practices
BI tools and platforms`);
  const [isInitializing, setIsInitializing] = useState(false);

  const handleFeedSearch = async () => {
    setIsInitializing(true);
    try {
      const response = await fetch("/api/initialize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Services initialized:", result);

      // Update keywords based on the form data
      const keywords = [
        companyType,
        specialty,
        blogFocus,
        targetAudience,
        ...interests.split("\n").filter((interest) => interest.trim()),
      ].filter((keyword) => keyword.trim());

      console.log("Updated keywords:", keywords);

      // Update the search form inputs
      onKeywordsGenerated?.(keywords);

      // Generate relevant subreddits based on the business context
      const relevantSubreddits = [
        "datascience",
        "MachineLearning",
        "programming",
        "businessintelligence",
        "analytics",
        "dataisbeautiful",
        "visualization",
      ];

      onSubredditsGenerated?.(relevantSubreddits);

      // Pass business context for AI analysis
      onBusinessContextGenerated?.({
        companyType,
        specialty,
        blogFocus,
        targetAudience,
        interests: interests.split("\n").filter((interest) => interest.trim()),
      });
    } catch (error) {
      console.error("Feed search error:", error);
    } finally {
      setIsInitializing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="company-type">Company Type</Label>
          <Input
            id="company-type"
            value={companyType}
            onChange={(e) => setCompanyType(e.target.value)}
            placeholder="e.g., software house, e-commerce platform"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="specialty">Specialty</Label>
          <Input
            id="specialty"
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            placeholder="Company's main specialty"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="blog-focus">Blog Focus</Label>
          <Input
            id="blog-focus"
            value={blogFocus}
            onChange={(e) => setBlogFocus(e.target.value)}
            placeholder="Main topics for blog content"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="target-audience">Target Audience</Label>
          <Input
            id="target-audience"
            value={targetAudience}
            onChange={(e) => setTargetAudience(e.target.value)}
            placeholder="Primary target audience"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="interests">Interests</Label>
          <Textarea
            id="interests"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            placeholder="Company interests (one per line)"
            rows={6}
          />
        </div>
      </div>

      <Button
        onClick={handleFeedSearch}
        disabled={isInitializing}
        className="w-full"
      >
        {isInitializing ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Searching Feed...
          </>
        ) : (
          <>
            <Search className="mr-2 h-4 w-4" />
            Feed Search
          </>
        )}
      </Button>
    </div>
  );
}
