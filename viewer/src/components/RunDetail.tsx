import { Clock3, DollarSign, GitBranch, Hash } from "lucide-react";

import type { AiCall, EventNode, RunSummary } from "../api/types";
import { countEvents, formatCost, formatDuration } from "../utils/format";
import { AiCallDetail } from "./AiCallDetail";
import { ErrorDetail } from "./ErrorDetail";

interface RunDetailProps {
  run: RunSummary;
  events: EventNode[];
  aiCalls?: AiCall[];
}

export function RunDetail({ run, events, aiCalls = [] }: RunDetailProps) {
  const allEvents = flattenEvents(events);
  const selectedAiEvent = allEvents.find((event) => event.event_type === "ai_call");
  const selectedAiCall =
    selectedAiEvent?.ai_call ?? aiCalls.find((aiCall) => aiCall.event_id === selectedAiEvent?.id);
  const failedEvent = allEvents.find((event) => event.status === "failed" && event.error_message);

  return (
    <section className="run-detail">
      <header className="run-detail-header">
        <div>
          <p className="eyebrow">{run.id}</p>
          <h1>{run.project_name}</h1>
        </div>
        <span className={`status-pill ${run.status}`}>{run.status}</span>
      </header>

      <div className="metric-grid">
        <Metric icon={<Clock3 size={18} />} label="Duration" value={formatDuration(run.duration_ms)} />
        <Metric icon={<DollarSign size={18} />} label="Cost" value={formatCost(run.total_cost_usd)} />
        <Metric icon={<Hash size={18} />} label="Events" value={`${countEvents(events)} steps`} />
        <Metric icon={<GitBranch size={18} />} label="Runtime" value={run.runtime_language} />
      </div>

      <section className="steps-panel">
        <div className="section-title">
          <h2>Steps</h2>
        </div>
        {events.length === 0 ? (
          <p className="muted empty-state">No steps captured for this run.</p>
        ) : (
          <ol className="event-tree">
            {events.map((event) => (
              <EventTreeItem key={event.id} event={event} />
            ))}
          </ol>
        )}
      </section>

      <div className="detail-grid">
        {selectedAiCall && (
          <AiCallDetail aiCall={selectedAiCall} durationMs={selectedAiEvent?.duration_ms ?? null} />
        )}
        {failedEvent && <ErrorDetail event={failedEvent} runId={run.id} />}
      </div>
    </section>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="metric">
      <span className="metric-icon">{icon}</span>
      <span>
        <span className="metric-label">{label}</span>
        <strong>{value}</strong>
      </span>
    </div>
  );
}

function EventTreeItem({ event }: { event: EventNode }) {
  return (
    <li>
      <div className={`event-row ${event.status}`}>
        <span className="event-type">{labelForEvent(event.event_type)}</span>
        <strong>{event.name}</strong>
        <span>{event.status}</span>
        <span>{formatDuration(event.duration_ms)}</span>
      </div>
      {event.children.length > 0 && (
        <ol>
          {event.children.map((child) => (
            <EventTreeItem key={child.id} event={child} />
          ))}
        </ol>
      )}
    </li>
  );
}

function labelForEvent(eventType: string): string {
  if (eventType === "ai_call") {
    return "AI call";
  }
  if (eventType === "log") {
    return "Log";
  }
  return "Function";
}

function flattenEvents(events: EventNode[]): EventNode[] {
  return events.flatMap((event) => [event, ...flattenEvents(event.children)]);
}
