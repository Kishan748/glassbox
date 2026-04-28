import { Clipboard, Cpu } from "lucide-react";

import type { AiCall } from "../api/types";
import { formatCost, formatTokens } from "../utils/format";

interface AiCallDetailProps {
  aiCall: AiCall;
  durationMs: number | null;
}

export function AiCallDetail({ aiCall, durationMs }: AiCallDetailProps) {
  const prompt = JSON.stringify(aiCall.messages, null, 2);
  const response = aiCall.response_text ?? "";

  return (
    <section className="detail-panel">
      <div className="section-title">
        <Cpu aria-hidden="true" size={18} />
        <h3>AI call</h3>
      </div>
      <dl className="meta-grid">
        <div>
          <dt>Provider</dt>
          <dd>{aiCall.provider}</dd>
        </div>
        <div>
          <dt>Model</dt>
          <dd>{aiCall.model}</dd>
        </div>
        <div>
          <dt>Latency</dt>
          <dd>{durationMs === null ? "Unknown" : `${durationMs} ms`}</dd>
        </div>
        <div>
          <dt>Tokens</dt>
          <dd>{formatTokens(aiCall.input_tokens, aiCall.output_tokens)}</dd>
        </div>
        <div>
          <dt>Cost</dt>
          <dd>{formatCost(aiCall.cost_usd)}</dd>
        </div>
      </dl>

      <div className="copy-row">
        <h4>Prompt</h4>
        <button type="button" onClick={() => copyText(prompt)} aria-label="Copy prompt">
          <Clipboard aria-hidden="true" size={16} />
          Copy prompt
        </button>
      </div>
      <pre className="code-block">{prompt}</pre>

      <div className="copy-row">
        <h4>Response</h4>
        <button type="button" onClick={() => copyText(response)} aria-label="Copy response">
          <Clipboard aria-hidden="true" size={16} />
          Copy response
        </button>
      </div>
      <pre className="code-block">{response || "No response text captured."}</pre>
    </section>
  );
}

function copyText(text: string) {
  return navigator.clipboard?.writeText(text);
}
