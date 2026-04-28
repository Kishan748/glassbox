import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RunList } from "./RunList";
import type { RunSummary } from "../api/types";

const runs: RunSummary[] = [
  {
    id: "run_1",
    project_name: "Demo",
    started_at: "2026-04-28T10:00:00Z",
    ended_at: "2026-04-28T10:00:02Z",
    status: "completed",
    runtime_language: "python",
    runtime_version: "3.14",
    os: "macOS",
    cwd: "/tmp/demo",
    total_cost_usd: 0.03,
    total_input_tokens: 12,
    total_output_tokens: 8,
    duration_ms: 2000,
    tags: ["local"]
  }
];

describe("RunList", () => {
  it("shows runs and selects a run", async () => {
    const onSelectRun = vi.fn();

    render(<RunList runs={runs} selectedRunId={undefined} onSelectRun={onSelectRun} />);
    await userEvent.click(screen.getByRole("button", { name: /Demo completed/i }));

    expect(screen.getByText("Runs")).toBeInTheDocument();
    expect(screen.getByText("run_1")).toBeInTheDocument();
    expect(onSelectRun).toHaveBeenCalledWith("run_1");
  });
});
