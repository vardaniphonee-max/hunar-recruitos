"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type View = "overview" | "roles" | "talent" | "campaigns" | "candidate" | "attendance";
type CampaignState = "NOT_STARTED" | "INITIATED" | "RINGING" | "IN_PROGRESS" | "COMPLETED";

const navItems: { id: View; label: string; icon: string }[] = [
  { id: "overview", label: "Overview", icon: "⌂" },
  { id: "roles", label: "Roles", icon: "◇" },
  { id: "talent", label: "Talent search", icon: "⌕" },
  { id: "campaigns", label: "Campaigns", icon: "◉" },
  { id: "attendance", label: "Attendance blueprint", icon: "⌘" },
];

const candidates = [
  {
    id: 1,
    name: "Ananya Rao",
    initials: "AR",
    role: "Senior Customer Success Manager",
    company: "Chargebee",
    location: "Bengaluru, India",
    experience: "7 years",
    skills: ["B2B SaaS", "Enterprise accounts", "Onboarding"],
    score: 94,
    source: "Demo · Apollo-shaped",
    tone: "violet",
  },
  {
    id: 2,
    name: "Rohan Mehta",
    initials: "RM",
    role: "Customer Success Lead",
    company: "Freshworks",
    location: "Chennai, India",
    experience: "6 years",
    skills: ["SaaS", "Team leadership", "Retention"],
    score: 89,
    source: "Demo · Apollo-shaped",
    tone: "amber",
  },
  {
    id: 3,
    name: "Nisha Verma",
    initials: "NV",
    role: "Enterprise Success Partner",
    company: "Darwinbox",
    location: "Hyderabad, India",
    experience: "8 years",
    skills: ["Enterprise SaaS", "Renewals", "QBRs"],
    score: 86,
    source: "Demo · Apollo-shaped",
    tone: "blue",
  },
  {
    id: 4,
    name: "Kabir Shah",
    initials: "KS",
    role: "Customer Experience Manager",
    company: "Razorpay",
    location: "Mumbai, India",
    experience: "5 years",
    skills: ["Fintech", "Escalations", "Analytics"],
    score: 81,
    source: "Demo · Apollo-shaped",
    tone: "green",
  },
];

const screeningQuestions = [
  "Tell me about the largest portfolio of enterprise accounts you have managed.",
  "How do you identify and respond to churn risk?",
  "Are you comfortable working from Bengaluru three days a week?",
  "What is your notice period and expected compensation?",
];

function DemoPill() {
  return <span className="demo-pill"><span /> Demo mode</span>;
}

function StatusBadge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`status-badge ${tone}`}>{children}</span>;
}

function Avatar({ initials, tone = "violet" }: { initials: string; tone?: string }) {
  return <span className={`avatar ${tone}`}>{initials}</span>;
}

function AppIcon({ children }: { children: React.ReactNode }) {
  return <span className="app-icon" aria-hidden="true">{children}</span>;
}

export function RecruitOSApp() {
  const [view, setView] = useState<View>("overview");
  const [mobileNav, setMobileNav] = useState(false);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(true);
  const [shortlisted, setShortlisted] = useState<number[]>([1, 2]);
  const [selectedCandidateId, setSelectedCandidateId] = useState(1);
  const [campaignState, setCampaignState] = useState<CampaignState>("NOT_STARTED");
  const [showConfirm, setShowConfirm] = useState(false);
  const [notice, setNotice] = useState("");
  const [roleSaved, setRoleSaved] = useState(true);
  const [attendanceLayer, setAttendanceLayer] = useState<"capture" | "verify" | "reconcile">("capture");
  const campaignTimers = useRef<number[]>([]);
  const storageReady = useRef(false);

  useEffect(() => {
    const restoreTimer = window.setTimeout(() => {
      const hash = window.location.hash.replace("#", "") as View;
      if (["overview", "roles", "talent", "campaigns", "candidate", "attendance"].includes(hash)) setView(hash);
      const savedShortlist = window.localStorage.getItem("recruitos-shortlist");
      const savedCandidate = Number(window.localStorage.getItem("recruitos-selected-candidate"));
      const savedCampaign = window.localStorage.getItem("recruitos-campaign-state") as CampaignState | null;
      storageReady.current = true;
      if (savedShortlist) {
        try { setShortlisted(JSON.parse(savedShortlist)); } catch { window.localStorage.removeItem("recruitos-shortlist"); }
      }
      if (candidates.some((candidate) => candidate.id === savedCandidate)) setSelectedCandidateId(savedCandidate);
      if (savedCampaign && ["NOT_STARTED", "INITIATED", "RINGING", "IN_PROGRESS", "COMPLETED"].includes(savedCampaign)) setCampaignState(savedCampaign);
    }, 0);

    const handleHistory = () => {
      const next = window.location.hash.replace("#", "") as View;
      if (["overview", "roles", "talent", "campaigns", "candidate", "attendance"].includes(next)) setView(next);
    };
    window.addEventListener("popstate", handleHistory);
    return () => {
      window.clearTimeout(restoreTimer);
      window.removeEventListener("popstate", handleHistory);
      campaignTimers.current.forEach(window.clearTimeout);
    };
  }, []);

  useEffect(() => {
    if (storageReady.current) window.localStorage.setItem("recruitos-shortlist", JSON.stringify(shortlisted));
  }, [shortlisted]);

  useEffect(() => {
    if (storageReady.current) window.localStorage.setItem("recruitos-campaign-state", campaignState);
  }, [campaignState]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(""), 2800);
    return () => window.clearTimeout(timer);
  }, [notice]);

  const pageTitle = useMemo(() => {
    const names: Record<View, [string, string]> = {
      overview: ["Good evening, Vardan", "Here’s what’s moving across your hiring pipeline."],
      roles: ["Customer Success Manager", "Role setup, screening plan, and pipeline activity."],
      talent: ["Talent search", "Find people who match the role, then bring the best into your pipeline."],
      campaigns: ["Voice campaigns", "Review, launch, and track candidate conversations."],
      candidate: ["Candidate review", "One profile, every hiring signal, ready for human judgment."],
      attendance: ["Attendance without smartphones", "A practical operating blueprint for 1,000 people across 100 sites."],
    };
    return names[view];
  }, [view]);

  function navigate(next: View) {
    setView(next);
    setMobileNav(false);
    if (window.location.hash !== `#${next}`) window.history.pushState({}, "", `#${next}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function runSearch() {
    setSearching(true);
    setSearched(false);
    window.setTimeout(() => {
      setSearching(false);
      setSearched(true);
      setNotice("4 demo candidates found");
    }, 950);
  }

  function toggleShortlist(id: number) {
    setShortlisted((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
    );
  }

  function openCandidate(id: number) {
    setSelectedCandidateId(id);
    if (storageReady.current) window.localStorage.setItem("recruitos-selected-candidate", String(id));
    navigate("candidate");
  }

  function launchCampaign() {
    setShowConfirm(false);
    campaignTimers.current.forEach(window.clearTimeout);
    setCampaignState("INITIATED");
    setNotice("Demo campaign started — no real call was placed");
    const lifecycle: Array<[CampaignState, number]> = [
      ["RINGING", 800],
      ["IN_PROGRESS", 1700],
      ["COMPLETED", 3000],
    ];
    campaignTimers.current = lifecycle.map(([state, delay]) => window.setTimeout(() => setCampaignState(state), delay));
  }

  return (
    <main className="app-shell">
      <aside className={`sidebar ${mobileNav ? "open" : ""}`}>
        <button className="brand" onClick={() => navigate("overview")} aria-label="Go to overview">
          <span className="brand-mark">H</span>
          <span>Hunar <strong>RecruitOS</strong></span>
        </button>

        <nav aria-label="Primary navigation">
          <p className="nav-label">Workspace</p>
          {navItems.map((item) => (
            <button
              key={item.id}
              className={view === item.id ? "active" : ""}
              onClick={() => navigate(item.id)}
            >
              <AppIcon>{item.icon}</AppIcon>
              {item.label}
              {item.id === "campaigns" && <span className="nav-count">3</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="integration-card">
            <span className="pulse-dot" />
            <div>
              <strong>Demo providers active</strong>
              <small>Hunar + Apollo adapters ready</small>
            </div>
          </div>
          <div className="profile-row">
            <Avatar initials="VM" tone="ink" />
            <div><strong>Vardan Malik</strong><small>Recruiter workspace</small></div>
            <button aria-label="Open account menu">•••</button>
          </div>
        </div>
      </aside>

      {mobileNav && <button className="sidebar-scrim" onClick={() => setMobileNav(false)} aria-label="Close navigation" />}

      <section className="workspace">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobileNav(true)} aria-label="Open navigation">☰</button>
          <div className="breadcrumb"><span>RecruitOS</span><b>/</b>{pageTitle[0]}</div>
          <div className="top-actions">
            <DemoPill />
            <button className="icon-button" aria-label="Search">⌕</button>
            <button className="icon-button has-alert" aria-label="Notifications">♢</button>
          </div>
        </header>

        <div className="page">
          <div className="page-heading">
            <div>
              <h1>{pageTitle[0]}</h1>
              <p>{pageTitle[1]}</p>
            </div>
            {view === "overview" && (
              <button className="primary-button" onClick={() => navigate("roles")}><span>＋</span> Create role</button>
            )}
            {view === "talent" && (
              <button className="secondary-button" onClick={() => setShortlisted([])}>Clear shortlist</button>
            )}
          </div>

          {view === "overview" && <Overview onNavigate={navigate} />}
          {view === "roles" && (
            <Roles roleSaved={roleSaved} setRoleSaved={setRoleSaved} onNavigate={navigate} setNotice={setNotice} />
          )}
          {view === "talent" && (
            <TalentSearch
              searching={searching}
              searched={searched}
              shortlisted={shortlisted}
              onSearch={runSearch}
              onToggle={toggleShortlist}
              onCandidate={openCandidate}
              onCampaign={() => navigate("campaigns")}
            />
          )}
          {view === "campaigns" && (
            <Campaigns campaignState={campaignState} onLaunch={() => setShowConfirm(true)} onCandidate={() => openCandidate(1)} />
          )}
          {view === "candidate" && <CandidateDetail candidateId={selectedCandidateId} setNotice={setNotice} />}
          {view === "attendance" && (
            <AttendanceBlueprint layer={attendanceLayer} setLayer={setAttendanceLayer} />
          )}
        </div>
      </section>

      {showConfirm && (
        <div className="modal-backdrop" role="presentation">
          <section className="confirm-modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
            <div className="modal-icon">◉</div>
            <StatusBadge tone="demo">Demo simulation</StatusBadge>
            <h2 id="confirm-title">Launch voice campaign?</h2>
            <p>This will simulate Hunar call states for two shortlisted candidates. No phone call or paid API request will be made.</p>
            <div className="modal-summary">
              <div><span>Candidates</span><strong>2</strong></div>
              <div><span>Questions</span><strong>4</strong></div>
              <div><span>Language</span><strong>English</strong></div>
            </div>
            <div className="modal-actions">
              <button className="secondary-button" onClick={() => setShowConfirm(false)}>Cancel</button>
              <button className="primary-button" onClick={launchCampaign}>Start demo campaign</button>
            </div>
          </section>
        </div>
      )}

      {notice && <div className="toast" role="status"><span>✓</span>{notice}</div>}
    </main>
  );
}

function Overview({ onNavigate }: { onNavigate: (view: View) => void }) {
  const stats = [
    { label: "Active roles", value: "4", delta: "+1 this week", icon: "◇", tone: "violet" },
    { label: "Candidates", value: "128", delta: "+24 discovered", icon: "◎", tone: "blue" },
    { label: "Calls completed", value: "42", delta: "78% completion", icon: "◉", tone: "green" },
    { label: "Qualified", value: "18", delta: "43% of completed", icon: "✓", tone: "amber" },
  ];
  return (
    <div className="stack-xl">
      <div className="metric-grid">
        {stats.map((stat) => (
          <article className="metric-card" key={stat.label}>
            <span className={`metric-icon ${stat.tone}`}>{stat.icon}</span>
            <p>{stat.label}</p>
            <strong>{stat.value}</strong>
            <small><span>↗</span>{stat.delta}</small>
          </article>
        ))}
      </div>

      <div className="overview-grid">
        <article className="panel pipeline-panel">
          <div className="panel-heading">
            <div><h2>Hiring pipeline</h2><p>Candidate movement across active roles</p></div>
            <button>Last 30 days⌄</button>
          </div>
          <div className="funnel">
            <div><span><i className="violet" />Discovered</span><b>128</b><div><em style={{ width: "100%" }} /></div></div>
            <div><span><i className="blue" />Shortlisted</span><b>64</b><div><em style={{ width: "50%" }} /></div></div>
            <div><span><i className="amber" />Contacted</span><b>54</b><div><em style={{ width: "42%" }} /></div></div>
            <div><span><i className="green" />Qualified</span><b>18</b><div><em style={{ width: "14%" }} /></div></div>
          </div>
          <div className="funnel-foot"><span><b>14.1%</b> discovery-to-qualified</span><span>Updated just now</span></div>
        </article>

        <article className="panel call-outcome-panel">
          <div className="panel-heading"><div><h2>Call outcomes</h2><p>54 attempts this month</p></div><button aria-label="More options">•••</button></div>
          <div className="donut-wrap">
            <div className="donut"><div><strong>78%</strong><span>completed</span></div></div>
            <div className="legend">
              <span><i className="green" />Completed <b>42</b></span>
              <span><i className="amber" />No answer <b>7</b></span>
              <span><i className="red" />Failed <b>3</b></span>
              <span><i className="gray" />Queued <b>2</b></span>
            </div>
          </div>
        </article>
      </div>

      <div className="overview-grid lower">
        <article className="panel activity-panel">
          <div className="panel-heading"><div><h2>Recent activity</h2><p>Latest candidate and campaign updates</p></div><button>View all</button></div>
          {[
            ["AR", "Ananya Rao completed the voice screen", "Customer Success Manager · 8 min ago", "Completed", "green"],
            ["RM", "Rohan Mehta was shortlisted", "Customer Success Manager · 24 min ago", "Shortlisted", "violet"],
            ["NV", "Nisha Verma’s call was not answered", "Customer Success Manager · 1 hr ago", "Retry due", "amber"],
          ].map((row, index) => (
            <button className="activity-row" key={row[0]} onClick={() => index === 0 && onNavigate("candidate")}>
              <Avatar initials={row[0]} tone={index === 1 ? "amber" : index === 2 ? "blue" : "violet"} />
              <span><strong>{row[1]}</strong><small>{row[2]}</small></span>
              <StatusBadge tone={row[4]}>{row[3]}</StatusBadge>
              <b>›</b>
            </button>
          ))}
        </article>

        <article className="panel focus-card">
          <div className="focus-top"><span>Priority role</span><StatusBadge tone="green">On track</StatusBadge></div>
          <h2>Customer Success Manager</h2>
          <p>Bengaluru · 5–8 years</p>
          <div className="focus-stats"><span><b>36</b> candidates</span><span><b>12</b> shortlisted</span><span><b>6</b> qualified</span></div>
          <div className="progress-label"><span>Pipeline progress</span><strong>67%</strong></div>
          <div className="progress-bar"><span /></div>
          <button className="primary-button full" onClick={() => onNavigate("talent")}>Continue sourcing <b>→</b></button>
        </article>
      </div>
    </div>
  );
}

function Roles({ roleSaved, setRoleSaved, onNavigate, setNotice }: {
  roleSaved: boolean;
  setRoleSaved: (value: boolean) => void;
  onNavigate: (view: View) => void;
  setNotice: (message: string) => void;
}) {
  const [title, setTitle] = useState("Customer Success Manager");
  const [location, setLocation] = useState("Bengaluru, India");
  const [description, setDescription] = useState("Own a portfolio of enterprise customers, drive onboarding and adoption, identify churn risk, and partner with sales and product to deliver measurable customer outcomes.");
  const [formError, setFormError] = useState("");

  function saveRole() {
    if (title.trim().length < 3) return setFormError("Role title must contain at least 3 characters.");
    if (location.trim().length < 2) return setFormError("Add a valid work location.");
    if (description.trim().length < 30) return setFormError("Job description must contain at least 30 characters.");
    setFormError("");
    setRoleSaved(true);
    setNotice("Role saved");
  }

  return (
    <div className="role-layout">
      <section className="panel role-form">
        <div className="section-kicker"><span>01</span> Role brief</div>
        {formError && <div className="form-error" role="alert"><span>!</span>{formError}</div>}
        <label>Role title<input required minLength={3} maxLength={160} value={title} onChange={(event) => { setTitle(event.target.value); setRoleSaved(false); setFormError(""); }} /></label>
        <div className="field-grid">
          <label>Location<input required minLength={2} maxLength={160} value={location} onChange={(event) => { setLocation(event.target.value); setRoleSaved(false); setFormError(""); }} /></label>
          <label>Experience<select defaultValue="5–8 years" onChange={() => setRoleSaved(false)}><option>3–5 years</option><option>5–8 years</option><option>8–12 years</option></select></label>
        </div>
        <label>Job description<textarea required minLength={30} maxLength={8000} value={description} onChange={(event) => { setDescription(event.target.value); setRoleSaved(false); setFormError(""); }} /></label>
        <label>Required skills<div className="tag-input"><span>B2B SaaS ×</span><span>Enterprise accounts ×</span><span>Retention ×</span><input aria-label="Add skill" placeholder="Add skill…" /></div></label>

        <div className="section-divider" />
        <div className="section-kicker"><span>02</span> Voice screening plan <StatusBadge tone="demo">Hunar-ready</StatusBadge></div>
        <p className="helper">These questions become the structured result schema for your voice agent.</p>
        <div className="question-list">
          {screeningQuestions.map((question, index) => (
            <div key={question}><span>{index + 1}</span><textarea aria-label={`Screening question ${index + 1}`} defaultValue={question} onChange={() => setRoleSaved(false)} /><button aria-label={`Remove question ${index + 1}`}>×</button></div>
          ))}
        </div>
        <button className="dashed-button">＋ Add screening question</button>
        <div className="form-actions">
          <span>{roleSaved ? "All changes saved" : "Unsaved changes"}</span>
          <button className="secondary-button" onClick={() => onNavigate("overview")}>Cancel</button>
          <button className="primary-button" onClick={saveRole}>Save role</button>
        </div>
      </section>

      <aside className="role-aside">
        <article className="panel role-summary">
          <span className="eyebrow">Role health</span>
          <div className="health-ring"><strong>92</strong><small>Strong brief</small></div>
          <ul><li><span>✓</span>Clear outcome ownership</li><li><span>✓</span>Searchable skills added</li><li><span>✓</span>4 structured questions</li><li className="suggestion"><span>＋</span>Add salary range</li></ul>
        </article>
        <article className="panel mini-pipeline">
          <div className="panel-heading"><div><h2>Pipeline</h2><p>Customer Success Manager</p></div></div>
          <div><span>Discovered</span><b>36</b></div><div><span>Shortlisted</span><b>12</b></div><div><span>Voice screened</span><b>8</b></div><div><span>Qualified</span><b>6</b></div>
          <button className="primary-button full" onClick={() => onNavigate("talent")}>Find candidates →</button>
        </article>
      </aside>
    </div>
  );
}

function TalentSearch({ searching, searched, shortlisted, onSearch, onToggle, onCandidate, onCampaign }: {
  searching: boolean;
  searched: boolean;
  shortlisted: number[];
  onSearch: () => void;
  onToggle: (id: number) => void;
  onCandidate: (id: number) => void;
  onCampaign: () => void;
}) {
  return (
    <div className="stack-lg">
      <section className="search-builder panel">
        <div className="search-top">
          <div><span className="eyebrow">Searching for</span><h2>Customer Success Manager</h2><p>We translated your role brief into editable search criteria.</p></div>
          <DemoPill />
        </div>
        <div className="criteria-grid">
          <div className="filter-field"><span>Titles</span><div className="tag-input compact"><span>Customer Success Manager ×</span><span>CS Lead ×</span></div></div>
          <div className="filter-field"><span>Location</span><div className="select-like">Bengaluru, India <b>⌄</b></div></div>
          <div className="filter-field"><span>Experience</span><div className="select-like">5–8 years <b>⌄</b></div></div>
          <div className="filter-field"><span>Keywords</span><div className="tag-input compact"><span>B2B SaaS ×</span><span>Enterprise ×</span></div></div>
        </div>
        <div className="search-actions"><small><span>ⓘ</span> Demo results use the same normalized shape as the live Apollo adapter.</small><button className="primary-button" disabled={searching} onClick={onSearch}>{searching ? "Searching…" : "⌕ Search talent"}</button></div>
      </section>

      <div className="results-heading"><div><h2>{searching ? "Searching the demo index…" : "4 strong matches"}</h2><p>Ranked by title, skills, experience, and location fit.</p></div><div className="shortlist-chip">{shortlisted.length} shortlisted</div></div>

      {searching && <div className="candidate-grid">{[1,2,3,4].map((id) => <div className="candidate-card skeleton" key={id}><i /><i /><i /><i /></div>)}</div>}
      {searched && !searching && (
        <div className="candidate-grid">
          {candidates.map((candidate) => (
            <article className="candidate-card" key={candidate.id}>
              <div className="candidate-source"><StatusBadge tone="demo">Demo data</StatusBadge><span>{candidate.source}</span></div>
              <div className="candidate-header">
                <Avatar initials={candidate.initials} tone={candidate.tone} />
                <button className={shortlisted.includes(candidate.id) ? "saved" : ""} onClick={() => onToggle(candidate.id)} aria-label={`${shortlisted.includes(candidate.id) ? "Remove" : "Add"} ${candidate.name} ${shortlisted.includes(candidate.id) ? "from" : "to"} shortlist`}>{shortlisted.includes(candidate.id) ? "★" : "☆"}</button>
              </div>
              <button className="candidate-name" onClick={() => onCandidate(candidate.id)}>{candidate.name}</button>
              <p>{candidate.role}</p><small>{candidate.company}</small>
              <div className="candidate-meta"><span>⌖ {candidate.location}</span><span>◷ {candidate.experience}</span></div>
              <div className="skill-row">{candidate.skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
              <div className="match-row"><div><strong>{candidate.score}% match</strong><span><i style={{ width: `${candidate.score}%` }} /></span></div><button onClick={() => onCandidate(candidate.id)}>Why? →</button></div>
              <button className={shortlisted.includes(candidate.id) ? "secondary-button full" : "primary-button full"} onClick={() => onToggle(candidate.id)}>{shortlisted.includes(candidate.id) ? "✓ Shortlisted" : "＋ Add to shortlist"}</button>
            </article>
          ))}
        </div>
      )}
      {shortlisted.length > 0 && (
        <div className="selection-bar"><div className="avatar-stack">{candidates.filter((candidate) => shortlisted.includes(candidate.id)).slice(0, 2).map((candidate) => <Avatar key={candidate.id} initials={candidate.initials} tone={candidate.tone} />)}<span>{shortlisted.length}</span></div><p><strong>{shortlisted.length} candidate{shortlisted.length === 1 ? "" : "s"} selected</strong><small>Ready for a voice outreach campaign</small></p><button className="primary-button" onClick={onCampaign}>Create campaign →</button></div>
      )}
    </div>
  );
}

function Campaigns({ campaignState, onLaunch, onCandidate }: { campaignState: CampaignState; onLaunch: () => void; onCandidate: () => void }) {
  const isRunning = !["NOT_STARTED", "COMPLETED"].includes(campaignState);
  const statusLabels: Record<CampaignState, string> = {
    NOT_STARTED: "Ready to launch",
    INITIATED: "Call initiated",
    RINGING: "Candidate phone ringing",
    IN_PROGRESS: "Conversation in progress",
    COMPLETED: "Completed",
  };
  const activeStatus = statusLabels[campaignState];
  return (
    <div className="campaign-layout">
      <section className="stack-lg">
        <article className="panel campaign-hero">
          <div className="campaign-hero-top"><div><StatusBadge tone={campaignState === "COMPLETED" ? "green" : isRunning ? "amber" : "demo"}>{activeStatus}</StatusBadge><h2>CS Manager · August shortlist</h2><p>2 candidates · English · 4 screening questions</p></div><span className={`campaign-orb ${isRunning ? "calling" : campaignState.toLowerCase()}`}>◉</span></div>
          <div className="campaign-steps">
            {[
              ["1", "Review", "Candidates & questions"],
              ["2", "Voice outreach", campaignState === "NOT_STARTED" ? "Waiting to launch" : campaignState === "COMPLETED" ? "2 of 2 complete" : activeStatus],
              ["3", "Human review", campaignState === "COMPLETED" ? "Ready now" : "After conversations"],
            ].map((step, index) => <div className={(campaignState !== "NOT_STARTED" && index < 2) || (campaignState === "COMPLETED") ? "done" : index === 0 ? "current" : ""} key={step[0]}><span>{(campaignState !== "NOT_STARTED" && index === 0) || (campaignState === "COMPLETED" && index < 3) ? "✓" : step[0]}</span><p><strong>{step[1]}</strong><small>{step[2]}</small></p></div>)}
          </div>
          {campaignState === "NOT_STARTED" && <button className="primary-button large" onClick={onLaunch}>◉ Launch demo campaign</button>}
          {isRunning && <div className="calling-banner"><span className="voice-bars"><i /><i /><i /><i /></span><p><strong>{activeStatus}</strong><small>Lifecycle: NOT_STARTED → INITIATED → RINGING → IN_PROGRESS → COMPLETED</small></p></div>}
          {campaignState === "COMPLETED" && <button className="primary-button large" onClick={onCandidate}>Review completed conversation →</button>}
        </article>

        <article className="panel candidate-call-list">
          <div className="panel-heading"><div><h2>Candidates</h2><p>Each call uses the same verified Hunar request contract.</p></div><StatusBadge tone="demo">No real calls</StatusBadge></div>
          {[candidates[0], candidates[1]].map((candidate, index) => (
            <button className="call-row" key={candidate.id} onClick={index === 0 && campaignState === "COMPLETED" ? onCandidate : undefined}>
              <Avatar initials={candidate.initials} tone={candidate.tone} />
              <span className="call-person"><strong>{candidate.name}</strong><small>{candidate.role}</small></span>
              <span className="phone-mask">+91 ••••• ••{index ? "118" : "482"}</span>
              <StatusBadge tone={campaignState === "COMPLETED" ? (index ? "violet" : "green") : isRunning ? "amber" : "neutral"}>{campaignState === "COMPLETED" ? (index ? "Interested" : "Qualified") : isRunning ? campaignState.replace("_", " ") : "Queued"}</StatusBadge>
              <b>›</b>
            </button>
          ))}
        </article>
      </section>

      <aside className="stack-lg">
        <article className="panel provider-panel"><div className="provider-logo">H</div><div><span className="eyebrow">Voice provider</span><h3>Hunar Voice AI</h3></div><StatusBadge tone="green">Adapter ready</StatusBadge><ul><li><span>✓</span>`X-API-Key` server-side</li><li><span>✓</span>Signed callback verification</li><li><span>✓</span>Idempotent result updates</li></ul><small>Live calling stays locked until an authorized number is confirmed.</small></article>
        <article className="panel question-preview"><div className="panel-heading"><div><h2>Screening plan</h2><p>4 structured questions</p></div></div>{screeningQuestions.slice(0,3).map((question, index) => <div key={question}><span>{index + 1}</span><p>{question}</p></div>)}<button>View all questions</button></article>
      </aside>
    </div>
  );
}

function CandidateDetail({ candidateId, setNotice }: { candidateId: number; setNotice: (message: string) => void }) {
  const candidate = candidates.find((item) => item.id === candidateId) ?? candidates[0];
  const isAnanya = candidate.id === 1;
  const city = candidate.location.replace(", India", "");
  const recommendation = isAnanya
    ? "Ananya demonstrated direct ownership of enterprise portfolios, a structured churn-risk approach, and clear interest in the role. Notice period is the only timing consideration."
    : `${candidate.name}'s demo profile aligns strongly on role seniority, ${candidate.skills[0]}, and ${candidate.skills[1]}. Confirm availability and notice period during the next human interview.`;
  const portfolioAnswer = isAnanya
    ? "I currently own 42 enterprise accounts with roughly ₹18 crore in annual recurring revenue. I run onboarding, quarterly reviews, adoption planning, and renewals with each account."
    : `At ${candidate.company}, I own customer outcomes across ${candidate.skills[0].toLowerCase()} accounts, including adoption planning, stakeholder reviews, and renewals.`;
  const churnAnswer = isAnanya
    ? "I combine product usage, stakeholder engagement, support history, and business outcomes into a health score. For high-risk accounts, I agree a recovery plan with an executive sponsor and review it weekly."
    : `I monitor engagement, product usage, support history, and ${candidate.skills[2].toLowerCase()} signals, then agree a documented recovery plan with the customer team.`;
  const [decision, setDecision] = useState("Advance to interview");
  return (
    <div className="candidate-detail-layout">
      <section className="stack-lg">
        <article className="panel profile-card">
          <div className="candidate-source"><StatusBadge tone="demo">Demo data</StatusBadge><span>Simulated conversation · clearly labelled</span></div>
          <div className="profile-main"><Avatar initials={candidate.initials} tone={candidate.tone} /><div><h2>{candidate.name}</h2><p>{candidate.role} at {candidate.company}</p><span>⌖ {city} · ◷ {candidate.experience} · ◇ Open to opportunities</span></div><div className="profile-score"><strong>{candidate.score}</strong><span>Role match</span></div></div>
          <div className="profile-skills">{candidate.skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
        </article>

        <article className="panel recommendation-card">
          <div className="recommendation-title"><span className="spark">✦</span><div><span className="eyebrow">Application-generated recommendation</span><h2>Strong fit — advance to interview</h2></div><StatusBadge tone="green">High confidence</StatusBadge></div>
          <p>{recommendation}</p>
          <div className="signal-grid"><div><span>Role expertise</span><strong>Excellent</strong></div><div><span>Communication</span><strong>Strong</strong></div><div><span>Interest</span><strong>High</strong></div><div><span>Availability</span><strong>45 days</strong></div></div>
          <small>This recommendation is advisory. A recruiter makes the final decision.</small>
        </article>

        <article className="panel transcript-card">
          <div className="panel-heading"><div><h2>Voice conversation</h2><p>Demo transcript · 4m 38s · English</p></div><button>▶ Recording unavailable in demo</button></div>
          <div className="transcript">
            <div className="agent-line"><span>H</span><p><b>Hunar AI · 00:18</b>Tell me about the largest portfolio of enterprise accounts you have managed.</p></div>
            <div className="candidate-line"><Avatar initials={candidate.initials} tone={candidate.tone} /><p><b>{candidate.name} · 00:26</b>{portfolioAnswer}</p></div>
            <div className="agent-line"><span>H</span><p><b>Hunar AI · 01:12</b>How do you identify and respond to churn risk?</p></div>
            <div className="candidate-line"><Avatar initials={candidate.initials} tone={candidate.tone} /><p><b>{candidate.name} · 01:19</b>{churnAnswer}</p></div>
          </div>
          <button className="text-button">Show full demo transcript ↓</button>
        </article>
      </section>

      <aside className="stack-lg">
        <article className="panel answers-card"><div className="panel-heading"><div><h2>Structured answers</h2><p>Mapped from Hunar result schema</p></div></div><div><span>Enterprise portfolio</span><p>{isAnanya ? "42 accounts · ₹18 Cr ARR" : `${candidate.role} · ${candidate.company}`}</p></div><div><span>Churn-risk method</span><p>{isAnanya ? "Health score + recovery plan" : `${candidate.skills[1]} + recovery plan`}</p></div><div><span>Hybrid work</span><p>{isAnanya ? "Comfortable, 3 days/week" : "Confirm during interview"}</p></div><div><span>Notice period</span><p>{isAnanya ? "45 days, negotiable" : "Not captured in search data"}</p></div></article>
        <article className="panel review-card"><span className="eyebrow">Human decision</span><h2>Recruiter review</h2><p>Automated signals support this review; they do not make the hiring decision.</p><label>Decision<select value={decision} onChange={(event) => setDecision(event.target.value)}><option>Advance to interview</option><option>Hold for review</option><option>Do not proceed</option></select></label><label>Decision note<textarea placeholder="Add your reasoning…" defaultValue="Strong enterprise CS experience and clear ownership of outcomes." /></label><button className="primary-button full" onClick={() => setNotice(`Review saved: ${decision}`)}>Save human review</button></article>
        <article className="panel audit-card"><span>✓</span><div><strong>Transparent signal trail</strong><p>Provider result, application summary, and recruiter override remain separately attributed.</p></div></article>
      </aside>
    </div>
  );
}

function AttendanceBlueprint({ layer, setLayer }: { layer: "capture" | "verify" | "reconcile"; setLayer: (value: "capture" | "verify" | "reconcile") => void }) {
  const layerCopy = {
    capture: { title: "Capture at every site", body: "A shared RFID or biometric terminal records check-in and check-out. Feature-phone IVR is the fallback—no smartphone or app required.", bullets: ["Local offline queue", "Timestamp + site ID", "Feature-phone fallback"] },
    verify: { title: "Verify identity and location", body: "Employee PIN plus a rotating site code reduces proxy attendance. Biometrics are optional where privacy policy and operating conditions allow.", bullets: ["Rotating location code", "Supervisor exception call", "Buddy-punching alerts"] },
    reconcile: { title: "Reconcile centrally", body: "Events sync into one ledger. Rules flag missing punches; an LLM summarizes anomalies and prepares a review queue without altering source records.", bullets: ["Immutable audit trail", "Human-approved corrections", "Daily HR digest"] },
  }[layer];
  return (
    <div className="stack-xl attendance-page">
      <section className="attendance-hero">
        <div><span className="eyebrow">Architecture proposal · Assignment 3</span><h2>No smartphones.<br/><em>No attendance blind spots.</em></h2><p>A resilient, voice-first operating system for 1,000 employees across 100 distributed sites.</p><div className="hero-numbers"><span><strong>100</strong> sites</span><span><strong>1,000</strong> people</span><span><strong>2</strong> check events/day</span></div></div>
        <div className="site-map" aria-label="Illustrative network of attendance sites"><div className="central-node"><span>HR</span><small>Central ledger</small></div>{["Site 01","Site 14","Site 28","Site 43","Site 67","Site 82","Site 100"].map((site, index) => <span className={`site-node node-${index}`} key={site}><i />{site}</span>)}</div>
      </section>

      <section className="blueprint-switcher panel">
        <div className="blueprint-tabs" role="tablist">
          <button className={layer === "capture" ? "active" : ""} onClick={() => setLayer("capture")} role="tab"><span>01</span>Capture</button>
          <button className={layer === "verify" ? "active" : ""} onClick={() => setLayer("verify")} role="tab"><span>02</span>Verify</button>
          <button className={layer === "reconcile" ? "active" : ""} onClick={() => setLayer("reconcile")} role="tab"><span>03</span>Reconcile</button>
        </div>
        <div className="blueprint-content"><div><span className="blueprint-icon">{layer === "capture" ? "⌁" : layer === "verify" ? "◎" : "✦"}</span><h2>{layerCopy.title}</h2><p>{layerCopy.body}</p><ul>{layerCopy.bullets.map((bullet) => <li key={bullet}><span>✓</span>{bullet}</li>)}</ul></div><AttendanceFlow active={layer} /></div>
      </section>

      <section className="attendance-grid">
        <article className="panel principle-card"><span className="eyebrow">Identity & fraud controls</span><h2>Trust, but verify at the edge.</h2><div className="control-list"><div><span>01</span><p><strong>Something you know</strong>Employee PIN, never spoken to a supervisor.</p></div><div><span>02</span><p><strong>Somewhere you are</strong>Rotating code displayed only at the assigned site.</p></div><div><span>03</span><p><strong>Anomaly detection</strong>Impossible travel, duplicate punches, and repeated overrides.</p></div></div></article>
        <article className="panel exception-card"><div className="exception-head"><span>!</span><div><span className="eyebrow">Failure path</span><h2>Internet down at Site 43</h2></div></div><div className="timeline"><div><i>08:54</i><p><strong>Terminal stores encrypted events locally</strong>No employee queue or manual register.</p></div><div><i>09:10</i><p><strong>Supervisor receives IVR confirmation</strong>Only the exception count, not employee PINs.</p></div><div><i>11:32</i><p><strong>Connection returns; events sync</strong>Original timestamps are preserved.</p></div><div><i>17:00</i><p><strong>HR reviews one conflict</strong>Correction requires a reason and approval.</p></div></div></article>
      </section>

      <section className="rollout panel"><div><span className="eyebrow">Practical rollout</span><h2>Prove reliability before scaling.</h2></div><div className="rollout-steps"><div><span>Pilot</span><strong>5 sites · 2 weeks</strong><p>Measure match rate, queue time, and failure recovery.</p></div><b>→</b><div><span>Regional</span><strong>25 sites · 4 weeks</strong><p>Train supervisors and calibrate anomaly rules.</p></div><b>→</b><div><span>Network</span><strong>100 sites</strong><p>Daily reconciliation, monthly controls review.</p></div></div></section>
    </div>
  );
}

function AttendanceFlow({ active }: { active: "capture" | "verify" | "reconcile" }) {
  return <div className="attendance-flow"><div className={active === "capture" ? "active" : ""}><span>RFID</span><small>Shared terminal</small></div><b>→</b><div className={active === "verify" ? "active" : ""}><span>PIN + CODE</span><small>Identity check</small></div><b>→</b><div className={active === "reconcile" ? "active" : ""}><span>LEDGER</span><small>Central record</small></div><i className="fallback-line"/><div className="fallback"><span>☎</span><small>Feature-phone IVR fallback</small></div></div>;
}
