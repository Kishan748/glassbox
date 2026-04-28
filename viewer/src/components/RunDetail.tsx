import { useState } from "react";
import { Clipboard, Clock3, DollarSign, GitBranch, Hash, ListTree } from "lucide-react";

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
  const defaultEvent = allEvents.find((event) => event.event_type === "ai_call") ?? allEvents[0];
  const [selectedEventId, setSelectedEventId] = useState<string | undefined>();
  const selectedEvent =
    allEvents.find((event) => event.id === selectedEventId) ?? defaultEvent ?? null;
  const selectedAiEvent = selectedEvent?.event_type === "ai_call" ? selectedEvent : null;
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
              <EventTreeItem
                key={event.id}
                event={event}
                selectedEventId={selectedEvent?.id}
                onSelectEvent={setSelectedEventId}
              />
            ))}
          </ol>
        )}
      </section>

      <div className="detail-grid">
        {selectedEvent && <EventDetail event={selectedEvent} run={run} aiCall={selectedAiCall} />}
        {selectedAiCall && (
          <AiCallDetail aiCall={selectedAiCall} durationMs={selectedAiEvent?.duration_ms ?? null} />
        )}
        {failedEvent && <ErrorDetail event={failedEvent} runId={run.id} />}
      </div>
    </section>
  );
}

function EventDetail({
  event,
  run,
  aiCall
}: {
  event: EventNode;
  run: RunSummary;
  aiCall?: AiCall | null;
}) {
  const source = event.file_path
    ? `${event.file_path}${event.line_number === null ? "" : `:${event.line_number}`}`
    : "Not captured";
  const data = JSON.stringify(event.data ?? {}, null, 2);
  const debugPrompt = buildDebugPrompt({ event, run, source, data, aiCall });

  return (
    <section className="detail-panel">
      <div className="copy-row event-detail-title">
        <div className="section-title">
          <ListTree aria-hidden="true" size={18} />
          <h3>Event detail</h3>
        </div>
        <button
          type="button"
          onClick={() => copyText(debugPrompt)}
          aria-label="Copy debug prompt"
        >
          <Clipboard aria-hidden="true" size={16} />
          Copy debug prompt
        </button>
      </div>
      <dl className="meta-grid">
        <div>
          <dt>Name</dt>
          <dd>{event.name}</dd>
        </div>
        <div>
          <dt>Type</dt>
          <dd>{labelForEvent(event.event_type)}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{event.status}</dd>
        </div>
        <div>
          <dt>Duration</dt>
          <dd>{formatDuration(event.duration_ms)}</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd>{source}</dd>
        </div>
      </dl>
      {event.error_message && <pre className="code-block error-message">{event.error_message}</pre>}
      <h4>Captured data</h4>
      <pre className="code-block">{data}</pre>
    </section>
  );
}

function buildDebugPrompt({
  event,
  run,
  source,
  data,
  aiCall
}: {
  event: EventNode;
  run: RunSummary;
  source: string;
  data: string;
  aiCall?: AiCall | null;
}): string {
  const lines = [
    "Debug this Glassbox event.",
    "",
    `Run: ${run.id}`,
    `Project: ${run.project_name}`,
    `Run status: ${run.status}`,
    `Event: ${event.name}`,
    `Event type: ${labelForEvent(event.event_type)}`,
    `Event status: ${event.status}`,
    `Duration: ${formatDuration(event.duration_ms)}`,
    `Source: ${source}`,
  ];

  if (event.error_message) {
    lines.push("", "Error:", event.error_message);
  }

  lines.push("", "Captured data:", data);

  if (aiCall) {
    lines.push(
      "",
      "AI call:",
      `Provider: ${aiCall.provider}`,
      `Model: ${aiCall.model}`,
      `Prompt messages: ${JSON.stringify(aiCall.messages, null, 2)}`,
      `Response: ${aiCall.response_text ?? "No response text captured."}`,
    );
  }

  return lines.join("\n");
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

function EventTreeItem({
  event,
  selectedEventId,
  onSelectEvent
}: {
  event: EventNode;
  selectedEventId: string | undefined;
  onSelectEvent: (eventId: string) => void;
}) {
  const eventLabel = labelForEvent(event.event_type);
  const duration = formatDuration(event.duration_ms);

  return (
    <li>
      <button
        aria-pressed={event.id === selectedEventId}
        className={`event-row ${event.status} ${event.id === selectedEventId ? "selected" : ""}`}
        onClick={() => onSelectEvent(event.id)}
        type="button"
        aria-label={`${eventLabel} ${event.name} ${event.status} ${duration}`}
      >
        <span className="event-type">{eventLabel}</span>
        <strong>{event.name}</strong>
        <span>{event.status}</span>
        <span>{duration}</span>
      </button>
      {event.children.length > 0 && (
        <ol>
          {event.children.map((child) => (
            <EventTreeItem
              key={child.id}
              event={child}
              selectedEventId={selectedEventId}
              onSelectEvent={onSelectEvent}
            />
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

function copyText(text: string) {
  return navigator.clipboard?.writeText(text);
}
