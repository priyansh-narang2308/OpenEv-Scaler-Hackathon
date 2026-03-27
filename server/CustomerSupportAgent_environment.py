import json
from uuid import uuid4
from typing import Dict, Any, List, Optional
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from models import CustomersupportagentAction, CustomersupportagentObservation


# Mock Order Database
ORDERS = {
    "ORD-12345": {"item": "Quantum Toaster", "status": "Shipped", "delivery_date": "2024-03-20"},
    "ORD-67890": {"item": "Solar Kettle", "status": "Processing", "delivery_date": "TBD"},
    "ORD-99999": {"item": "Anti-Gravity Boots", "status": "Delivered", "delivery_date": "2024-03-15"},
}

CATEGORIES = ["Shipping", "Returns", "Technical Support", "Billing"]

# Define Tasks for different scenarios
TASKS = [
    {
        "id": "easy_shipping",
        "description": "Categorize the following customer query: 'Where is my package? I ordered it last week.'",
        "query": "Where is my package? I ordered it last week.",
        "difficulty": "easy",
        "correct_category": "Shipping",
    },
    {
        "id": "medium_return",
        "description": "Categorize and reply to: 'I want to return my Solar Kettle, it's not working properly.' Provide return instructions.",
        "query": "I want to return my Solar Kettle, it's not working properly.",
        "difficulty": "medium",
        "correct_category": "Returns",
        "required_reply_keywords": ["return", "instructions"],
    },
    {
        "id": "hard_order_lookup",
        "description": "Lookup order #ORD-12345, categorize the query 'Where is my order #ORD-12345?', and provide a specific status update to the customer.",
        "query": "Where is my order #ORD-12345?",
        "difficulty": "hard",
        "correct_category": "Shipping",
        "required_order_id": "ORD-12345",
        "required_reply_keywords": ["Shipped", "2024-03-20"],
    },
]


class CustomersupportagentState(State):
    """Customer Support specific state."""

    task_index: int = 0
    history: List[Dict[str, Any]] = []
    current_order: Optional[Dict[str, Any]] = None
    category_assigned: Optional[str] = None
    reply_sent: bool = False


class CustomersupportagentEnvironment(Environment):
    """
    Customer Support Agent Environment.
    Handles customer support tasks like categorization, order lookup, and drafting replies.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self, task_index: int = 0):
        """Initialize with a specific task."""
        self._state = CustomersupportagentState(
            episode_id=str(uuid4()),
            step_count=0,
            task_index=task_index % len(TASKS),
            history=[],
            current_order=None,
            category_assigned=None,
            reply_sent=False,
        )
        self._task_index = self._state.task_index
        self.current_task = TASKS[self._task_index]

    def reset(self, task_index: Optional[int] = None) -> CustomersupportagentObservation:
        """Reset the environment to the beginning of the task."""
        if task_index is not None:
            self._task_index = task_index % len(TASKS)

        self.current_task = TASKS[self._task_index]
        self._state = CustomersupportagentState(
            episode_id=str(uuid4()),
            step_count=0,
            task_index=self._task_index,
            history=[],
            current_order=None,
            category_assigned=None,
            reply_sent=False,
        )

        return self._get_observation()

    def _get_observation(self) -> CustomersupportagentObservation:
        return CustomersupportagentObservation(
            ticket_id=f"TKT-{self._state.episode_id[:8]}",
            customer_query=self.current_task["query"],
            suggested_categories=CATEGORIES,
            order_details=self._state.current_order,
            history=self._state.history,
            system_status=self._get_system_status(),
        )

    def _get_system_status(self) -> str:
        if self._state.reply_sent:
            return "Resolved"
        if self._state.category_assigned:
            return "Categorized, awaiting reply"
        return "New"

    def step(self, action: CustomersupportagentAction) -> CustomersupportagentObservation:  # type: ignore[override]
        self._state.step_count += 1
        reward_val = 0.0
        done = False

        self._state.history.append({"step": self._state.step_count, "action": action.model_dump()})

        if action.action_type == "categorize":
            if action.category:
                self._state.category_assigned = action.category
                if action.category == self.current_task.get("correct_category"):
                    reward_val += 0.3
            else:
                self._state.history.append({"error": "No category provided"})

        elif action.action_type == "lookup_order":
            order_id = action.order_id
            if order_id and order_id in ORDERS:
                self._state.current_order = ORDERS[order_id]
                reward_val += 0.2
            else:
                self._state.history.append({"error": f"Order {order_id} not found"})

        elif action.action_type == "reply":
            if action.reply_text:
                self._state.reply_sent = True
                done = True
                reward_val += self._calculate_final_reward(action.reply_text)
            else:
                self._state.history.append({"error": "No reply text provided"})

        if self._state.step_count >= 10:
            done = True

        obs = self._get_observation()
        obs.reward = reward_val
        obs.done = done

        return obs

    def _calculate_final_reward(self, reply_text: str) -> float:
        score = 0.0
        if self._state.category_assigned == self.current_task.get("correct_category"):
            score += 0.3
        else:
            score -= 0.1

        required_keywords = self.current_task.get("required_reply_keywords", [])
        if required_keywords:
            matches = [kw.lower() in reply_text.lower() for kw in required_keywords]
            if any(matches):
                score += (sum(matches) / len(matches)) * 0.4
        elif self.current_task["difficulty"] == "easy":
            score += 0.4

        if self.current_task["difficulty"] == "hard":
            required_id = self.current_task.get("required_order_id")
            if self._state.current_order and self._state.current_order == ORDERS.get(required_id):
                score += 0.3
            else:
                score -= 0.2

        return max(0.0, min(1.0, score))

    def get_grader_score(self) -> float:
        if not self._state.reply_sent:
            return 0.0
        last_action = next((h["action"] for h in reversed(self._state.history) if h["action"]["action_type"] == "reply"), None)
        if last_action:
            return self._calculate_final_reward(last_action["reply_text"])
        return 0.0

    @property
    def state(self) -> State:
        return self._state
