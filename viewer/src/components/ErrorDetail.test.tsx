import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ErrorDetail } from "./ErrorDetail";
import type { EventNode } from "../api/types";

const event: EventNode = {
  id: "evt_error",
  run_id: "run_1",
  parent_id: null,
  event_type: "function",
  name: "explode",
  started_at: "2026-04-28T10:00:00Z",
  duration_ms: 12,
  status: "failed",
  error_message: "ValueError: boom",
  file_path: "app.py",
  line_number: 42,
  data: {},
  children: []
};

describe("ErrorDetail", () => {
  it("shows error location and copies a clean debugging prompt", async () => {
    const writeText = vi.fn(async (_text: string): Promise<void> => undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<ErrorDetail event={event} runId="run_1" />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("ValueError: boom")).toBeInTheDocument();
    expect(screen.getByText("app.py:42")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Copy debugging prompt" }));

    expect(writeText.mock.calls[0][0]).toContain("run_1");
    expect(writeText.mock.calls[0][0]).toContain("ValueError: boom");
    expect(writeText.mock.calls[0][0]).toContain("app.py:42");
  });
});
