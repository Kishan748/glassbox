import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchRun, fetchRunEvents, fetchRuns, fetchStats } from "./client";

describe("viewer API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches stats, runs, run detail, and events from the backend API", async () => {
    const fetchMock = vi.fn(async (url: RequestInfo | URL) => {
      const path = String(url);
      const body =
        path === "/api/stats"
          ? { run_count: 1, event_count: 2, ai_call_count: 1 }
          : path === "/api/runs"
            ? { runs: [{ id: "run_1", project_name: "Demo", status: "completed" }] }
            : path === "/api/runs/run_1"
              ? { run: { id: "run_1", project_name: "Demo", status: "completed" } }
              : { events: [{ id: "evt_1", name: "step", children: [] }] };

      return new Response(JSON.stringify(body), {
        headers: { "content-type": "application/json" }
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchStats()).resolves.toMatchObject({ run_count: 1 });
    await expect(fetchRuns()).resolves.toMatchObject({ runs: [{ id: "run_1" }] });
    await expect(fetchRun("run_1")).resolves.toMatchObject({ run: { id: "run_1" } });
    await expect(fetchRunEvents("run_1")).resolves.toMatchObject({
      events: [{ id: "evt_1" }]
    });

    expect(fetchMock).toHaveBeenCalledWith("/api/stats");
    expect(fetchMock).toHaveBeenCalledWith("/api/runs");
    expect(fetchMock).toHaveBeenCalledWith("/api/runs/run_1");
    expect(fetchMock).toHaveBeenCalledWith("/api/runs/run_1/events");
  });
});
