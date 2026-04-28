import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RunDetail } from "./RunDetail";
import type { AiCall, EventNode, RunSummary } from "../api/types";

const run: RunSummary = {
  id: "run_1",
  project_name: "Demo",
  started_at: "2026-04-28T10:00:00Z",
  ended_at: "2026-04-28T10:00:02Z",
  status: "failed",
  runtime_language: "python",
  runtime_version: "3.14",
  os: "macOS",
  cwd: "/tmp/demo",
  total_cost_usd: 0.12,
  total_input_tokens: 100,
  total_output_tokens: 50,
  duration_ms: 2000,
  tags: ["local"]
};

const events: EventNode[] = [
  {
    id: "evt_parent",
    run_id: "run_1",
    parent_id: null,
    event_type: "function",
    name: "main",
    started_at: "2026-04-28T10:00:00Z",
    duration_ms: 2000,
    status: "failed",
    error_message: null,
    file_path: "app.py",
    line_number: 10,
    data: {
      args: ["local AI traces"],
      return_value: "Explain why local AI traces help debugging."
    },
    children: [
      {
        id: "evt_ai",
        run_id: "run_1",
        parent_id: "evt_parent",
        event_type: "ai_call",
        name: "openai.chat.completions.create",
        started_at: "2026-04-28T10:00:01Z",
        duration_ms: 250,
        status: "completed",
        error_message: null,
        file_path: null,
        line_number: null,
        data: { provider: "openai", model: "gpt-4o-mini" },
        children: []
      }
    ]
  }
];

const aiCalls: AiCall[] = [
  {
    event_id: "evt_ai",
    provider: "openai",
    model: "gpt-4o-mini",
    temperature: null,
    max_tokens: null,
    system_prompt: null,
    messages: [{ role: "user", content: "Prompt" }],
    response_text: "Response",
    stop_reason: "stop",
    input_tokens: 100,
    output_tokens: 50,
    cost_usd: 0.12
  }
];

describe("RunDetail", () => {
  it("shows run metrics, steps, and AI call detail", () => {
    render(<RunDetail run={run} events={events} aiCalls={aiCalls} />);

    expect(screen.getByRole("heading", { name: "Demo" })).toBeInTheDocument();
    expect(screen.getAllByText("failed").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("2.00s").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("$0.120000").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("2 steps")).toBeInTheDocument();
    expect(screen.getByText("Steps")).toBeInTheDocument();
    expect(screen.getByText("main")).toBeInTheDocument();
    expect(screen.getAllByText("openai.chat.completions.create").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("AI call").length).toBeGreaterThanOrEqual(1);
  });

  it("selects a function event and shows its captured data", async () => {
    render(<RunDetail run={run} events={events} aiCalls={aiCalls} />);

    await userEvent.click(screen.getByRole("button", { name: /Function main failed 2.00s/i }));

    expect(screen.getByRole("heading", { name: "Event detail" })).toBeInTheDocument();
    expect(screen.getAllByText("main").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("app.py:10")).toBeInTheDocument();
    expect(screen.getByText(/local AI traces/)).toBeInTheDocument();
    expect(screen.getByText(/Explain why local AI traces help debugging/)).toBeInTheDocument();
  });

  it("selects an AI event and shows its prompt and response", async () => {
    render(<RunDetail run={run} events={events} aiCalls={aiCalls} />);

    await userEvent.click(
      screen.getByRole("button", { name: /AI call openai.chat.completions.create completed 250 ms/i })
    );

    expect(screen.getByRole("heading", { name: "Event detail" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "AI call" })).toBeInTheDocument();
    expect(screen.getAllByText(/Prompt/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Response/).length).toBeGreaterThanOrEqual(1);
  });

  it("copies a debugging prompt for the selected event", async () => {
    const writeText = vi.fn();
    Object.assign(navigator, { clipboard: { writeText } });
    render(<RunDetail run={run} events={events} aiCalls={aiCalls} />);

    await userEvent.click(screen.getByRole("button", { name: /Function main failed 2.00s/i }));
    await userEvent.click(screen.getByRole("button", { name: "Copy debug prompt" }));

    expect(writeText).toHaveBeenCalledTimes(1);
    const prompt = writeText.mock.calls[0][0] as string;
    expect(prompt).toContain("Debug this Glassbox event.");
    expect(prompt).toContain("Run: run_1");
    expect(prompt).toContain("Project: Demo");
    expect(prompt).toContain("Event: main");
    expect(prompt).toContain("Source: app.py:10");
    expect(prompt).toContain("local AI traces");
  });

  it("includes AI call prompt and response in the copied debugging prompt", async () => {
    const writeText = vi.fn();
    Object.assign(navigator, { clipboard: { writeText } });
    render(<RunDetail run={run} events={events} aiCalls={aiCalls} />);

    await userEvent.click(
      screen.getByRole("button", { name: /AI call openai.chat.completions.create completed 250 ms/i })
    );
    await userEvent.click(screen.getByRole("button", { name: "Copy debug prompt" }));

    const prompt = writeText.mock.calls[0][0] as string;
    expect(prompt).toContain("AI call:");
    expect(prompt).toContain("Provider: openai");
    expect(prompt).toContain('"content": "Prompt"');
    expect(prompt).toContain("Response");
  });

  it("scrolls selected event details into view on mobile", async () => {
    const scrollIntoView = vi.fn();
    const originalScrollIntoView = window.HTMLElement.prototype.scrollIntoView;
    const originalMatchMedia = window.matchMedia;
    const originalRequestAnimationFrame = window.requestAnimationFrame;
    window.HTMLElement.prototype.scrollIntoView = scrollIntoView;
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      value: vi.fn().mockReturnValue({ matches: true })
    });
    Object.defineProperty(window, "requestAnimationFrame", {
      configurable: true,
      value: (callback: FrameRequestCallback) => {
        callback(0);
        return 0;
      }
    });

    try {
      render(<RunDetail run={run} events={events} aiCalls={aiCalls} />);

      await userEvent.click(screen.getByRole("button", { name: /Function main failed 2.00s/i }));

      expect(scrollIntoView).toHaveBeenCalledWith({ behavior: "smooth", block: "start" });
    } finally {
      window.HTMLElement.prototype.scrollIntoView = originalScrollIntoView;
      Object.defineProperty(window, "matchMedia", {
        configurable: true,
        value: originalMatchMedia
      });
      Object.defineProperty(window, "requestAnimationFrame", {
        configurable: true,
        value: originalRequestAnimationFrame
      });
    }
  });
});
