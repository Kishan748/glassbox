import { Clipboard, TriangleAlert } from "lucide-react";

import type { EventNode } from "../api/types";

interface ErrorDetailProps {
  event: EventNode;
  runId: string;
}

export function ErrorDetail({ event, runId }: ErrorDetailProps) {
  const location = formatLocation(event);
  const prompt = buildDebuggingPrompt(event, runId);

  return (
    <section className="detail-panel error-panel">
      <div className="section-title">
        <TriangleAlert aria-hidden="true" size={18} />
        <h3>Error</h3>
      </div>
      <dl className="meta-grid">
        <div>
          <dt>Step</dt>
          <dd>{event.name}</dd>
        </div>
        <div>
          <dt>Location</dt>
          <dd>{location}</dd>
        </div>
      </dl>
      <pre className="code-block error-message">{event.error_message}</pre>
      <button
        className="primary-action"
        type="button"
        onClick={() => navigator.clipboard?.writeText(prompt)}
        aria-label="Copy debugging prompt"
      >
        <Clipboard aria-hidden="true" size={16} />
        Copy debugging prompt
      </button>
    </section>
  );
}

export function buildDebuggingPrompt(event: EventNode, runId: string): string {
  return [
    "Help me debug this Glassbox run.",
    `Run ID: ${runId}`,
    `Step: ${event.name}`,
    `Status: ${event.status}`,
    `Location: ${formatLocation(event)}`,
    `Error: ${event.error_message ?? "No error message captured."}`,
    "Explain the likely cause and suggest the smallest code change to fix it."
  ].join("\n");
}

function formatLocation(event: EventNode): string {
  if (event.file_path && event.line_number !== null) {
    return `${event.file_path}:${event.line_number}`;
  }
  return event.file_path ?? "No source location captured";
}
