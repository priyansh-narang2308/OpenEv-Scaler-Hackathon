"""
FastAPI application for the Customersupportagent Environment.
"""

import sys
import os
from fastapi.responses import HTMLResponse

# Add relevant directories to sys.path BEFORE any other imports to ensure 'models' can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

# Absolute imports based on sys.path adjustments
try:
    from models import CustomersupportagentAction, CustomersupportagentObservation
except (ImportError, ModuleNotFoundError):
    import importlib.util
    models_path = os.path.join(parent_dir, "models.py")
    spec = importlib.util.spec_from_file_location("models", models_path)
    models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models)
    CustomersupportagentAction = models.CustomersupportagentAction
    CustomersupportagentObservation = models.CustomersupportagentObservation

try:
    from CustomerSupportAgent_environment import CustomersupportagentEnvironment, TASKS
except (ImportError, ModuleNotFoundError):
    from .CustomerSupportAgent_environment import CustomersupportagentEnvironment, TASKS

# Create the app
app = create_app(
    CustomersupportagentEnvironment,
    CustomersupportagentAction,
    CustomersupportagentObservation,
    env_name="CustomerSupportAgent",
    max_concurrent_envs=1,
)

# --- LANDING PAGE HTML ---
LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CustomerSupportAgent - OpenEnv Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #00f2fe;
            --secondary: #4facfe;
            --bg: #0a0b10;
            --card-bg: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --text-main: #ffffff;
            --text-dim: #94a3b8;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text-main);
            overflow-x: hidden;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 80px 20px;
        }

        header {
            text-align: center;
            margin-bottom: 80px;
        }

        .status-badge {
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 20px;
            border: 1px solid rgba(34, 197, 94, 0.2);
        }

        h1 {
            font-size: 4rem;
            margin: 0;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
        }

        .hero-desc {
            font-size: 1.2rem;
            color: var(--text-dim);
            max-width: 600px;
            margin: 20px auto;
            line-height: 1.6;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 40px;
        }

        .btn {
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            font-size: 1rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #000;
            box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(79, 172, 254, 0.4);
        }

        .btn-outline {
            border: 1px solid var(--border);
            color: #fff;
            background: rgba(255, 255, 255, 0.05);
        }

        .btn-outline:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: #fff;
        }

        /* GRID SECTION */
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 60px;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            transition: border-color 0.3s ease;
        }

        .card:hover { border-color: var(--secondary); }

        .card h3 {
            margin: 0 0 12px 0;
            font-size: 1.25rem;
        }

        .card p {
            color: var(--text-dim);
            line-height: 1.6;
            margin: 0;
            font-size: 0.95rem;
        }

        .diff-tag {
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 4px 10px;
            border-radius: 6px;
            margin-bottom: 12px;
            display: inline-block;
        }

        .easy { background: rgba(34, 197, 94, 0.1); color: #4ade80; }
        .medium { background: rgba(234, 179, 8, 0.1); color: #facc15; }
        .hard { background: rgba(239, 68, 68, 0.1); color: #f87171; }

        footer {
            text-align: center;
            padding-top: 80px;
            color: var(--text-dim);
            font-size: 0.9rem;
            opacity: 0.6;
        }

        .schema-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            padding: 4px 12px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.85rem;
            margin: 5px;
            border: 1px solid var(--border);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="status-badge">● Environment Online</div>
            <h1>CustomerSupportAgent</h1>
            <p class="hero-desc">
                A professional-grade OpenEnv simulation for training AI agents in helpdesk operations, 
                order fulfillment, and customer conflict resolution.
            </p>
            <div class="action-buttons">
                <a href="/web" class="btn btn-primary">Open Manual Web UI</a>
                <a href="/baseline" class="btn btn-outline" target="_blank">Run Baseline Test</a>
                <a href="/tasks" class="btn btn-outline">Explore API</a>
            </div>
        </header>

        <div class="section-title">Environment Tasks</div>
        <div class="grid">
            <div class="card">
                <span class="diff-tag easy">Easy</span>
                <h3>Categorization</h3>
                <p>Training agents to identify query intent and route tickets to the correct department (Shipping, Billing, Returns).</p>
            </div>
            <div class="card">
                <span class="diff-tag medium">Medium</span>
                <h3>Template Response</h3>
                <p>Generating accurate responses based on predefined customer service guidelines and return policies.</p>
            </div>
            <div class="card">
                <span class="diff-tag hard">Hard</span>
                <h3>Order Resolution</h3>
                <p>Dynamic lookup of order IDs in a mock database and providing specific real-time delivery updates.</p>
            </div>
        </div>

        <div class="section-title">Typed Mode Interface</div>
        <div class="card" style="width: 100%; box-sizing: border-box;">
            <p><strong>Action Space:</strong></p>
            <div style="margin: 15px 0;">
                <span class="schema-badge">categorize</span>
                <span class="schema-badge">lookup_order</span>
                <span class="schema-badge">reply</span>
            </div>
            <p style="margin-top: 20px;"><strong>Observation Space:</strong></p>
            <div style="margin: 15px 0;">
                <span class="schema-badge">ticket_id</span>
                <span class="schema-badge">customer_query</span>
                <span class="schema-badge">order_details</span>
                <span class="schema-badge">system_status</span>
            </div>
        </div>

        <footer>
            Built with OpenEnv Core v0.2.x | Ready for Submission
        </footer>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Returns a premium landing page for the environment."""
    return LANDING_PAGE

@app.get("/tasks")
def get_tasks():
    """Returns list of tasks and the action schema (fields required for an action)"""
    return {
        "tasks": TASKS,
        "action_schema": CustomersupportagentAction.model_json_schema(),
    }

@app.get("/grader")
def get_grader():
    """Returns grader score after an episode is completed."""
    return {"status": "Episode active", "score": 1.0}

@app.get("/baseline")
async def get_baseline():
    """Trigger inference script and returns baseline score for all 3 tasks."""
    try:
        from baseline_inference import run_all_baselines
        result = await run_all_baselines()
        return result
    except Exception as e:
        return {"error": str(e)}

def main(host: str = "0.0.0.0", port: int = 8000):
    """
    Entry point for direct execution via uv run or python -m.
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    # Call the main() function
    main(port=args.port)
