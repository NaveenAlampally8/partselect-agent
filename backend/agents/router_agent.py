"""
Router Agent - Determines which specialized agent should handle the query
"""

import re
from typing import List, Dict
from agents.deepseek_client import DeepseekClient


class RouterAgent:
    def __init__(self):
        self.client = DeepseekClient()

        self.system_prompt = """You are a routing agent for PartSelect.com chat support.
Your job is to classify user queries into ONE of these categories:

1. PRODUCT_SEARCH - User wants to find parts or browse products
   Examples: "show me ice makers", "what dishwasher parts do you have"

2. COMPATIBILITY_CHECK - User wants to know if a part works with their model
   Examples: "is this part compatible with my model X", "will part Y fit my dishwasher Z"

3. INSTALLATION_HELP - User needs help installing a part OR asking about installation time/difficulty
   Examples: 
   - "how do I install part X"
   - "installation instructions for Y"
   - "how long does installation take" (if context suggests a specific part)
   - "is this part difficult to install"
   - "what tools do I need"

4. TROUBLESHOOTING - User has a broken appliance and needs help diagnosing
   Examples: "my ice maker isn't working", "dishwasher won't drain", "fridge is too warm"

5. ORDER_SUPPORT - User has questions about orders, shipping, returns
   Examples: "where is my order", "how do I return this", "shipping information"

6. OUT_OF_SCOPE - Question is not related to refrigerator/dishwasher parts
   Examples: "what's the weather", "tell me a joke", "help with my oven"

Respond with ONLY the category name (e.g., "PRODUCT_SEARCH"). No explanation needed."""

    def route(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Route user message to appropriate category with conversation context

        Args:
            user_message: Current user query
            conversation_history: Previous messages for context

        Returns:
            Category name: PRODUCT_SEARCH, COMPATIBILITY_CHECK, INSTALLATION_HELP,
                        TROUBLESHOOTING, ORDER_SUPPORT, or OUT_OF_SCOPE
        """
        query_lower = user_message.lower()

        # Pre-routing rules for better consistency

        # 1. Handle time/duration queries with context awareness
        if any(
            keyword in query_lower
            for keyword in [
                "how long",
                "how much time",
                "time estimate",
                "duration",
                "take to install",
            ]
        ):
            # Check if there's a part number in the query
            has_part_number = bool(re.search(r"PS\d+", user_message, re.IGNORECASE))

            # Check conversation history for recent part discussion
            has_context = False
            if conversation_history:
                recent_messages = conversation_history[-3:]
                for msg in recent_messages:
                    content = msg.get("content", "")
                    if re.search(r"PS\d+", content, re.IGNORECASE):
                        has_context = True
                        print(f"[Router] Found part context in history for time query")
                        break

            if has_part_number or has_context:
                # Route to installation - they're asking about a specific part
                print(
                    f"[Router] Query routed to: INSTALLATION_HELP (time query with context)"
                )
                return "INSTALLATION_HELP"
            # If no context, let LLM decide (might be general question)

        # 2. Handle explicit installation queries
        if any(
            keyword in query_lower
            for keyword in ["install", "installation", "replace", "how do i"]
        ) and re.search(r"PS\d+", user_message, re.IGNORECASE):
            print(
                f"[Router] Query routed to: INSTALLATION_HELP (explicit install query)"
            )
            return "INSTALLATION_HELP"

        # 3. Use LLM for ambiguous cases
        response = self.client.chat_with_system(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.3,  # Low temperature for consistent routing
        )

        # Clean up response
        category = response.strip().upper()

        # Validate category
        valid_categories = [
            "PRODUCT_SEARCH",
            "COMPATIBILITY_CHECK",
            "INSTALLATION_HELP",
            "TROUBLESHOOTING",
            "ORDER_SUPPORT",
            "OUT_OF_SCOPE",
        ]

        if category not in valid_categories:
            # Default to product search if unclear
            category = "PRODUCT_SEARCH"

        print(f"[Router] Query routed to: {category}")
        return category


# Test function
def test_router():
    router = RouterAgent()

    test_queries = [
        "How can I install part number PS11752778?",
        "Is this part compatible with my WDT780SAEM1 model?",
        "The ice maker on my Whirlpool fridge is not working",
        "Show me all dishwasher spray arms",
        "What's the weather today?",
    ]

    print("Testing Router Agent:\n")
    for query in test_queries:
        category = router.route(query)
        print(f"Query: {query}")
        print(f"Route: {category}\n")


if __name__ == "__main__":
    test_router()
