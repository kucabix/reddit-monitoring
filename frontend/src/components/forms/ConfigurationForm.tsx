"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Settings, Loader2 } from "lucide-react";

export function ConfigurationForm() {
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
  const [initializationResult, setInitializationResult] = useState<any>(null);

  const handleInitialize = async () => {
    setIsInitializing(true);
    setInitializationResult(null);
    try {
      const response = await fetch("http://localhost:8000/api/initialize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setInitializationResult(result);
      console.log("Initialization result:", result);
    } catch (error) {
      console.error("Initialization error:", error);
      setInitializationResult({
        status: "error",
        message: `Failed to initialize services: ${error}`,
        services: {},
      });
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
        onClick={handleInitialize}
        disabled={isInitializing}
        className="w-full"
      >
        {isInitializing ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Initializing Services...
          </>
        ) : (
          <>
            <Settings className="mr-2 h-4 w-4" />
            Initialize Services
          </>
        )}
      </Button>

      {initializationResult && (
        <div className="mt-4 p-4 border rounded-lg">
          <h3 className="font-semibold mb-2">Initialization Results</h3>
          <div
            className={`p-2 rounded ${
              initializationResult.status === "success"
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : initializationResult.status === "warning"
                ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
            }`}
          >
            <strong>Status:</strong> {initializationResult.message}
          </div>

          {initializationResult.services && (
            <div className="mt-3 space-y-2">
              {Object.entries(initializationResult.services).map(
                ([service, result]: [string, any]) => (
                  <div
                    key={service}
                    className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-800 rounded"
                  >
                    <span className="font-medium capitalize">{service}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        result.status === "success"
                          ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                          : result.status === "warning"
                          ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                          : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                      }`}
                    >
                      {result.status}
                    </span>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
