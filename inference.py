import os
import json
import asyncio
import re
from typing import List, Dict, Any
from openai import OpenAI
from models import CustomersupportagentAction, CustomersupportagentObservation
from server.CustomerSupportAgent_environment import TASKS, CustomersupportagentEnvironment

# Requirement: Use API_BASE_URL, MODEL_NAME, and HF_TOKEN
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize OpenAI client as per requirements
# If HF_TOKEN is provided, use it as the API key. 
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN or "no-token-provided"
)

async def run_inference_on_task(task_index: int) -> float:
    env = CustomersupportagentEnvironment(task_index=task_index)
    obs = env.reset()
    
    # 1. Categorize
    prompt = (
        f"Customer Query: {obs.customer_query}\n"
        f"Categories: {obs.suggested_categories}\n"
        f"Task: Pick the best category from the list. Return ONLY the category name."
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        category_resp = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling LLM for categorization: {e}")
        # Fallback to a simple heuristic
        if "package" in obs.customer_query or "order" in obs.customer_query:
            category_resp = "Shipping"
        elif "return" in obs.customer_query:
            category_resp = "Returns"
        else:
            category_resp = "Technical Support"

    obs = env.step(CustomersupportagentAction(action_type="categorize", category=category_resp))
    
    # 2. Lookup Order (if applicable)
    if "#ORD-" in obs.customer_query:
        match = re.search(r"ORD-\d+", obs.customer_query)
        if match:
            order_id = match.group(0)
            obs = env.step(CustomersupportagentAction(action_type="lookup_order", order_id=order_id))
    
    # 3. Reply
    reply_prompt = (
        f"Query: {obs.customer_query}\n"
        f"Order Info: {obs.order_details}\n"
        f"Category: {category_resp}\n"
        f"Task: Write a helpful reply to the customer. Be concise."
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": reply_prompt}]
        )
        reply_resp = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling LLM for reply: {e}")
        reply_resp = "Thank you for reaching out. We are looking into your request."

    obs = env.step(CustomersupportagentAction(action_type="reply", reply_text=reply_resp))
    
    return obs.reward

async def run_all_tasks():
    scores = {}
    total_score = 0
    for i in range(len(TASKS)):
        print(f"Running task {i+1}/{len(TASKS)}: {TASKS[i]['id']}...")
        score = await run_inference_on_task(i)
        scores[TASKS[i]["id"]] = score
        total_score += score
        print(f"Score for {TASKS[i]['id']}: {score}")
    
    avg_score = total_score / len(TASKS) if TASKS else 0
    return {
        "individual_scores": scores,
        "average_score": avg_score
    }

if __name__ == "__main__":
    if not API_BASE_URL or not MODEL_NAME:
        print("Warning: API_BASE_URL or MODEL_NAME environment variables are not set.")
    
    result = asyncio.run(run_all_tasks())
    print("\n--- FINAL SCORES ---")
    print(json.dumps(result, indent=2))
