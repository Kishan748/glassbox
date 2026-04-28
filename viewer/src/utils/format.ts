export function formatDuration(durationMs: number | null): string {
  if (durationMs === null) {
    return "Running";
  }
  if (durationMs < 1000) {
    return `${durationMs} ms`;
  }
  return `${(durationMs / 1000).toFixed(2)}s`;
}

export function formatCost(cost: number | null): string {
  if (cost === null) {
    return "$0.000000";
  }
  return `$${cost.toFixed(6)}`;
}

export function formatTokens(inputTokens: number | null, outputTokens: number | null): string {
  if (inputTokens === null && outputTokens === null) {
    return "No token data";
  }
  return `${inputTokens ?? 0} in / ${outputTokens ?? 0} out`;
}

export function countEvents(events: { children: unknown[] }[]): number {
  return events.reduce((count, event) => {
    const children = event.children as { children: unknown[] }[];
    return count + 1 + countEvents(children);
  }, 0);
}
