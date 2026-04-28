import type { RunEventsResponse, RunResponse, RunsResponse, StatsResponse } from "./types";

export async function fetchStats(): Promise<StatsResponse> {
  return fetchJson<StatsResponse>("/api/stats");
}

export async function fetchRuns(): Promise<RunsResponse> {
  return fetchJson<RunsResponse>("/api/runs");
}

export async function fetchRun(runId: string): Promise<RunResponse> {
  return fetchJson<RunResponse>(`/api/runs/${encodeURIComponent(runId)}`);
}

export async function fetchRunEvents(runId: string): Promise<RunEventsResponse> {
  return fetchJson<RunEventsResponse>(`/api/runs/${encodeURIComponent(runId)}/events`);
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}
