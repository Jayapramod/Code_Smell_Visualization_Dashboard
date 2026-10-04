import React, { useState } from "react";
import "./App.css";

const initialMetrics = {
  totalFiles: 142,
  loc: 28491,
  totalSmells: 37,
  avgComplexity: 4.7,
  maxComplexity: 18,
  filesWithSmells: 24,
  functionsAnalyzed: 638,
  classesAnalyzed: 87,
};

const smellData = [
  {
    file: "src/services/UserService.js",
    type: "Long Function",
    severity: "High",
    line: 42,
    metric: "86 lines",
  },
  {
    file: "src/controllers/AuthController.js",
    type: "High Complexity",
    severity: "High",
    line: 78,
    metric: "Complexity: 18",
  },
  {
    file: "src/components/Dashboard.jsx",
    type: "Deep Nesting",
    severity: "Medium",
    line: 124,
    metric: "Depth: 6",
  },
  {
    file: "src/utils/parser.js",
    type: "Too Many Parameters",
    severity: "Medium",
    line: 31,
    metric: "7 parameters",
  },
  {
    file: "src/api/client.js",
    type: "TODO/FIXME",
    severity: "Low",
    line: 91,
    metric: "TODO",
  },
  {
    file: "src/modules/report.js",
    type: "Long File",
    severity: "Medium",
    line: 1,
    metric: "1,284 lines",
  },
];

const complexityData = [
  {
    file: "src/controllers/AuthController.js",
    function: "authenticateUser",
    complexity: 18,
    timeComplexity: "O(n)",
  },
  {
    file: "src/services/UserService.js",
    function: "getUsers",
    complexity: 12,
    timeComplexity: "O(n log n)",
  },
  {
    file: "src/utils/parser.js",
    function: "parseData",
    complexity: 9,
    timeComplexity: "O(n)",
  },
  {
    file: "src/api/client.js",
    function: "request",
    complexity: 6,
    timeComplexity: "O(1)",
  },
];

function MetricCard({ title, value, icon }) {
  return (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>

      <div>
        <p className="metric-title">{title}</p>
        <h2>{value}</h2>
      </div>
    </div>
  );
}

function SeverityBadge({ severity }) {
  return (
    <span className={`severity ${severity.toLowerCase()}`}>
      {severity}
    </span>
  );
}

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);

  const handleAnalyze = () => {
    if (!repoUrl.trim()) {
      alert("Please enter a repository URL.");
      return;
    }

    setLoading(true);
    setAnalyzed(false);

    // Mock API call
    setTimeout(() => {
      setLoading(false);
      setAnalyzed(true);
    }, 1500);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-logo">&lt;/&gt;</div>

          <div>
            <h1>CodeLens</h1>
            <p>Repository Code Analyzer</p>
          </div>
        </div>

        <div className="header-status">
          <span className="status-dot"></span>
          Analyzer Online
        </div>
      </header>

      <main className="container">
        {/* Hero */}
        <section className="hero">
          <div>
            <span className="eyebrow">CODE QUALITY ANALYZER</span>

            <h1>
              Understand your
              <span> codebase.</span>
            </h1>

            <p>
              Analyze your repository for code smells, complexity,
              maintainability and other important engineering metrics.
            </p>
          </div>
        </section>

        {/* Repository Input */}
        <section className="repo-section">
          <div className="repo-input-wrapper">
            <div className="input-icon">⌘</div>

            <input
              type="text"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
            />

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze Repository"}
            </button>
          </div>

          <div className="input-hint">
            Enter a public GitHub repository URL to start analysis.
          </div>
        </section>

        {/* Loading */}
        {loading && (
          <div className="loading-card">
            <div className="spinner"></div>

            <div>
              <strong>Analyzing repository...</strong>
              <p>
                Scanning files, functions, complexity and code smells.
              </p>
            </div>
          </div>
        )}

        {/* Dashboard */}
        {analyzed && !loading && (
          <>
            {/* Repository Info */}
            <section className="repo-info">
              <div>
                <span className="section-label">ANALYZED REPOSITORY</span>

                <h2>
                  {repoUrl.replace("https://github.com/", "")}
                </h2>
              </div>

              <span className="analyzed-badge">
                ✓ Analysis Complete
              </span>
            </section>

            {/* Metrics */}
            <section>
              <div className="section-heading">
                <div>
                  <span className="section-label">OVERVIEW</span>
                  <h2>Repository Metrics</h2>
                </div>

                <span className="metric-count">8 metrics</span>
              </div>

              <div className="metrics-grid">
                <MetricCard
                  title="Total Files"
                  value={initialMetrics.totalFiles}
                  icon="📁"
                />

                <MetricCard
                  title="Lines of Code"
                  value={initialMetrics.loc.toLocaleString()}
                  icon="⌘"
                />

                <MetricCard
                  title="Total Code Smells"
                  value={initialMetrics.totalSmells}
                  icon="⚠"
                />

                <MetricCard
                  title="Avg. Cyclomatic Complexity"
                  value={initialMetrics.avgComplexity}
                  icon="◎"
                />

                <MetricCard
                  title="Maximum Complexity"
                  value={initialMetrics.maxComplexity}
                  icon="↗"
                />

                <MetricCard
                  title="Files with Smells"
                  value={initialMetrics.filesWithSmells}
                  icon="📄"
                />

                <MetricCard
                  title="Functions Analyzed"
                  value={initialMetrics.functionsAnalyzed}
                  icon="ƒ"
                />

                <MetricCard
                  title="Classes Analyzed"
                  value={initialMetrics.classesAnalyzed}
                  icon="C"
                />
              </div>
            </section>

            {/* Summary */}
            <section className="summary-card">
              <div className="summary-icon">✦</div>

              <div>
                <span className="section-label">ANALYSIS SUMMARY</span>

                <h2>Good foundation, but some refactoring is recommended.</h2>

                <p>
                  The repository contains{" "}
                  <strong>{initialMetrics.totalFiles} files</strong>{" "}
                  with approximately{" "}
                  <strong>
                    {initialMetrics.loc.toLocaleString()} lines
                  </strong>{" "}
                  of code. We detected{" "}
                  <strong>{initialMetrics.totalSmells} code smells</strong>{" "}
                  across{" "}
                  <strong>{initialMetrics.filesWithSmells} files</strong>.
                </p>

                <p>
                  The average cyclomatic complexity is{" "}
                  <strong>{initialMetrics.avgComplexity}</strong>, while the
                  most complex function has a complexity of{" "}
                  <strong>{initialMetrics.maxComplexity}</strong>.
                  Consider prioritizing high-complexity functions and long
                  functions for refactoring.
                </p>
              </div>
            </section>

            {/* Code Smells */}
            <section className="smells-section">
              <div className="section-heading">
                <div>
                  <span className="section-label">QUALITY</span>
                  <h2>Code Smells</h2>
                </div>

                <span className="danger-count">
                  {initialMetrics.totalSmells} detected
                </span>
              </div>

              <div className="smell-types">
                <div className="smell-type">
                  <span>Long Function</span>
                  <strong>8</strong>
                </div>

                <div className="smell-type">
                  <span>Long File</span>
                  <strong>5</strong>
                </div>

                <div className="smell-type">
                  <span>Too Many Parameters</span>
                  <strong>7</strong>
                </div>

                <div className="smell-type">
                  <span>High Complexity</span>
                  <strong>9</strong>
                </div>

                <div className="smell-type">
                  <span>Deep Nesting</span>
                  <strong>5</strong>
                </div>

                <div className="smell-type">
                  <span>TODO/FIXME</span>
                  <strong>3</strong>
                </div>
              </div>
            </section>

            {/* Smell Details */}
            <section className="table-section">
              <div className="section-heading">
                <div>
                  <span className="section-label">DETAILED FINDINGS</span>
                  <h2>Smell Details</h2>
                </div>

                <span className="table-count">
                  {smellData.length} shown
                </span>
              </div>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>File</th>
                      <th>Smell Type</th>
                      <th>Severity</th>
                      <th>Line</th>
                      <th>Metric / Value</th>
                    </tr>
                  </thead>

                  <tbody>
                    {smellData.map((smell, index) => (
                      <tr key={index}>
                        <td className="file-name">{smell.file}</td>

                        <td>{smell.type}</td>

                        <td>
                          <SeverityBadge severity={smell.severity} />
                        </td>

                        <td>
                          <span className="line-number">
                            {smell.line}
                          </span>
                        </td>

                        <td className="metric-value">
                          {smell.metric}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Complexity */}
            <section className="table-section">
              <div className="section-heading">
                <div>
                  <span className="section-label">PERFORMANCE</span>
                  <h2>Complexity Analysis</h2>
                </div>
              </div>

              <div className="complexity-grid">
                <div className="complexity-card">
                  <span>Average Complexity</span>
                  <strong>{initialMetrics.avgComplexity}</strong>
                  <small>Cyclomatic complexity</small>
                </div>

                <div className="complexity-card">
                  <span>Maximum Complexity</span>
                  <strong>{initialMetrics.maxComplexity}</strong>
                  <small>Highest function complexity</small>
                </div>
              </div>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>File</th>
                      <th>Function</th>
                      <th>Cyclomatic Complexity</th>
                      <th>Time Complexity</th>
                    </tr>
                  </thead>

                  <tbody>
                    {complexityData.map((item, index) => (
                      <tr key={index}>
                        <td className="file-name">{item.file}</td>

                        <td className="function-name">
                          {item.function}()
                        </td>

                        <td>
                          <span
                            className={
                              item.complexity >= 15
                                ? "complexity high"
                                : item.complexity >= 10
                                ? "complexity medium"
                                : "complexity low"
                            }
                          >
                            {item.complexity}
                          </span>
                        </td>

                        <td>
                          <code className="big-o">
                            {item.timeComplexity}
                          </code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Footer */}
            <footer>
              <span>CodeLens</span>
              <span>Repository analysis dashboard</span>
            </footer>
          </>
        )}

        {!analyzed && !loading && (
          <div className="empty-state">
            <div className="empty-icon">{`{ }`}</div>

            <h2>Ready to analyze your repository</h2>

            <p>
              Enter a repository URL above and click{" "}
              <strong>Analyze Repository</strong>.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

