export type RunStatus = "running" | "completed" | "failed" | string;

export interface RunSummary {
  id: string;
  project_name: string;
  started_at: string;
  ended_at: string | null;
  status: RunStatus;
  runtime_language: string;
  runtime_version: string | null;
  os: string | null;
  cwd: string | null;
  total_cost_usd: number | null;
  total_input_tokens: number | null;
  total_output_tokens: number | null;
  duration_ms: number | null;
  tags: string[];
}

export interface EventNode {
  id: string;
  run_id: string;
  parent_id: string | null;
  event_type: string;
  name: string;
  started_at: string;
  duration_ms: number | null;
  status: RunStatus;
  error_message: string | null;
  file_path: string | null;
  line_number: number | null;
  data: Record<string, unknown>;
  children: EventNode[];
  ai_call?: AiCall | null;
}

export interface AiCall {
  event_id: string;
  provider: string;
  model: string;
  temperature: number | null;
  max_tokens: number | null;
  system_prompt: string | null;
  messages: Array<Record<string, unknown>>;
  response_text: string | null;
  stop_reason: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
}

export interface StatsResponse {
  database_exists: boolean;
  setup_required: boolean;
  run_count: number;
  event_count: number;
  ai_call_count: number;
}

export interface RunsResponse {
  setup_required?: boolean;
  runs: RunSummary[];
}

export interface RunResponse {
  run: RunSummary;
}

export interface RunEventsResponse {
  events: EventNode[];
}
