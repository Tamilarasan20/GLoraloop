"use client";

import { Database, Download, FileText, ImageIcon, Loader2, Palette, Play, Save } from "lucide-react";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";

const StudioCanvas = dynamic(() => import("./studio-canvas"), { ssr: false });

type TemplateLayer = {
  type: string;
  content?: string | null;
  src?: string | null;
  color?: string | null;
  font_family?: string | null;
  font_size?: number | null;
  x: number;
  y: number;
  width?: number | null;
  height?: number | null;
  z_index: number;
};

type TemplateReadyData = {
  canvas_width: number;
  canvas_height: number;
  layout: string;
  headline: string;
  subheadline: string;
  background_image?: string | null;
  cta: string;
  layers: TemplateLayer[];
};

type BrandAnalysisResult = {
  brand_kit: {
    brand_name: string;
    summary: string;
    audience: string;
    tone: string[];
    colors: string[];
    font_style: string;
    logo_url?: string | null;
    images: string[];
    campaign_angles: string[];
  };
  campaign_concepts: Array<{
    name: string;
    objective: string;
    headline: string;
    subheadline: string;
    cta: string;
    channels: string[];
  }>;
  template_ready_data: TemplateReadyData[];
  strategy_pdf_url?: string | null;
  strategy_document?: {
    title: string;
    business_profile: {
      overview: string;
      products_or_services: string[];
      key_selling_points: string[];
      retail_or_distribution?: string[];
      target_audience: string[];
      founder_story?: string | null;
      marketing_goals?: string[];
      website?: string;
    };
    social_strategy: {
      priority_platforms?: Array<{ platform: string; priority: number; role: string; posting_cadence: string }>;
      content_pillars: string[];
      messaging_hierarchy?: string[];
      quick_wins: string[];
    };
    market_research: {
      market_opportunity: string[];
      trend_tailwinds?: string[];
      competitive_landscape?: string[];
      key_risks: string[];
      social_platform_insights?: string[];
      target_audiences_on_social?: string[];
    };
    brand_guidelines: {
      brand_personality: string[];
      color_palette: Record<string, string>;
      typography?: Record<string, string>;
      design_style?: string[];
      logo_url?: string | null;
      social_content_principles: string[];
    };
    extracted_assets: Array<{ type: string; url: string; alt?: string | null; width?: number | null; height?: number | null; notes?: string | null }>;
  } | null;
};

type KnowledgeBaseResponse = {
  id: string;
  business_name: string;
  website: string;
};

type JobResponse = {
  id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  progress: number;
  stage: string;
  error?: string | null;
  result?: BrandAnalysisResult | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [url, setUrl] = useState("https://example.com");
  const [job, setJob] = useState<JobResponse | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState(0);
  const [isStarting, setIsStarting] = useState(false);
  const [canvasExporter, setCanvasExporter] = useState<(() => void) | null>(null);
  const [activeKbTab, setActiveKbTab] = useState<"Documents" | "Visual Assets" | "Brand Guidelines">("Documents");
  const [savedKnowledgeBase, setSavedKnowledgeBase] = useState<KnowledgeBaseResponse | null>(null);
  const [isSavingKnowledgeBase, setIsSavingKnowledgeBase] = useState(false);

  const result = job?.result ?? null;
  const template = result?.template_ready_data[selectedTemplate] ?? null;
  const strategyPdfUrl = result?.strategy_pdf_url
    ? result.strategy_pdf_url.startsWith("/")
      ? `${API_BASE}${result.strategy_pdf_url}`
      : result.strategy_pdf_url
    : null;

  const statusLabel = useMemo(() => {
    if (!job) return "Ready";
    return `${job.stage} · ${job.progress}%`;
  }, [job]);

  async function startAnalysis() {
    setIsStarting(true);
    setJob(null);
    setSavedKnowledgeBase(null);
    try {
      const response = await fetch(`${API_BASE}/v1/brand-kits/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
      const created = (await response.json()) as JobResponse;
      setJob(created);
      pollJob(created.id);
    } finally {
      setIsStarting(false);
    }
  }

  async function pollJob(jobId: string) {
    let keepPolling = true;
    while (keepPolling) {
      const response = await fetch(`${API_BASE}/v1/jobs/${jobId}`);
      const nextJob = (await response.json()) as JobResponse;
      setJob(nextJob);
      keepPolling = nextJob.status === "queued" || nextJob.status === "running";
      if (keepPolling) await new Promise((resolve) => setTimeout(resolve, 1200));
    }
  }

  async function saveProject() {
    if (!result) return;
    await fetch(`${API_BASE}/v1/projects`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer founder@laraloop.local"
      },
      body: JSON.stringify({
        name: result.brand_kit.brand_name,
        source_url: url,
        brand_kit: result.brand_kit,
        templates: result.template_ready_data
      })
    });
  }

  async function saveKnowledgeBase() {
    if (!result) return;
    setIsSavingKnowledgeBase(true);
    try {
      const response = await fetch(`${API_BASE}/v1/knowledge-bases`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer founder@laraloop.local"
        },
        body: JSON.stringify({
          source_url: url,
          analysis: result
        })
      });
      const saved = (await response.json()) as KnowledgeBaseResponse;
      setSavedKnowledgeBase(saved);
    } finally {
      setIsSavingKnowledgeBase(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="toolbar">
        <div>
          <p className="eyebrow">Laraloop Brand DNA</p>
          <h1>Campaign Generator</h1>
        </div>
        <div className="url-form">
          <input value={url} onChange={(event) => setUrl(event.target.value)} aria-label="Website URL" />
          <button onClick={startAnalysis} disabled={isStarting}>
            {isStarting ? <Loader2 size={18} className="spin" /> : <Play size={18} />}
            Generate
          </button>
        </div>
      </section>

      <section className="workspace">
        <aside className="panel">
          <div className="status">
            <span>{statusLabel}</span>
            <div><i style={{ width: `${job?.progress ?? 0}%` }} /></div>
          </div>

          {result && (
            <>
              <h2>{result.brand_kit.brand_name}</h2>
              <p>{result.brand_kit.summary}</p>
              <div className="swatches">
                {result.brand_kit.colors.map((color) => (
                  <span key={color} title={color} style={{ background: color }} />
                ))}
              </div>
              <div className="chips">
                {result.brand_kit.tone.map((tone) => (
                  <span key={tone}>{tone}</span>
                ))}
              </div>
              <h3>Variations</h3>
              {result.template_ready_data.map((item, index) => (
                <button
                  className={selectedTemplate === index ? "variation active" : "variation"}
                  key={item.headline}
                  onClick={() => setSelectedTemplate(index)}
                >
                  {item.headline}
                </button>
              ))}
            </>
          )}

          {job?.error && <p className="error">{job.error}</p>}
        </aside>

        <section className="canvas-wrap">
          {template ? <StudioCanvas template={template} onExporterReady={setCanvasExporter} /> : <div className="empty-canvas">Paste a URL to generate campaign-ready templates.</div>}
        </section>

        <aside className="panel">
          <h2>Actions</h2>
          <button className="wide" onClick={() => canvasExporter?.()} disabled={!canvasExporter}>
            <Download size={18} />
            Export PNG
          </button>
          <button className="wide ghost" onClick={saveProject} disabled={!result}>
            <Save size={18} />
            Save Project
          </button>
          <button className="wide ghost" onClick={saveKnowledgeBase} disabled={!result || isSavingKnowledgeBase}>
            {isSavingKnowledgeBase ? <Loader2 size={18} className="spin" /> : <Database size={18} />}
            {savedKnowledgeBase ? "Knowledge Base Saved" : "Save Knowledge Base"}
          </button>
          {savedKnowledgeBase && <p className="saved-note">KB ID: {savedKnowledgeBase.id.slice(0, 8)}</p>}
          {strategyPdfUrl && (
            <a className="download-link" href={strategyPdfUrl} target="_blank" rel="noreferrer">
              Open Strategy PDF
            </a>
          )}
          {result && (
            <>
              <h3>Campaigns</h3>
              {result.campaign_concepts.map((concept) => (
                <article className="concept" key={concept.name}>
                  <strong>{concept.name}</strong>
                  <span>{concept.objective}</span>
                  <p>{concept.subheadline}</p>
                </article>
              ))}
              {result.strategy_document && (
                <>
                  <h3>Knowledge Base</h3>
                  <div className="kb-tabs">
                    {(["Documents", "Visual Assets", "Brand Guidelines"] as const).map((tab) => (
                      <button
                        key={tab}
                        className={activeKbTab === tab ? "kb-tab active" : "kb-tab"}
                        onClick={() => setActiveKbTab(tab)}
                      >
                        {tab === "Documents" && <FileText size={14} />}
                        {tab === "Visual Assets" && <ImageIcon size={14} />}
                        {tab === "Brand Guidelines" && <Palette size={14} />}
                        {tab}
                      </button>
                    ))}
                  </div>
                  <KnowledgeBasePreview result={result} activeTab={activeKbTab} />
                </>
              )}
            </>
          )}
        </aside>
      </section>
    </main>
  );
}

function KnowledgeBasePreview({
  result,
  activeTab
}: {
  result: BrandAnalysisResult;
  activeTab: "Documents" | "Visual Assets" | "Brand Guidelines";
}) {
  const doc = result.strategy_document;
  if (!doc) return null;

  if (activeTab === "Documents") {
    return (
      <div className="kb-section">
        <DocumentCard title="Business Profile" lines={[
          doc.business_profile.overview,
          ...doc.business_profile.key_selling_points.slice(0, 3)
        ]} />
        <DocumentCard title="Social Strategy" lines={[
          ...doc.social_strategy.content_pillars.slice(0, 4),
          ...doc.social_strategy.quick_wins.slice(0, 2)
        ]} />
        <DocumentCard title="Market Research" lines={[
          ...doc.market_research.market_opportunity.slice(0, 3),
          ...doc.market_research.key_risks.slice(0, 2)
        ]} />
      </div>
    );
  }

  if (activeTab === "Visual Assets") {
    const assets = doc.extracted_assets.filter((asset) => asset.url);
    return (
      <div className="kb-section">
        <p className="kb-muted">{assets.length} scraped assets available for future campaigns.</p>
        <div className="asset-grid">
          {assets.slice(0, 12).map((asset, index) => (
            <a
              key={`${asset.url}-${index}`}
              className="asset-tile"
              href={asset.url.startsWith("/") ? `${API_BASE}${asset.url}` : asset.url}
              target="_blank"
              rel="noreferrer"
              title={asset.alt ?? asset.notes ?? asset.type}
            >
              {asset.type === "screenshot" || asset.type === "image" || asset.type === "logo" ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={asset.url.startsWith("/") ? `${API_BASE}${asset.url}` : asset.url} alt={asset.alt ?? asset.type} />
              ) : (
                <ImageIcon size={18} />
              )}
              <span>{asset.type}</span>
            </a>
          ))}
        </div>
      </div>
    );
  }

  const guidelines = doc.brand_guidelines;
  return (
    <div className="kb-section">
      <DocumentCard title="Personality" lines={guidelines.brand_personality} />
      <div className="guideline-block">
        <strong>Color Palette</strong>
        <div className="guideline-swatches">
          {Object.entries(guidelines.color_palette).map(([role, color]) => (
            <span key={`${role}-${color}`}>
              <i style={{ background: color }} />
              {role}: {color}
            </span>
          ))}
        </div>
      </div>
      <DocumentCard title="Content Principles" lines={guidelines.social_content_principles.slice(0, 5)} />
    </div>
  );
}

function DocumentCard({ title, lines }: { title: string; lines: string[] }) {
  return (
    <article className="kb-card">
      <strong>{title}</strong>
      <ul>
        {lines.filter(Boolean).slice(0, 6).map((line, index) => (
          <li key={`${title}-${index}`}>{line}</li>
        ))}
      </ul>
    </article>
  );
}
