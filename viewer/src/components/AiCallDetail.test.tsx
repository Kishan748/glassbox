import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AiCallDetail } from "./AiCallDetail";
import type { AiCall } from "../api/types";

const aiCall: AiCall = {
  event_id: "evt_ai",
  provider: "openai",
  model: "gpt-4o-mini",
  temperature: 0.2,
  max_tokens: 128,
  system_prompt: null,
  messages: [{ role: "user", content: "What happened?" }],
  response_text: "The run completed.",
  stop_reason: "stop",
  input_tokens: 12,
  output_tokens: 8,
  cost_usd: 0.000012
};

describe("AiCallDetail", () => {
  it("shows AI call detail and copies prompt and response", async () => {
    const writeText = vi.fn(async () => undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    render(<AiCallDetail aiCall={aiCall} durationMs={230} />);

    expect(screen.getByText("AI call")).toBeInTheDocument();
    expect(screen.getByText("openai")).toBeInTheDocument();
    expect(screen.getByText("gpt-4o-mini")).toBeInTheDocument();
    expect(screen.getByText("230 ms")).toBeInTheDocument();
    expect(screen.getByText("12 in / 8 out")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Copy prompt" }));
    await userEvent.click(screen.getByRole("button", { name: "Copy response" }));

    expect(writeText).toHaveBeenNthCalledWith(1, JSON.stringify(aiCall.messages, null, 2));
    expect(writeText).toHaveBeenNthCalledWith(2, "The run completed.");
  });
});
