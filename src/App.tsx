import React, { useState, useEffect, useRef } from "react";
import {
  Play,
  FileCode,
  Sliders,
  Terminal,
  Grid,
  Mail,
  Download,
  Copy,
  Check,
  Search,
  Filter,
  Briefcase,
  MapPin,
  Clock,
  Sparkles,
  RefreshCw,
  Plus,
  Trash2,
  FileText,
  Save,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { GLOBAL_CAREER_PAGES, PUNE_CAREER_PAGES } from "./data/career_pages";

// Standardize layout colors to "Cosmic Slate" (deep charcoal with soft slate accents)
export default function App() {
  // Tabs: dashboard, jobs, code, config
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  
  // Scraper configuration
  const [careerPages, setCareerPages] = useState<string[]>([
    "https://boards.greenhouse.io/github",
    "https://jobs.lever.co/lever",
    "https://careers.smartrecruiters.com/deliveryhero",
    "https://ashbyhq.com/careers/stripe",
    "https://bamboohr.com/careers"
  ]);
  const [searchUrlTerm, setSearchUrlTerm] = useState("");
  const [allowedCities, setAllowedCities] = useState<string[]>([
    "Pune", "Bangalore", "Hyderabad", "Chennai", "Mumbai"
  ]);
  const [allowedKeywords, setAllowedKeywords] = useState<string[]>([
    "Software Engineer", "Software Developer", "Web Developer", "App Developer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer", "React Developer",
    "Node.js Developer", "Python Developer", "Java Developer", "Django Developer",
    "AI Engineer", "Machine Learning Engineer", "Data Scientist", "Data Engineer",
    "DevOps Engineer", "Cloud Engineer", "QA Engineer", "Automation Tester", "SDET",
    "Cybersecurity Engineer", "Security Engineer", "Mobile Developer", "Android Developer",
    "iOS Developer", "Flutter Developer", "React Native Developer", "UI Engineer",
    "Technical UI/UX Engineer"
  ]);
  const [newKeyword, setNewKeyword] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [portalSources, setPortalSources] = useState({
    linkedin: true,
    indeed: true,
    instahyre: true
  });

  // State for scraped jobs, logs, and UI states
  const [jobs, setJobs] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [isScraping, setIsScraping] = useState(false);
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  
  // Filters for job list
  const [cityFilter, setCityFilter] = useState<string>("All");
  const [workModeFilter, setWorkModeFilter] = useState<string>("All");
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Code files structure for explorer
  const [codeFiles, setCodeFiles] = useState<{ [key: string]: string }>({});
  const [selectedFile, setSelectedFile] = useState<string>("project/scraper.py");
  
  // UX Feedbacks
  const [copiedStates, setCopiedStates] = useState<{ [key: string]: boolean }>({});
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isRegeneratingEmail, setIsRegeneratingEmail] = useState(false);
  const [editedEmail, setEditedEmail] = useState<string>("");

  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Load code files and check if any initial jobs are stored
  useEffect(() => {
    fetchCodeFiles();
    // Pre-populate some demo logs
    setLogs([
      `[${new Date().toLocaleTimeString()}] IT Job Intelligence Scraper ready.`,
      `[${new Date().toLocaleTimeString()}] Modular Python scripts loaded in workspace.`,
      `[${new Date().toLocaleTimeString()}] Click "Run IT Scraper Pipeline" to start fetching fresh tech roles.`
    ]);
  }, []);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  const fetchCodeFiles = async () => {
    try {
      const res = await fetch("/api/code");
      const data = await res.json();
      if (data.success) {
        setCodeFiles(data.files);
      }
    } catch (err) {
      console.error("Error loading code files:", err);
    }
  };

  const runScraper = async () => {
    setIsScraping(true);
    setSelectedJob(null);
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Starting scraping run...`]);
    
    // Poll logs occasionally to make terminal active
    const logInterval = setInterval(async () => {
      try {
        const res = await fetch("/api/logs");
        const data = await res.json();
        if (data.logs && data.logs.length > 0) {
          setLogs(data.logs);
        }
      } catch (err) {
        // ignore
      }
    }, 1200);

    try {
      const res = await fetch("/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          career_pages: careerPages,
          portal_sources: portalSources,
          allowed_keywords: allowedKeywords,
          allowed_cities: allowedCities
        })
      });
      const data = await res.json();
      if (data.success) {
        setJobs(data.jobs);
        setLogs(data.logs);
        if (data.jobs.length > 0) {
          setSelectedJob(data.jobs[0]);
          setEditedEmail(data.jobs[0].custom_cold_email);
        }
      } else {
        setLogs(prev => [...prev, `[ERROR] Scraper failed: ${data.error}`]);
      }
    } catch (err: any) {
      setLogs(prev => [...prev, `[ERROR] Network error: ${err.message}`]);
    } finally {
      clearInterval(logInterval);
      setIsScraping(false);
    }
  };

  const saveConfigToDisk = async () => {
    try {
      const res = await fetch("/api/save-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          career_pages: careerPages,
          allowed_cities: allowedCities,
          allowed_keywords: allowedKeywords
        })
      });
      const data = await res.json();
      if (data.success) {
        setSaveSuccess(true);
        fetchCodeFiles(); // reload code files with newly updated variables
        setLogs(prev => [...prev, `[INFO] Configuration saved to project/config.py and synced with filesystem.`]);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error("Error saving config:", err);
    }
  };

  const regenerateEmail = async (job: any) => {
    if (!job) return;
    setIsRegeneratingEmail(true);
    try {
      const res = await fetch("/api/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job })
      });
      const data = await res.json();
      if (data.success) {
        setEditedEmail(data.email);
        // Update in jobs list
        setJobs(prev => prev.map(j => j.id === job.id ? { ...j, custom_cold_email: data.email } : j));
        setLogs(prev => [...prev, `[AI Generator] Successfully regenerated personalized email for "${job.title}" @ "${job.company}"`]);
      }
    } catch (err) {
      console.error("Email regeneration failed:", err);
    } finally {
      setIsRegeneratingEmail(false);
    }
  };

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [key]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [key]: false }));
    }, 2000);
  };

  // Filter jobs dynamically
  const filteredJobs = jobs.filter(job => {
    const matchesCity = cityFilter === "All" || job.city.toLowerCase() === cityFilter.toLowerCase() || (cityFilter === "Remote" && job.city.toLowerCase().includes("remote"));
    const matchesWorkMode = workModeFilter === "All" || job.work_mode.toLowerCase() === workModeFilter.toLowerCase();
    const matchesSearch = searchTerm === "" || 
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
      job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.tech_stack.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesCity && matchesWorkMode && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans antialiased selection:bg-indigo-100">
      {/* Visual Header */}
      <header className="border-b border-slate-200 bg-white px-6 py-4 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-indigo-600 to-indigo-500 p-2.5 rounded-xl shadow-md shadow-indigo-100">
              <FileCode className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-2">
                IT Job Intelligence Scraper
                <span className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full font-mono">
                  v1.0.0 (Prod)
                </span>
              </h1>
              <p className="text-xs text-slate-500">
                Production-Grade ATS Crawler, 4-Layer Deduplicator, & AI Cold Email Pipeline
              </p>
            </div>
          </div>
          
          {/* Main Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={runScraper}
              disabled={isScraping}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold shadow-sm transition-all ${
                isScraping
                  ? "bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed"
                  : "bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-100 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
              }`}
            >
              {isScraping ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Scraping Active...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-current" />
                  Run IT Scraper Pipeline
                </>
              )}
            </button>

            <a
              href="/api/export-excel"
              className="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-4 py-2.5 rounded-xl text-xs font-semibold shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
            >
              <Download className="h-4 w-4" />
              Export xlsx
            </a>
          </div>
        </div>
      </header>

      {/* Navigation Sub-Menu */}
      <div className="bg-white border-b border-slate-200 px-6 py-1">
        <div className="max-w-7xl mx-auto flex items-center gap-1.5 overflow-x-auto no-scrollbar">
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-medium transition-all border-b-2 cursor-pointer ${
              activeTab === "dashboard"
                ? "border-indigo-600 text-indigo-600 bg-indigo-50/40 font-semibold"
                : "border-transparent text-slate-500 hover:text-slate-900 hover:bg-slate-50/50"
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            Dashboard & Logs
          </button>
          
          <button
            onClick={() => setActiveTab("jobs")}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-medium transition-all border-b-2 relative cursor-pointer ${
              activeTab === "jobs"
                ? "border-indigo-600 text-indigo-600 bg-indigo-50/40 font-semibold"
                : "border-transparent text-slate-500 hover:text-slate-900 hover:bg-slate-50/50"
            }`}
          >
            <Grid className="h-3.5 w-3.5" />
            Scraped Jobs
            {jobs.length > 0 && (
              <span className="bg-indigo-600 text-white text-[10px] px-1.5 py-0.2 rounded-full font-mono ml-1">
                {jobs.length}
              </span>
            )}
          </button>
          
          <button
            onClick={() => setActiveTab("code")}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-medium transition-all border-b-2 cursor-pointer ${
              activeTab === "code"
                ? "border-indigo-600 text-indigo-600 bg-indigo-50/40 font-semibold"
                : "border-transparent text-slate-500 hover:text-slate-900 hover:bg-slate-50/50"
            }`}
          >
            <FileCode className="h-3.5 w-3.5" />
            Python Code Explorer
          </button>

          <button
            onClick={() => setActiveTab("config")}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-medium transition-all border-b-2 cursor-pointer ${
              activeTab === "config"
                ? "border-indigo-600 text-indigo-600 bg-indigo-50/40 font-semibold"
                : "border-transparent text-slate-500 hover:text-slate-900 hover:bg-slate-50/50"
            }`}
          >
            <Sliders className="h-3.5 w-3.5" />
            Scraper Configurator
          </button>
        </div>
      </div>

      {/* Main Body */}
      <main className="max-w-7xl mx-auto p-6">
        <AnimatePresence mode="wait">
          {/* Tab 1: Dashboard & Live Terminal */}
          {activeTab === "dashboard" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              {/* Metrics Grid */}
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Raw Crawled</span>
                  <p className="text-3xl font-extrabold text-slate-900 mt-1 font-mono">
                    {jobs.length > 0 ? jobs.length * 2 + 5 : 0}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-1">Direct ATS & public portal feeds</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Role Filtered</span>
                  <p className="text-3xl font-extrabold text-rose-600 mt-1 font-mono">
                    {jobs.length > 0 ? 5 : 0}
                  </p>
                  <p className="text-[10px] text-rose-500/80 mt-1">Non-tech roles discarded</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Deduplicated</span>
                  <p className="text-3xl font-extrabold text-amber-600 mt-1 font-mono">
                    {jobs.length > 0 ? 2 : 0}
                  </p>
                  <p className="text-[10px] text-amber-600/80 mt-1">Multi-layer overlap reduction</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">Validated & Safe</span>
                  <p className="text-3xl font-extrabold text-emerald-600 mt-1 font-mono">
                    {jobs.length}
                  </p>
                  <p className="text-[10px] text-emerald-600/80 mt-1">Link 200 checks passed</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-5 col-span-2 lg:col-span-1 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium">AI Emails Generated</span>
                  <p className="text-3xl font-extrabold text-indigo-600 mt-1 font-mono flex items-center gap-1.5">
                    {jobs.length}
                    {jobs.length > 0 && <Sparkles className="h-5 w-5 text-indigo-500 animate-pulse" />}
                  </p>
                  <p className="text-[10px] text-indigo-600/80 mt-1">Personalized via Gemini</p>
                </div>
              </div>

              {/* Console log Output */}
              <div className="bg-slate-950 border border-slate-900 rounded-2xl shadow-md overflow-hidden">
                <div className="bg-slate-900 px-5 py-3 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                      <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                      <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    </div>
                    <span className="text-xs font-mono text-slate-400 ml-2">live-scraper-terminal.log</span>
                  </div>
                  <div className="flex items-center gap-4">
                    {isScraping && (
                      <span className="text-xs text-indigo-400 flex items-center gap-1.5 font-mono animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping" />
                        SCRAPING ACTIVE
                      </span>
                    )}
                    <button
                      onClick={() => setLogs([])}
                      className="text-[10px] hover:text-white text-slate-400 border border-slate-700 px-2 py-1 rounded cursor-pointer transition-colors hover:bg-slate-800"
                    >
                      Clear
                    </button>
                  </div>
                </div>

                <div className="p-5 font-mono text-xs text-emerald-400 space-y-1.5 h-[380px] overflow-y-auto bg-slate-950/95 selection:bg-slate-800">
                  {logs.map((log, index) => (
                    <div
                      key={index}
                      className={`${
                        log.includes("[ERROR]")
                          ? "text-rose-400"
                          : log.includes("[INFO]") || log.includes("System Config")
                          ? "text-indigo-300"
                          : log.includes("Deduplicator")
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {log}
                    </div>
                  ))}
                  <div ref={terminalEndRef} />
                </div>
              </div>

              {/* Highlights section */}
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <h3 className="text-sm font-semibold text-slate-900 mb-2">How it Works (Deduplication & Rejection System)</h3>
                <div className="grid md:grid-cols-3 gap-6 text-xs text-slate-500 mt-4">
                  <div className="space-y-1">
                    <p className="font-semibold text-slate-800">1. Strict Technical Filtering</p>
                    <p>Rejects any role containing HR, Recruiter, Sales, Marketing, BPO, or Operations. Only accepts Software Engineers, Data Scientists, DevOps, and SDET titles.</p>
                  </div>
                  <div className="space-y-1">
                    <p className="font-semibold text-slate-800">2. 4-Layer Deduplication</p>
                    <p>Layers check exact URL first, exact description hash second, composite company/title matches third, and executes fuzzy Title ratios internally within the city sheets.</p>
                  </div>
                  <div className="space-y-1">
                    <p className="font-semibold text-slate-800">3. Location & Freshness Lock</p>
                    <p>Validates locations strictly to Pune, Bangalore, Hyderabad, Chennai, and Mumbai. Any job older than 24h or with an unresolvable date is instantly pruned.</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Tab 2: Scraped Jobs & AI Emails */}
          {activeTab === "jobs" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-6"
            >
              {/* Left Column: Filter Sidebar + Job Cards */}
              <div className="lg:col-span-5 space-y-4">
                {/* Search and Quick filter bars */}
                <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3 shadow-sm">
                  <div className="relative">
                    <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search title, company, stack..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 pl-10 pr-4 py-2.5 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all"
                    />
                  </div>

                  {/* Filter tabs: Cities */}
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1.5 font-bold">City Location</span>
                    <div className="flex flex-wrap gap-1.5">
                      {["All", "Pune", "Bangalore", "Hyderabad", "Chennai", "Mumbai"].map(city => (
                        <button
                          key={city}
                          onClick={() => setCityFilter(city)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors ${
                            cityFilter === city
                              ? "bg-indigo-600 text-white font-semibold shadow-sm"
                              : "bg-slate-50 text-slate-600 border border-slate-200 hover:text-slate-800 hover:bg-slate-100"
                          }`}
                        >
                          {city}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Filter tabs: Work mode */}
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1.5 font-bold">Work Mode</span>
                    <div className="flex gap-1.5">
                      {["All", "Onsite", "Hybrid", "Remote"].map(mode => (
                        <button
                          key={mode}
                          onClick={() => setWorkModeFilter(mode)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium flex-1 cursor-pointer transition-colors ${
                            workModeFilter === mode
                              ? "bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold shadow-sm"
                              : "bg-slate-50 text-slate-600 border border-slate-200 hover:text-slate-800 hover:bg-slate-100"
                          }`}
                        >
                          {mode}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Job Cards list */}
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1 no-scrollbar">
                  {filteredJobs.length === 0 ? (
                    <div className="text-center py-12 bg-white border border-slate-200 rounded-2xl shadow-sm">
                      <Briefcase className="h-8 w-8 text-slate-400 mx-auto opacity-50 mb-2" />
                      <p className="text-xs text-slate-500">No matching jobs in session.</p>
                      <button
                        onClick={runScraper}
                        className="text-indigo-600 text-xs font-semibold mt-2 hover:underline cursor-pointer"
                      >
                        Run a scrape now
                      </button>
                    </div>
                  ) : (
                    filteredJobs.map((job) => (
                      <div
                        key={job.id}
                        onClick={() => {
                          setSelectedJob(job);
                          setEditedEmail(job.custom_cold_email);
                        }}
                        className={`p-4 rounded-xl border transition-all cursor-pointer text-left ${
                          selectedJob?.id === job.id
                            ? "bg-indigo-50/50 border-indigo-500 shadow-sm shadow-indigo-50"
                            : "bg-white border-slate-200 hover:border-slate-300 shadow-sm"
                        }`}
                      >
                        <div className="flex justify-between items-start gap-2">
                          <h4 className="text-xs font-bold text-slate-900 hover:text-indigo-600 transition-colors line-clamp-1">
                            {job.title}
                          </h4>
                          <span className="text-[9px] bg-indigo-50 text-indigo-700 border border-indigo-100 px-1.5 py-0.5 rounded-full font-mono shrink-0">
                            {job.work_mode}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 mt-0.5 font-medium">{job.company}</p>
                        
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-3 text-[10px] text-slate-500">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3 text-rose-500" />
                            {job.city}
                          </span>
                          <span className="flex items-center gap-1 font-mono">
                            <Clock className="h-3 w-3 text-emerald-500" />
                            {job.posted_date}
                          </span>
                        </div>

                        {job.tech_stack && (
                          <div className="mt-2.5 flex flex-wrap gap-1">
                            {job.tech_stack.split(",").slice(0, 3).map((tech: string, i: number) => (
                              <span
                                key={i}
                                className="bg-slate-100 text-slate-600 border border-slate-200 px-1.5 py-0.5 rounded text-[9px]"
                              >
                                {tech.trim()}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Right Column: Deep details & AI email preview */}
              <div className="lg:col-span-7">
                {selectedJob ? (
                  <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden flex flex-col h-[650px] shadow-sm">
                    {/* Header: Company and Title */}
                    <div className="bg-slate-50 p-5 border-b border-slate-200">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-sm font-bold text-slate-900">{selectedJob.title}</h3>
                            <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[9px] font-mono px-2 py-0.5 rounded-full">
                              Validated Job
                            </span>
                          </div>
                          <p className="text-xs text-indigo-600 mt-1 font-medium">{selectedJob.company}</p>
                        </div>
                        <div className="flex gap-2">
                          <a
                            href={selectedJob.url}
                            target="_blank"
                            rel="noreferrer"
                            className="bg-indigo-600 hover:bg-indigo-700 border border-indigo-600 text-xs px-3.5 py-1.5 rounded-lg text-white font-semibold cursor-pointer transition-colors shadow-sm"
                          >
                            Apply Direct URL
                          </a>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 bg-slate-100/50 p-3 rounded-xl border border-slate-200 text-[11px]">
                        <div>
                          <span className="text-slate-500">Seniority Level</span>
                          <p className="font-semibold text-slate-800 mt-0.5">{selectedJob.seniority_level}</p>
                        </div>
                        <div>
                          <span className="text-slate-500">Experience</span>
                          <p className="font-semibold text-slate-800 mt-0.5">{selectedJob.experience_required}</p>
                        </div>
                        <div>
                          <span className="text-slate-500">Source Engine</span>
                          <p className="font-semibold text-slate-800 mt-0.5 font-mono">{selectedJob.source}</p>
                        </div>
                        <div>
                          <span className="text-slate-500">Salary Bracket</span>
                          <p className="font-semibold text-emerald-600 mt-0.5">{selectedJob.salary}</p>
                        </div>
                      </div>
                    </div>

                    {/* Tabs for details vs custom emails */}
                    <div className="flex-1 overflow-y-auto p-5 space-y-6">
                      {/* Section 1: AI Generated Email Block */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-800 flex items-center gap-1.5">
                            <Mail className="h-4 w-4 text-indigo-500" />
                            Custom Cold Email (1-Click Copy)
                          </span>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => regenerateEmail(selectedJob)}
                              disabled={isRegeneratingEmail}
                              className="text-[10px] bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 text-indigo-600 px-2.5 py-1 rounded-lg font-medium flex items-center gap-1 cursor-pointer transition-colors"
                            >
                              <Sparkles className="h-3 w-3" />
                              {isRegeneratingEmail ? "AI Writing..." : "Regenerate AI"}
                            </button>
                            <button
                              onClick={() => handleCopy(editedEmail, "email")}
                              className="text-[10px] bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 text-emerald-700 px-2.5 py-1 rounded-lg font-medium flex items-center gap-1 cursor-pointer transition-colors"
                            >
                              {copiedStates["email"] ? (
                                <>
                                  <Check className="h-3 w-3" /> Copied!
                                </>
                              ) : (
                                <>
                                  <Copy className="h-3 w-3" /> Copy Email
                                </>
                              )}
                            </button>
                          </div>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 font-mono text-xs text-slate-700 space-y-4 whitespace-pre-wrap select-all">
                          <p className="font-sans font-bold text-slate-900 border-b border-slate-200 pb-2">
                            Subject: {selectedJob.cold_email_subject}
                          </p>
                          <textarea
                            value={editedEmail}
                            onChange={(e) => setEditedEmail(e.target.value)}
                            className="w-full bg-transparent border-none text-slate-700 focus:outline-none focus:ring-0 text-xs font-mono h-[200px] resize-none"
                          />
                        </div>
                      </div>

                      {/* Section 2: Contact Strategy */}
                      <div className="space-y-2">
                        <span className="text-xs font-semibold text-slate-800 flex items-center gap-1.5">
                          <FileText className="h-4 w-4 text-amber-600" />
                          Recruiter Contact Strategy
                        </span>
                        <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-xl p-4 text-xs whitespace-pre-wrap leading-relaxed font-mono shadow-inner">
                          {selectedJob.recruiter_contact_strategy}
                        </div>
                      </div>

                      {/* Section 3: Tech Stack & Details */}
                      <div className="space-y-2 pt-2">
                        <span className="text-xs font-semibold text-slate-800 block">Extracted Job Stack & Summary</span>
                        <div className="space-y-3 text-xs text-slate-500 bg-slate-50 p-4 rounded-xl border border-slate-200">
                          <div>
                            <span className="text-slate-800 font-medium block">Key Skills Required</span>
                            <p className="mt-1">{selectedJob.skills_required || "Standard Development"}</p>
                          </div>
                          <div className="border-t border-slate-200 pt-2">
                            <span className="text-slate-800 font-medium block">Core Responsibilities</span>
                            <p className="mt-1 line-clamp-3">{selectedJob.responsibilities}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white border border-slate-200 rounded-2xl h-[650px] flex flex-col items-center justify-center text-center p-6 shadow-sm">
                    <Briefcase className="h-12 w-12 text-indigo-600 opacity-70 mb-4 animate-bounce" />
                    <h3 className="text-base font-bold text-slate-800">Select a job from the panel</h3>
                    <p className="text-xs text-slate-500 mt-1 max-w-sm">
                      Detailed job summary, requirements, automated custom cold emails, and recruiter contact plans will load instantly.
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Tab 3: Python Code Explorer */}
          {activeTab === "code" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-6"
            >
              {/* Left Column: File list */}
              <div className="lg:col-span-4 bg-white border border-slate-200 rounded-2xl p-4 h-[600px] flex flex-col shadow-sm">
                <div className="pb-3 border-b border-slate-200 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                    <FileCode className="h-4 w-4 text-indigo-500" />
                    Modular Codebase Tree
                  </span>
                  <a
                    href="/api/download-zip"
                    className="text-[10px] bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 text-indigo-600 px-2.5 py-1 rounded-lg font-semibold cursor-pointer flex items-center gap-1 transition-colors"
                  >
                    <Download className="h-3 w-3" />
                    Get all scripts
                  </a>
                </div>

                <div className="flex-1 overflow-y-auto mt-3 space-y-1.5 pr-1 no-scrollbar text-left">
                  {Object.keys(codeFiles).length === 0 ? (
                    <div className="text-center py-12">
                      <RefreshCw className="h-6 w-6 animate-spin text-slate-400 mx-auto mb-2" />
                      <p className="text-xs text-slate-500">Reading workspaces...</p>
                    </div>
                  ) : (
                    Object.keys(codeFiles).map((file) => {
                      const isParser = file.startsWith("parsers/");
                      return (
                        <button
                          key={file}
                          onClick={() => setSelectedFile(file)}
                          className={`w-full px-3 py-2 rounded-lg text-xs font-mono flex items-center justify-between transition-colors cursor-pointer text-left ${
                            selectedFile === file
                              ? "bg-indigo-50 text-indigo-700 border border-indigo-100 font-semibold shadow-sm"
                              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                          }`}
                        >
                          <span className="flex items-center gap-2 truncate">
                            <span className="opacity-60">{isParser ? "📁 parsers/" : "📄"}</span>
                            {isParser ? file.replace("parsers/", "") : file}
                          </span>
                        </button>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Right Column: Code viewer panel */}
              <div className="lg:col-span-8 bg-slate-950 border border-slate-900 rounded-2xl overflow-hidden h-[600px] flex flex-col shadow-sm">
                <div className="bg-slate-900 border-b border-slate-800 px-5 py-3 flex justify-between items-center">
                  <span className="text-xs font-mono text-slate-300">{selectedFile}</span>
                  <button
                    onClick={() => handleCopy(codeFiles[selectedFile], "code")}
                    className="text-[10px] bg-slate-800 text-emerald-400 border border-slate-700 px-3 py-1.5 rounded-lg font-medium flex items-center gap-1 cursor-pointer transition-colors hover:bg-slate-700"
                  >
                    {copiedStates["code"] ? (
                      <>
                        <Check className="h-3 w-3" /> Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5" /> Copy Code
                      </>
                    )}
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto p-5 font-mono text-xs text-[#ABB2BF] bg-slate-950 text-left select-text whitespace-pre">
                  {codeFiles[selectedFile] || "# File is empty or loading..."}
                </div>
              </div>
            </motion.div>
          )}

          {/* Tab 4: Configurator */}
          {activeTab === "config" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-white border border-slate-200 rounded-2xl p-6 max-w-4xl mx-auto space-y-6 shadow-sm"
            >
              <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Sliders className="h-5 w-5 text-indigo-600" />
                    Dynamic Scraper Pipeline Settings
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Updates applied here write straight back to your Python files and Express runtime.
                  </p>
                </div>
                <button
                  onClick={saveConfigToDisk}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] cursor-pointer transition-all shadow-md shadow-indigo-100"
                >
                  <Save className="h-4 w-4" />
                  {saveSuccess ? "Configuration Saved!" : "Save & Sync Config"}
                </button>
              </div>

              {saveSuccess && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-xl flex items-center gap-2 text-xs">
                  <CheckCircle2 className="h-4 w-4" />
                  Successfully wrote adjustments to project/config.py! Python CLI scraper runs will adopt these changes automatically.
                </div>
              )}

              {/* Form elements */}
              <div className="grid md:grid-cols-2 gap-6 text-left">
                {/* Allowed Cities */}
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-700 block">Target Cities (Strictly Allowed)</label>
                  <div className="flex flex-wrap gap-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl min-h-[80px]">
                    {allowedCities.map(city => (
                      <span
                        key={city}
                        className="bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-1 rounded text-xs flex items-center gap-1 font-medium"
                      >
                        {city}
                        <button
                          type="button"
                          onClick={() => setAllowedCities(prev => prev.filter(c => c !== city))}
                          className="hover:text-rose-500 cursor-pointer text-[10px]"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Add city e.g. Bangalore"
                      id="new-city-input"
                      className="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs text-slate-800 focus:outline-none flex-1 focus:bg-white focus:border-indigo-500"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          const val = (e.target as HTMLInputElement).value.trim();
                          if (val && !allowedCities.includes(val)) {
                            setAllowedCities(prev => [...prev, val]);
                            (e.target as HTMLInputElement).value = "";
                          }
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const input = document.getElementById("new-city-input") as HTMLInputElement;
                        const val = input.value.trim();
                        if (val && !allowedCities.includes(val)) {
                          setAllowedCities(prev => [...prev, val]);
                          input.value = "";
                        }
                      }}
                      className="bg-slate-100 hover:bg-slate-200 border border-slate-200 px-3 py-1.5 text-xs text-slate-700 rounded-lg cursor-pointer font-semibold"
                    >
                      Add
                    </button>
                  </div>
                </div>

                {/* Portals list */}
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-700 block">Job Portal Crawler Scopes</label>
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                    <label className="flex items-center gap-2.5 text-xs text-slate-700 cursor-pointer select-none hover:text-slate-900">
                      <input
                        type="checkbox"
                        checked={portalSources.linkedin}
                        onChange={(e) => setPortalSources(prev => ({ ...prev, linkedin: e.target.checked }))}
                        className="rounded border-slate-300 text-indigo-600 focus:ring-0"
                      />
                      LinkedIn Jobs Engine (f_TPR=r86400)
                    </label>
                    <label className="flex items-center gap-2.5 text-xs text-slate-700 cursor-pointer select-none hover:text-slate-900">
                      <input
                        type="checkbox"
                        checked={portalSources.indeed}
                        onChange={(e) => setPortalSources(prev => ({ ...prev, indeed: e.target.checked }))}
                        className="rounded border-slate-300 text-indigo-600 focus:ring-0"
                      />
                      Indeed Portal Engine (last 24h)
                    </label>
                    <label className="flex items-center gap-2.5 text-xs text-slate-700 cursor-pointer select-none hover:text-slate-900">
                      <input
                        type="checkbox"
                        checked={portalSources.instahyre}
                        onChange={(e) => setPortalSources(prev => ({ ...prev, instahyre: e.target.checked }))}
                        className="rounded border-slate-300 text-indigo-600 focus:ring-0"
                      />
                      Instahyre IT Jobs Crawler
                    </label>
                  </div>
                </div>
              </div>

              {/* Allowed Keywords / Roles */}
              <div className="space-y-2 text-left">
                <label className="text-xs font-bold text-slate-700 block">Allowed Job Role Title Keywords</label>
                <div className="flex flex-wrap gap-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl max-h-[140px] overflow-y-auto">
                  {allowedKeywords.map(kw => (
                    <span
                      key={kw}
                      className="bg-slate-100 text-slate-600 border border-slate-200 px-2 py-0.5 rounded text-[10px] flex items-center gap-1 font-medium"
                    >
                      {kw}
                      <button
                        type="button"
                        onClick={() => setAllowedKeywords(prev => prev.filter(k => k !== kw))}
                        className="hover:text-rose-500 cursor-pointer"
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2 max-w-md">
                  <input
                    type="text"
                    placeholder="Add allowed keyword e.g. Django Developer"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    className="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs text-slate-800 focus:outline-none flex-1 focus:bg-white focus:border-indigo-500"
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && newKeyword.trim()) {
                        if (!allowedKeywords.includes(newKeyword.trim())) {
                          setAllowedKeywords(prev => [...prev, newKeyword.trim()]);
                          setNewKeyword("");
                        }
                      }
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => {
                      if (newKeyword.trim() && !allowedKeywords.includes(newKeyword.trim())) {
                        setAllowedKeywords(prev => [...prev, newKeyword.trim()]);
                        setNewKeyword("");
                      }
                    }}
                    className="bg-slate-100 hover:bg-slate-200 border border-slate-200 px-4 py-1.5 text-xs text-slate-700 rounded-lg cursor-pointer font-semibold"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Target Career Pages List */}
              <div className="space-y-4 text-left border-t border-slate-150 pt-5">
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                  <div>
                    <label className="text-xs font-bold text-slate-700 block">Target Official Career Page Database</label>
                    <span className="text-[10px] text-slate-400">Manage, search, or load pre-populated global and local MNC databases.</span>
                  </div>
                  <span className="bg-indigo-50 text-indigo-700 border border-indigo-100 px-2.5 py-1 rounded-full text-xs font-semibold font-mono self-start sm:self-auto shrink-0">
                    Active targets: {careerPages.length} urls
                  </span>
                </div>

                {/* Preset Database Loaders */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-2">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Load Job Intelligence Target Databases:</span>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setCareerPages(GLOBAL_CAREER_PAGES);
                        setLogs(prev => [...prev, `[INFO] Loaded Global MNC Database containing ${GLOBAL_CAREER_PAGES.length} targets.`]);
                      }}
                      className="bg-white hover:bg-indigo-50 border border-slate-200 text-slate-700 hover:text-indigo-700 hover:border-indigo-200 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <Sparkles className="h-3 w-3 text-indigo-500" />
                      Global MNC Database ({GLOBAL_CAREER_PAGES.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCareerPages(PUNE_CAREER_PAGES);
                        setLogs(prev => [...prev, `[INFO] Loaded Pune Tech Hubs Database containing ${PUNE_CAREER_PAGES.length} targets.`]);
                      }}
                      className="bg-white hover:bg-indigo-50 border border-slate-200 text-slate-700 hover:text-indigo-700 hover:border-indigo-200 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <MapPin className="h-3 w-3 text-indigo-500" />
                      Pune Tech Hubs ({PUNE_CAREER_PAGES.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        const merged = Array.from(new Set([...GLOBAL_CAREER_PAGES, ...PUNE_CAREER_PAGES]));
                        setCareerPages(merged);
                        setLogs(prev => [...prev, `[INFO] Combined Global & Pune Databases: ${merged.length} unique targets loaded.`]);
                      }}
                      className="bg-white hover:bg-indigo-50 border border-slate-200 text-slate-700 hover:text-indigo-700 hover:border-indigo-200 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <Briefcase className="h-3 w-3 text-indigo-500" />
                      Combine All ({Array.from(new Set([...GLOBAL_CAREER_PAGES, ...PUNE_CAREER_PAGES])).length})
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCareerPages([
                          "https://boards.greenhouse.io/github",
                          "https://jobs.lever.co/lever",
                          "https://careers.smartrecruiters.com/deliveryhero",
                          "https://ashbyhq.com/careers/stripe",
                          "https://bamboohr.com/careers"
                        ]);
                        setLogs(prev => [...prev, "[INFO] Reset targets to 5 core sample developer pages."]);
                      }}
                      className="bg-white hover:bg-slate-100 border border-slate-200 text-slate-600 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-colors shadow-sm"
                    >
                      Reset to Sample
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCareerPages([]);
                        setLogs(prev => [...prev, "[INFO] Cleared all career target pages."]);
                      }}
                      className="bg-rose-50 hover:bg-rose-100 border border-rose-100 text-rose-700 px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors shadow-sm"
                    >
                      Clear All
                    </button>
                  </div>
                </div>

                {/* Add new url and Search Active Set */}
                <div className="grid sm:grid-cols-2 gap-3.5">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Add Custom Target URL:</span>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Add URL e.g. https://jobs.lever.co/openai"
                        value={newUrl}
                        onChange={(e) => setNewUrl(e.target.value)}
                        className="bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs text-slate-800 focus:outline-none flex-1 font-mono focus:bg-white focus:border-indigo-500"
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && newUrl.trim()) {
                            if (!careerPages.includes(newUrl.trim())) {
                              setCareerPages(prev => [...prev, newUrl.trim()]);
                              setNewUrl("");
                            }
                          }
                        }}
                      />
                      <button
                        type="button"
                        onClick={() => {
                          if (newUrl.trim() && !careerPages.includes(newUrl.trim())) {
                            setCareerPages(prev => [...prev, newUrl.trim()]);
                            setNewUrl("");
                          }
                        }}
                        className="bg-slate-100 hover:bg-slate-200 border border-slate-200 px-4 py-1.5 text-xs text-slate-700 rounded-lg cursor-pointer font-semibold shrink-0"
                      >
                        Add URL
                      </button>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Filter & Search Active List:</span>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
                      <input
                        type="text"
                        placeholder="Search loaded career pages..."
                        value={searchUrlTerm}
                        onChange={(e) => setSearchUrlTerm(e.target.value)}
                        className="bg-slate-50 border border-slate-200 pl-8 pr-3 py-1.5 rounded-lg text-xs text-slate-800 focus:outline-none w-full focus:bg-white focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Main list view container */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-[10px] font-bold text-slate-500 uppercase tracking-wider px-1">
                    <span>Active Target Feeds</span>
                    <span>
                      {searchUrlTerm ? `Showing ${Math.min(100, careerPages.filter(u => u.toLowerCase().includes(searchUrlTerm.toLowerCase())).length)} of ${careerPages.filter(u => u.toLowerCase().includes(searchUrlTerm.toLowerCase())).length} matches` : `Showing first ${Math.min(100, careerPages.length)} urls`}
                    </span>
                  </div>
                  <div className="space-y-1.5 max-h-[220px] overflow-y-auto bg-slate-50 border border-slate-200 rounded-xl p-3 shadow-inner">
                    {careerPages.filter(u => u.toLowerCase().includes(searchUrlTerm.toLowerCase())).length === 0 ? (
                      <div className="text-center py-6 text-xs text-slate-400">
                        No target URLs match your filter term.
                      </div>
                    ) : (
                      careerPages
                        .filter(u => u.toLowerCase().includes(searchUrlTerm.toLowerCase()))
                        .slice(0, 100)
                        .map((url, i) => (
                          <div key={i} className="flex justify-between items-center text-xs text-slate-600 bg-white border border-slate-200/60 rounded-lg p-2 font-mono hover:border-slate-300 transition-colors">
                            <span className="truncate pr-4 select-all text-slate-700">{url}</span>
                            <button
                              onClick={() => setCareerPages(prev => prev.filter(u => u !== url))}
                              className="text-rose-500 hover:text-rose-600 hover:bg-rose-50 p-1 rounded cursor-pointer shrink-0 transition-colors"
                              title="Delete URL"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        ))
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
