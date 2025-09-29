"use client";

import { useState } from "react";
import { ConfigurationForm } from "@/components/forms/ConfigurationForm";
import { SearchForm } from "@/components/forms/SearchForm";
import { ResultsTable } from "@/components/results/ResultsTable";
import { StatsCards } from "@/components/dashboard/StatsCards";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, BarChart3, Settings } from "lucide-react";

export default function Dashboard() {
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedPosts, setSelectedPosts] = useState<number[]>([]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center space-x-2">
            <Search className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-3xl font-bold">Reddit Agent MVP</h1>
              <p className="text-muted-foreground">
                Monitor Reddit for keywords, analyze with AI, and export results
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="search" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="search" className="flex items-center space-x-2">
              <Search className="h-4 w-4" />
              <span>Search</span>
            </TabsTrigger>
            <TabsTrigger
              value="results"
              className="flex items-center space-x-2"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Results</span>
            </TabsTrigger>
            <TabsTrigger value="config" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Configuration</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="search" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Search Configuration</CardTitle>
                  <CardDescription>
                    Configure your search parameters and business context
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <SearchForm
                    onSearch={setSearchResults}
                    isSearching={isSearching}
                    setIsSearching={setIsSearching}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Business Context</CardTitle>
                  <CardDescription>
                    Set up your business context for AI analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ConfigurationForm />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            {searchResults.length > 0 ? (
              <>
                <StatsCards
                  results={searchResults}
                  selectedPosts={selectedPosts}
                />
                <ResultsTable
                  results={searchResults}
                  selectedPosts={selectedPosts}
                  onSelectionChange={setSelectedPosts}
                />
              </>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Search className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Results Yet</h3>
                  <p className="text-muted-foreground text-center">
                    Configure your search parameters and run a search to see
                    results here.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="config" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Advanced Configuration</CardTitle>
                <CardDescription>
                  Configure API keys and advanced settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ConfigurationForm />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
