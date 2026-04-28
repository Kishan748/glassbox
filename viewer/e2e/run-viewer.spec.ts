import { expect, type Page, test } from "@playwright/test";

const run = {
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

const aiCall = {
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
};

const events = [
  {
    id: "evt_parent",
    run_id: "run_1",
    parent_id: null,
    event_type: "function",
    name: "main",
    started_at: "2026-04-28T10:00:00Z",
    duration_ms: 2000,
    status: "failed",
    error_message: "ValueError: boom",
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
        ai_call: aiCall,
        children: []
      }
    ]
  }
];

test("loads a run and copies selected event debug context", async ({ context, page }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await mockRunApi(page);

  await page.goto("/#runs");

  await expect(page.getByRole("heading", { name: "Demo" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Function main failed 2.00s/i })).toBeVisible();

  await page.getByRole("button", { name: /Function main failed 2.00s/i }).click();
  await page.getByRole("button", { name: "Copy debug prompt" }).click();

  const prompt = await page.evaluate(() => navigator.clipboard.readText());
  expect(prompt).toContain("Debug this Glassbox event.");
  expect(prompt).toContain("Run: run_1");
  expect(prompt).toContain("Project: Demo");
  expect(prompt).toContain("Source: app.py:10");
  expect(prompt).toContain("local AI traces");
});

test("keeps event detail to the right of steps on desktop", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await mockRunApi(page);

  await page.goto("/#runs");
  await page.getByRole("button", { name: /Function main failed 2.00s/i }).click();

  const stepsBox = await page.locator(".steps-panel").boundingBox();
  const detailsBox = await page.locator(".detail-grid").boundingBox();

  expect(stepsBox).not.toBeNull();
  expect(detailsBox).not.toBeNull();
  expect(detailsBox!.x).toBeGreaterThan(stepsBox!.x + stepsBox!.width - 1);
  expect(Math.abs(detailsBox!.y - stepsBox!.y)).toBeLessThanOrEqual(4);
});

async function mockRunApi(page: Page) {
  await page.route("**/api/stats", (route) =>
    route.fulfill({ json: { setup_required: false, run_count: 1, event_count: 2, ai_call_count: 1 } })
  );
  await page.route("**/api/runs", (route) => route.fulfill({ json: { runs: [run] } }));
  await page.route("**/api/runs/run_1", (route) => route.fulfill({ json: { run } }));
  await page.route("**/api/runs/run_1/events", (route) =>
    route.fulfill({ json: { events } })
  );
}
