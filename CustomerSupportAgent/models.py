from typing import List, Optional, Literal, Dict, Any
from pydantic import Field
from openenv.core.env_server.types import Action, Observation

class CustomersupportagentAction(Action):

    action_type: Literal["categorize", "lookup_order", "reply"] = Field(
        ..., description="The type of action to perform"
    )
    category: Optional[str] = Field(None, description="Category for the ticket")
    order_id: Optional[str] = Field(None, description="Order ID to lookup")
    reply_text: Optional[str] = Field(None, description="The text of the reply to the customer")


class CustomersupportagentObservation(Observation):

    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_query: str = Field(..., description="The query from the customer")
    suggested_categories: List[str] = Field(
        default_factory=list, description="List of possible categories"
    )
    order_details: Optional[Dict[str, Any]] = Field(
        None, description="Details of the order if looked up"
    )
    history: List[Dict[str, Any]] = Field(
        default_factory=list, description="History of actions in this episode"
    )
    system_status: str = Field(
        default="Open", description="Current status of the ticket"
    )
    error_message: Optional[str] = Field(None, description="Error message if an action failed")
