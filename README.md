🌍 Multi-Agent Travel Planner

This project implements a Multi-Agent Travel Planner that generates personalized travel itineraries using a multi-phase workflow:

1. **Scope** – Clarify the traveler’s preferences (destinations, budget, style)

2. **Research** – Run parallel research agents for flights, hotels, and activities

3. **Plane/Write**  – Synthesize findings into a coherent day-by-day itinerary

The system leverages structured outputs, tool integration, and supervisor orchestration to produce detailed, user-aligned trip plans.

🚀 Quickstart
Prerequisites

Python 3.11+

uv
 for dependency management

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/Users/$USER/.local/bin:$PATH"

Installation
# Clone the repository
git clone https://github.com/kiransalunke94/Multi-Agent-Travel-Planner.git
cd Multi-Agent-Travel-Planner

# Install dependencies
uv sync
or
pip install .

Set up environment variables in .env (Rename env to .env):
```env
LLM_API_KEY=your_model_api_key_here
COMPRESSION_API_KEY=your_model_api_key_here
SUMMARIZE_API_KEY=your_model_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here   # optional
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=multi_agent_travel_planner
```

1. Trip Brief Generation

🎯 Purpose: Convert raw user input into structured travel briefs.

- Key Concepts:

    - Clarify ambiguous inputs
    - Structured representation of trip constraints (dates, budget, destinations)
    - Conditional routing when information is missing

- Implementation Highlights:

    - Pydantic models (ClarifyWithUser)
    - Date-aware prompt formatting
    - Structured output parsing

2. Research Agents with Travel Tools

🎯 Purpose: Collect and refine travel-related data (flights, stays, activities).

- Key Concepts:

    - Parallel research agents
    - Summarization of noisy API/search results
    - Think tool to reflect on findings and plan next steps

- Implementation Highlights:

    - Tavily Search for real-time results
    - Iterative research loop with refinement
    - Summarizer node for clean inputs to the planner
    - Compression node to compress the final research.

3. Supervisor Agent

🎯 Purpose: Orchestrate multiple research agents efficiently.

- Key Concepts:
    - Supervisor–researcher pattern
    - Parallel execution with async orchestration
    - Independent contexts per researcher

- Implementation Highlights:

    - Supervisor delegates tasks (flights, hotels, activities)
    - Agents run in parallel with asyncio.gather()
    - Context isolation ensures independent reasoning

4. Final Planner Agent

🎯 Purpose: Produce the final structured travel itinerary.

- Key Concepts:

    - Merge research into a single trip plan
    - Day-by-day itinerary with logistics + highlights
    - Align with user preferences (budget, travel style)

Implementation Highlights:

    - Trip synthesis into structured plan format
    - Human-readable itinerary output

🎯 Outcomes

✅ Structured Outputs → reliable trip briefs

⚡ Parallel Research → reduces latency

🧭 Supervisor Orchestration → focused & efficient agents

🔌 Tool Integration → real-time travel data

🌍 End-to-End Flow → coherent, ready-to-use itinerary
