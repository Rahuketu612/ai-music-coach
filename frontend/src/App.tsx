/**
 * AI Music Coach - Main App Component
 * 
 * Main application entry point with simple client-side routing.
 */

import React, { useState, useEffect } from "react";
import { Dashboard } from "./pages/Dashboard";
import { Practice } from "./pages/Practice";
import { Landing } from "./pages/Landing";
import { Onboarding } from "./pages/Onboarding";

type Page = "landing" | "onboarding" | "dashboard" | "practice";

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>("landing");

  useEffect(() => {
    // Simple client-side routing
    const path = window.location.pathname;
    if (path === "/dashboard" || path === "/app") {
      setCurrentPage("dashboard");
    } else if (path === "/practice") {
      setCurrentPage("practice");
    } else if (path === "/onboarding") {
      setCurrentPage("onboarding");
    } else {
      setCurrentPage("landing");
    }
  }, []);

  // Navigation bar component
  const Navigation = () => (
    <nav className="bg-white shadow-sm sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div 
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => window.location.href = "/"}
          >
            <span className="text-2xl">🎸</span>
            <span className="font-bold text-xl text-gray-900">AI Music Coach</span>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {currentPage !== "landing" && (
              <>
                <button
                  onClick={() => setCurrentPage("dashboard")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    currentPage === "dashboard"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setCurrentPage("practice")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    currentPage === "practice"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  Practice
                </button>
              </>
            )}
            {currentPage === "landing" && (
              <button
                onClick={() => setCurrentPage("onboarding")}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Get Started
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {currentPage !== "landing" && <Navigation />}
      
      {/* Page Content */}
      <main>
        {currentPage === "landing" && <Landing />}
        {currentPage === "onboarding" && <Onboarding />}
        {currentPage === "dashboard" && <Dashboard />}
        {currentPage === "practice" && <Practice />}
      </main>
    </div>
  );
};

export default App;