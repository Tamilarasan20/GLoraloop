"use client";

import { Download, Loader2, Play, Save } from "lucide-react";
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
      target_audience: string[];
    };
    social_strategy: {
      content_pillars: string[];
      quick_wins: string[];
    };
    market_research: {
      market_opportunity: string[];
      key_risks: string[];
    };
    brand_guidelines: {
      brand_personality: string[];
      color_palette: Record<string, string>;
      social_content_principles: string[];
    };
    extracted_assets: Array<{ type: string; url: string; alt?: string | null }>;
  } | null;
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
                  <h3>Strategy Document</h3>
                  <article className="concept">
                    <strong>Business Profile</strong>
                    <p>{result.strategy_document.business_profile.overview}</p>
                  </article>
                  <article className="concept">
                    <strong>Social Strategy</strong>
                    <p>{result.strategy_document.social_strategy.content_pillars.slice(0, 3).join(", ")}</p>
                  </article>
                  <article className="concept">
                    <strong>Extracted Assets</strong>
                    <p>{result.strategy_document.extracted_assets.length} website assets found.</p>
                  </article>
                </>
              )}
            </>
          )}
        </aside>
      </section>
    </main>
  );
}
