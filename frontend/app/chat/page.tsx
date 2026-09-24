"use client";

import { ArrowUp, ArrowUpRight, Check, MoreHorizontal, Pause, Search, TrendingUp } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";

import "./chat.css";

type Delta = { label: string; tone: "positive" | "negative" | "neutral"; arrow?: boolean };

type Kpi = { label: string; value: string; delta?: Delta };

type SummaryCard = {
  kind: "summary";
  kpis: Kpi[];
  bars: number[];
  highlightIndex: number;
};

type Creative = {
  id: string;
  name: string;
  detail: string;
  badge: string;
  tone: "success" | "critical";
  action: "scale" | "retire";
};

type ActionsCard = { kind: "actions"; creatives: Creative[] };

type Block = { kind: "text"; text: string } | SummaryCard | ActionsCard;

type Message = {
  id: string;
  author: "user" | "max";
  time: string;
  blocks: Block[];
};

const USER_NAME = "Emma";

const WEEKLY_SUMMARY: SummaryCard = {
  kind: "summary",
  kpis: [
    { label: "Spend", value: "$9,340", delta: { label: "+4%", tone: "neutral" } },
    { label: "ROAS", value: "2.7x", delta: { label: "from 2.3x", tone: "positive", arrow: true } },
    { label: "CPA", value: "$16.80", delta: { label: "−9%", tone: "positive" } },
    { label: "Creatives tested", value: "14" }
  ],
  bars: [42, 58, 46, 62, 74, 68, 92],
  highlightIndex: 6
};

const RECOMMENDATIONS: ActionsCard = {
  kind: "actions",
  creatives: [
    {
      id: "c-1",
      name: "Summer Hydration UGC",
      detail: "3.4x ROAS · $12.10 CPA",
      badge: "Top performer",
      tone: "success",
      action: "scale"
    },
    {
      id: "c-2",
      name: "Static Product Grid",
      detail: "1.1x ROAS · $31.40 CPA",
      badge: "Below target",
      tone: "critical",
      action: "retire"
    },
    {
      id: "c-3",
      name: "Founder Story Cut B",
      detail: "1.3x ROAS · $27.90 CPA",
      badge: "Below target",
      tone: "critical",
      action: "retire"
    }
  ]
};

const SEED_MESSAGES: Message[] = [
  {
    id: "m-1",
    author: "user",
    time: "4:30 PM",
    blocks: [{ kind: "text", text: "How did we do this week?" }]
  },
  {
    id: "m-2",
    author: "max",
    time: "4:30 PM",
    blocks: [
      { kind: "text", text: "Strong week — here's the summary:" },
      WEEKLY_SUMMARY,
      { kind: "text", text: "Your top performer earned more room — I'd scale it and retire the bottom two:" },
      RECOMMENDATIONS
    ]
  }
];

const SUGGESTIONS = [
  "Which creative should we scale?",
  "Compare this week to last week",
  "Draft next week's testing plan",
  "Where is spend leaking?"
];

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function buildReply(prompt: string): Block[] {
  const lower = prompt.toLowerCase();

  if (lower.includes("scale")) {
    return [
      { kind: "text", text: "Summer Hydration UGC is the clear winner. I'd raise its budget by 25% and hold for 3 days:" },
      { kind: "actions", creatives: [RECOMMENDATIONS.creatives[0]] }
    ];
  }

  if (lower.includes("compare") || lower.includes("last week")) {
    return [
      { kind: "text", text: "Week over week, efficiency improved while spend stayed flat:" },
      WEEKLY_SUMMARY
    ];
  }

  if (lower.includes("plan") || lower.includes("test")) {
    return [
      {
        kind: "text",
        text: "For next week I'd run 6 new creatives: 3 UGC hooks off the hydration angle, 2 short founder cuts, and 1 offer-led static. I can draft the briefs when you're ready."
      }
    ];
  }

  return [
    {
      kind: "text",
      text: "Got it. I'm looking at the last 7 days across all active campaigns — give me a second and I'll pull the numbers together."
    }
  ];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(SEED_MESSAGES);
  const [draft, setDraft] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [resolved, setResolved] = useState<Record<string, "scaled" | "retired" | "kept">>({});
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const canSend = draft.trim().length > 0 && !isTyping;

  useEffect(() => {
    const node = scrollRef.current;
    if (node) {
      node.scrollTo({ top: node.scrollHeight, behavior: "smooth" });
    }
  }, [messages, isTyping]);

  useEffect(() => {
    const node = textareaRef.current;
    if (!node) return;
    node.style.height = "auto";
    node.style.height = `${Math.min(node.scrollHeight, 160)}px`;
  }, [draft]);

  const dayLabel = useMemo(() => `Today · ${SEED_MESSAGES[0].time}`, []);

  function send(text: string) {
    const clean = text.trim();
    if (!clean || isTyping) return;

    const now = new Date();
    const userMessage: Message = {
      id: `u-${now.getTime()}`,
      author: "user",
      time: formatTime(now),
      blocks: [{ kind: "text", text: clean }]
    };

    setMessages((prev) => [...prev, userMessage]);
    setDraft("");
    setIsTyping(true);

    window.setTimeout(() => {
      const replyAt = new Date();
      setMessages((prev) => [
        ...prev,
        { id: `a-${replyAt.getTime()}`, author: "max", time: formatTime(replyAt), blocks: buildReply(clean) }
      ]);
      setIsTyping(false);
    }, 900);
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send(draft);
    }
  }

  function resolve(creative: Creative, outcome: "scaled" | "retired" | "kept") {
    setResolved((prev) => ({ ...prev, [creative.id]: outcome }));
    const verb = outcome === "scaled" ? "Scaling" : outcome === "retired" ? "Retiring" : "Keeping";
    const at = new Date();
    setMessages((prev) => [
      ...prev,
      {
        id: `s-${at.getTime()}`,
        author: "max",
        time: formatTime(at),
        blocks: [{ kind: "text", text: `${verb} ${creative.name}. I'll report back once the change has 24 hours of data.` }]
      }
    ]);
  }

  return (
    <main className="chat-root">
      <header className="chat-header">
        <div className="chat-avatar is-max" aria-hidden="true">
          <MaxFace size={28} />
        </div>
        <div className="chat-header-title">
          <strong>Max</strong>
          <span>Online · Growth agent</span>
        </div>
        <div className="chat-header-actions">
          <button className="chat-icon-button" type="button" aria-label="Search conversation">
            <Search size={18} />
          </button>
          <button className="chat-icon-button" type="button" aria-label="More actions">
            <MoreHorizontal size={18} />
          </button>
        </div>
      </header>

      <div className="chat-scroll" ref={scrollRef} role="log" aria-live="polite" aria-label="Conversation with Max">
        <div className="chat-thread">
          <p className="chat-day-divider">{dayLabel}</p>

          {messages.map((message) =>
            message.author === "user" ? (
              <UserRow key={message.id} message={message} />
            ) : (
              <MaxRow key={message.id} message={message} resolved={resolved} onResolve={resolve} />
            )
          )}

          {isTyping ? (
            <div className="chat-row is-assistant">
              <div className="chat-avatar is-max" aria-hidden="true">
                <MaxFace size={28} />
              </div>
              <div className="chat-row-body">
                <div className="chat-typing" aria-label="Max is typing">
                  <i />
                  <i />
                  <i />
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      <div className="chat-composer-wrap">
        <div className="chat-suggestions" aria-label="Suggested prompts">
          {SUGGESTIONS.map((suggestion) => (
            <button key={suggestion} className="chat-suggestion" type="button" onClick={() => send(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
        <form
          className="chat-composer"
          onSubmit={(event) => {
            event.preventDefault();
            send(draft);
          }}
        >
          <label className="chat-composer-field">
            <span className="chat-sr-only">Message Max</span>
            <textarea
              ref={textareaRef}
              rows={1}
              placeholder="Message Max…"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={onKeyDown}
            />
          </label>
          <button className="chat-composer-send" type="submit" aria-label="Send message" disabled={!canSend}>
            <ArrowUp size={30} strokeWidth={2.5} />
          </button>
        </form>
        <p className="chat-composer-hint">Enter to send · Shift + Enter for a new line</p>
      </div>
    </main>
  );
}

function UserRow({ message }: { message: Message }) {
  return (
    <div className="chat-row is-user">
      <div className="chat-row-body">
        {message.blocks.map((block, index) =>
          block.kind === "text" ? (
            <p key={index} className="chat-bubble is-user">
              {block.text}
            </p>
          ) : null
        )}
        <span className="chat-meta">
          {message.time} · {USER_NAME}
        </span>
      </div>
      <div className="chat-avatar is-user" aria-hidden="true">
        {USER_NAME.charAt(0)}
      </div>
    </div>
  );
}

function MaxRow({
  message,
  resolved,
  onResolve
}: {
  message: Message;
  resolved: Record<string, "scaled" | "retired" | "kept">;
  onResolve: (creative: Creative, outcome: "scaled" | "retired" | "kept") => void;
}) {
  return (
    <div className="chat-row is-assistant">
      <div className="chat-avatar is-max" aria-hidden="true">
        <MaxFace size={28} />
      </div>
      <div className="chat-row-body">
        <div>
          <p className="chat-sender">Max</p>
          {message.blocks[0]?.kind === "text" ? (
            <p className="chat-bubble is-assistant">{message.blocks[0].text}</p>
          ) : null}
        </div>
        {message.blocks.slice(message.blocks[0]?.kind === "text" ? 1 : 0).map((block, index) => {
          if (block.kind === "text") {
            return (
              <p key={index} className="chat-bubble is-assistant">
                {block.text}
              </p>
            );
          }
          if (block.kind === "summary") {
            return <SummaryCardView key={index} card={block} />;
          }
          return <ActionsCardView key={index} card={block} resolved={resolved} onResolve={onResolve} />;
        })}
      </div>
    </div>
  );
}

function SummaryCardView({ card }: { card: SummaryCard }) {
  const max = Math.max(...card.bars);
  return (
    <section className="chat-card" aria-label="Weekly performance summary">
      <dl className="chat-kpi-grid">
        {card.kpis.map((kpi) => (
          <div key={kpi.label} className="chat-kpi">
            <dt>{kpi.label}</dt>
            <dd>
              <span className="chat-kpi-value">{kpi.value}</span>
              {kpi.delta ? (
                <span className={`chat-kpi-delta is-${kpi.delta.tone}`}>
                  {kpi.delta.arrow ? <ArrowUpRight size={16} aria-hidden="true" /> : null}
                  {kpi.delta.label}
                </span>
              ) : null}
            </dd>
          </div>
        ))}
      </dl>
      <div className="chat-bars" role="img" aria-label="Daily ROAS for the last 7 days, peaking on the final day">
        {card.bars.map((value, index) => (
          <span
            key={index}
            className={`chat-bar${index === card.highlightIndex ? " is-highlight" : ""}`}
            style={{ height: `${Math.round((value / max) * 100)}%` }}
          />
        ))}
      </div>
    </section>
  );
}

function ActionsCardView({
  card,
  resolved,
  onResolve
}: {
  card: ActionsCard;
  resolved: Record<string, "scaled" | "retired" | "kept">;
  onResolve: (creative: Creative, outcome: "scaled" | "retired" | "kept") => void;
}) {
  return (
    <div className="chat-actions">
      {card.creatives.map((creative) => {
        const state = resolved[creative.id];
        return (
          <article key={creative.id} className="chat-action-card">
            <div className="chat-action-head">
              <span className="chat-action-thumb" aria-hidden="true" />
              <div className="chat-action-title">
                <strong>{creative.name}</strong>
                <span>{creative.detail}</span>
              </div>
              <span className={`chat-badge is-${creative.tone}`}>{creative.badge}</span>
            </div>
            <div className="chat-action-buttons">
              {state ? (
                <button className="chat-action-button" type="button" disabled>
                  <Check size={14} aria-hidden="true" />
                  {state === "scaled" ? "Scaled" : state === "retired" ? "Retired" : "Kept"}
                </button>
              ) : creative.action === "scale" ? (
                <>
                  <button className="chat-action-button is-primary" type="button" onClick={() => onResolve(creative, "scaled")}>
                    <TrendingUp size={14} aria-hidden="true" />
                    Scale +25%
                  </button>
                  <button className="chat-action-button" type="button" onClick={() => onResolve(creative, "kept")}>
                    Keep as is
                  </button>
                </>
              ) : (
                <>
                  <button className="chat-action-button is-primary" type="button" onClick={() => onResolve(creative, "retired")}>
                    <Pause size={14} aria-hidden="true" />
                    Retire
                  </button>
                  <button className="chat-action-button" type="button" onClick={() => onResolve(creative, "kept")}>
                    Keep running
                  </button>
                </>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}

function MaxFace({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <path d="M6 12 L9 8 L12 12" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 12 L19 8 L22 12" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M11 17 L14 20 L17 17" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
