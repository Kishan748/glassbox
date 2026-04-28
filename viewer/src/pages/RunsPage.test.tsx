import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RunsPage } from "./RunsPage";

describe("RunsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("explains how to create a database when no Glassbox database exists", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: RequestInfo | URL) => {
        const path = String(url);
        const body =
          path === "/api/stats"
            ? {
                database_exists: false,
                setup_required: true,
                run_count: 0,
                event_count: 0,
                ai_call_count: 0
              }
            : { setup_required: true, runs: [] };

        return new Response(JSON.stringify(body), {
          headers: { "content-type": "application/json" }
        });
      })
    );

    render(<RunsPage />);

    await waitFor(() => {
      expect(screen.getByText("No Glassbox database found.")).toBeInTheDocument();
    });
    expect(screen.getByText(/python3 examples\/simple_tracked_app.py/)).toBeInTheDocument();
    expect(screen.getByText(/python3 -m glassbox view --db glassbox.db/)).toBeInTheDocument();
  });

  it("explains that an existing database can still be empty or the wrong path", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: RequestInfo | URL) => {
        const path = String(url);
        const body =
          path === "/api/stats"
            ? {
                database_exists: true,
                setup_required: false,
                run_count: 0,
                event_count: 0,
                ai_call_count: 0
              }
            : { setup_required: false, runs: [] };

        return new Response(JSON.stringify(body), {
          headers: { "content-type": "application/json" }
        });
      })
    );

    render(<RunsPage />);

    await waitFor(() => {
      expect(screen.getByText("No runs found in this database.")).toBeInTheDocument();
    });
    expect(screen.getByText(/If you expected runs here, check the --db path/)).toBeInTheDocument();
  });
});
