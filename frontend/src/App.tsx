/**
 * AI Music Coach - Main App Component
 * 
 * Main application entry point with navigation.
 */

import React, { useState } from "react";
import { Dashboard } from "./pages/Dashboard";
import { Practice } from "./pages/Practice";

type Page = "dashboard" | "practice";

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <span className="text-2xl">🎸</span>
              <span className="font-bold text-xl text-gray-900">AI Music Coach</span>
            </div>

            {/* Navigation Links */}
            <div className="flex items-center gap-1">
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
            </div>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main>
        {currentPage === "dashboard" && <Dashboard />}
        {currentPage === "practice" && <Practice />}
      </main>
    </div>
  );
};

export default App;