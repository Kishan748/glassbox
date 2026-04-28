import { CheckCircle2, CircleAlert, LoaderCircle } from "lucide-react";

import type { RunSummary } from "../api/types";
import { formatCost, formatDuration } from "../utils/format";

interface RunListProps {
  runs: RunSummary[];
  selectedRunId: string | undefined;
  onSelectRun: (runId: string) => void;
}

export function RunList({ runs, selectedRunId, onSelectRun }: RunListProps) {
  return (
    <aside className="run-list" aria-label="Runs">
      <div className="panel-header">
        <h2>Runs</h2>
        <span>{runs.length}</span>
      </div>
      {runs.length === 0 ? (
        <p className="muted empty-state">No runs found. Run an instrumented Python app first.</p>
      ) : (
        <div className="run-list-items">
          {runs.map((run) => (
            <button
              className={`run-list-item ${run.id === selectedRunId ? "selected" : ""}`}
              key={run.id}
              onClick={() => onSelectRun(run.id)}
              type="button"
              aria-label={`${run.project_name} ${run.status}`}
            >
              <StatusIcon status={run.status} />
              <span className="run-list-copy">
                <strong>{run.project_name}</strong>
                <span>{run.id}</span>
              </span>
              <span className="run-list-meta">
                {formatDuration(run.duration_ms)}
                <span>{formatCost(run.total_cost_usd)}</span>
              </span>
            </button>
          ))}
        </div>
      )}
    </aside>
  );
}

function StatusIcon({ status }: { status: string }) {
  if (status === "completed") {
    return <CheckCircle2 aria-hidden="true" className="status-icon completed" size={18} />;
  }
  if (status === "failed") {
    return <CircleAlert aria-hidden="true" className="status-icon failed" size={18} />;
  }
  return <LoaderCircle aria-hidden="true" className="status-icon running" size={18} />;
}
