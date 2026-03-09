"""Local Orchestrator — dispatches tasks to ACP agents and collects the final report."""

import argparse
import json
import sys
from datetime import datetime, timezone

import httpx

AGENT_URLS = {
    "topic-scout": "http://localhost:8001",
    "summarizer": "http://localhost:8002",
    "sentiment-analyzer": "http://localhost:8003",
    "editor": "http://localhost:8004",
}

TIMEOUT = 600


def call_agent(agent_name: str, input_content: str, content_type: str = "application/json") -> str:
    """Call an ACP agent and return the response content."""
    url = AGENT_URLS[agent_name]

    # Create a run
    payload = {
        "agent_name": agent_name.replace("-", "_"),
        "input": [
            {
                "role": "user",
                "parts": [{"content": input_content, "content_type": content_type}],
            }
        ],
    }

    with httpx.Client(base_url=url, timeout=TIMEOUT) as client:
        # Start a run
        response = client.post("/runs", json=payload)
        response.raise_for_status()
        run = response.json()

        # If the run completed synchronously, extract output
        if run.get("status") == "completed":
            return extract_output(run)

        # Otherwise poll until complete
        run_id = run["run_id"]
        while True:
            response = client.get(f"/runs/{run_id}")
            response.raise_for_status()
            run = response.json()
            if run.get("status") in ("completed", "failed"):
                break

        if run.get("status") == "failed":
            print(f"  Agent {agent_name} failed: {run.get('error', 'unknown error')}", file=sys.stderr)
            sys.exit(1)

        return extract_output(run)


def extract_output(run: dict) -> str:
    """Extract the content from the last agent message in a run."""
    output = run.get("output", [])
    if not output:
        return ""
    last_message = output[-1]
    parts = last_message.get("parts", [])
    if not parts:
        return ""
    return parts[-1].get("content", "")


def main():
    parser = argparse.ArgumentParser(description="AI News Pipeline Orchestrator")
    parser.add_argument("--output-dir", default="output", help="Directory to save the briefing report")
    args = parser.parse_args()

    print("=" * 60)
    print("  AI News Pipeline — ACP Orchestrator")
    print("=" * 60)

    # Step 1: Topic Scout
    print("\n[1/4] Calling Topic Scout agent...")
    topics = call_agent("topic-scout", json.dumps({"request": "Find trending AI news"}))
    print(f"  Received topics.")

    # Step 2: Summarizer
    print("\n[2/4] Calling Summarizer agent...")
    summaries = call_agent("summarizer", topics)
    print(f"  Received summaries.")

    # Step 3: Sentiment Analyzer
    print("\n[3/4] Calling Sentiment Analyzer agent...")
    analyzed = call_agent("sentiment-analyzer", summaries)
    print(f"  Received sentiment analysis.")

    # Step 4: Editor
    print("\n[4/4] Calling Editor agent...")
    briefing = call_agent("editor", analyzed, content_type="text/markdown")
    print(f"  Received final briefing.")

    # Save the report
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{args.output_dir}/ai-news-briefing-{timestamp}.md"

    with open(filename, "w") as f:
        f.write(briefing)

    print(f"\n{'=' * 60}")
    print(f"  Briefing saved to: {filename}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
