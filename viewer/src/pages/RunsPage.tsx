import { useEffect, useMemo, useState } from "react";

import { fetchRun, fetchRunEvents, fetchRuns, fetchStats } from "../api/client";
import type { EventNode, RunSummary, StatsResponse } from "../api/types";
import { RunDetail } from "../components/RunDetail";
import { RunList } from "../components/RunList";

export function RunsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | undefined>();
  const [selectedRun, setSelectedRun] = useState<RunSummary | null>(null);
  const [events, setEvents] = useState<EventNode[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadRuns() {
      try {
        const [statsResponse, runsResponse] = await Promise.all([fetchStats(), fetchRuns()]);
        if (cancelled) {
          return;
        }
        setStats(statsResponse);
        setRuns(runsResponse.runs);
        setSelectedRunId((current) => current ?? runsResponse.runs[0]?.id);
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load runs.");
        }
      }
    }

    void loadRuns();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      return;
    }
    const runId = selectedRunId;
    let cancelled = false;

    async function loadRun() {
      try {
        const [runResponse, eventsResponse] = await Promise.all([
          fetchRun(runId),
          fetchRunEvents(runId)
        ]);
        if (!cancelled) {
          setSelectedRun(runResponse.run);
          setEvents(eventsResponse.events);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Failed to load run.");
        }
      }
    }

    void loadRun();
    return () => {
      cancelled = true;
    };
  }, [selectedRunId]);

  const setupRequired = Boolean(stats?.setup_required);
  const content = useMemo(() => {
    if (error) {
      return <p className="empty-state error-text">{error}</p>;
    }
    if (setupRequired) {
      return (
        <EmptyState
          title="No Glassbox database found."
          body="Create one by running an instrumented app, then reopen the viewer with the same database path."
          commands={[
            "python3 examples/simple_tracked_app.py",
            "python3 -m glassbox view --db glassbox.db --port 4747"
          ]}
        />
      );
    }
    if (stats && runs.length === 0) {
      return (
        <EmptyState
          title="No runs found in this database."
          body="If you expected runs here, check the --db path and make sure your app called glassbox.init()."
          commands={[
            "python3 -m glassbox runs --db glassbox.db",
            "python3 -m glassbox view --db glassbox.db --port 4747"
          ]}
        />
      );
    }
    if (!selectedRun) {
      return <p className="empty-state">Select a run to inspect its steps.</p>;
    }
    return <RunDetail run={selectedRun} events={events} />;
  }, [error, events, runs.length, selectedRun, setupRequired, stats]);

  return (
    <div className="runs-page">
      <RunList runs={runs} selectedRunId={selectedRunId} onSelectRun={setSelectedRunId} />
      <main className="main-panel">{content}</main>
    </div>
  );
}

function EmptyState({
  title,
  body,
  commands
}: {
  title: string;
  body: string;
  commands: string[];
}) {
  return (
    <section className="empty-state empty-state-detail">
      <h1>{title}</h1>
      <p>{body}</p>
      <div className="command-list" aria-label="Suggested commands">
        {commands.map((command) => (
          <code key={command}>{command}</code>
        ))}
      </div>
    </section>
  );
}
