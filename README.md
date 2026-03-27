---
title: CustomerSupportAgent OpenEnv
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# CustomerSupportAgent OpenEnv

A real-world simulation of a Customer Support Helpdesk. This environment allows AI agents to practice categorizing tickets, looking up order information from a database, and drafting helpful responses to customers.

## Motivation

AI agents are increasingly used in customer support roles. However, most evaluations focus on narrow tasks. `CustomerSupportAgent` provides a multi-step environment where the agent must integrate information from multiple sources (customer query + internal database) to provide a high-quality resolution.

## Environment Details

### Action Space

The agent can perform three types of actions:

1.  **categorize**: Assign a category to the ticket.
    - `category`: Choice of ["Shipping", "Returns", "Technical Support", "Billing"]
2.  **lookup_order**: Query the internal database for order information.
    - `order_id`: The ID of the order to look up (e.g., "ORD-12345")
3.  **reply**: Send the final response to the customer. This action ends the episode.
    - `reply_text`: The text of the response.

### Observation Space

The observation provided at each step includes:

-   `ticket_id`: Unique ID for the current session.
-   `customer_query`: The original text from the customer.
-   `suggested_categories`: A list of valid categories.
-   `order_details`: Information returned from a successful `lookup_order` action.
-   `history`: A log of previous actions in the current episode.
-   `system_status`: Current state of the ticket (e.g., "New", "Categorized", "Resolved").

### Tasks & Graders

The environment includes 3 tasks with increasing difficulty:

| Task ID | Difficulty | Objective | Grader Criteria |
| :--- | :--- | :--- | :--- |
| **easy_shipping** | Easy | Categorize a simple shipping query. | Correct category assignment. |
| **medium_return** | Medium | Categorize and provide return instructions. | Correct category + key terms in reply. |
| **hard_order_lookup** | Hard | Lookup a specific order and provide its status. | Correct category + order lookup + specific status in reply. |

### Reward Function

Rewards are provided for partial progress:
- **0.3**: Correct categorization.
- **0.2**: Successful order lookup (if relevant).
- **0.4 - 0.5**: Successful reply meeting task criteria.
Total reward ranges from **0.0** to **1.0**.

## Baseline Scores

The baseline agent uses `gpt-3.5-turbo` (or a deterministic fallback) to solve the tasks.

| Task | Baseline Score |
| :--- | :--- |
| easy_shipping | 0.70 |
| medium_return | 0.70 |
| hard_order_lookup | 1.00 |

**Average Baseline Score: 0.80**

## Setup and Usage

### Quick Start with Docker

1.  **Build the image**:
    ```bash
    docker build -t customersupportagent-env:latest -f server/Dockerfile .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 8000:8000 customersupportagent-env:latest
    ```

3.  **Access the web interface**: Open `http://localhost:8000/web` in your browser.

### API Endpoints

-   `GET /tasks`: Enumerate tasks and action schema.
-   `GET /baseline`: Trigger and return baseline inference scores.
-   `POST /reset`: Initialize a new episode.
-   `POST /step`: Perform an action.
-   `GET /grader`: Get the score for the current episode.

## OpenEnv Compliance

Validated against the OpenEnv specification. Includes:
-   `openenv.yaml`
-   Typed Pydantic models for Action and Observation.
-   Standard `step()`, `reset()`, `state()` API.
