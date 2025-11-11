"""
Product Search Agent - Finds relevant parts based on user query
Enhanced with conversation history support AND category extraction
"""

import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.deepseek_client import DeepseekClient
from vector_store.embeddings import VectorStore
from database.models import SessionLocal, Part
from typing import List, Dict, Optional


class ProductSearchAgent:
    def __init__(self):
        self.client = DeepseekClient()
        # Fix: Use absolute path for vector store
        vector_store_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "vector_store",
            "chroma_db",
        )
        self.vector_store = VectorStore(db_path=vector_store_path)

    def extract_category_from_query(self, query: str) -> str:
        """
        Extract category (Refrigerator/Dishwasher) from user query

        Returns:
            "Refrigerator", "Dishwasher", or None
        """
        query_lower = query.lower()

        # Check for dishwasher keywords
        dishwasher_keywords = ["dishwasher", "dish washer", "dish-washer"]
        for keyword in dishwasher_keywords:
            if keyword in query_lower:
                print(f"[ProductSearch] Detected category: Dishwasher")
                return "Dishwasher"

        # Check for refrigerator keywords
        fridge_keywords = ["refrigerator", "fridge", "freezer", "ice maker"]
        for keyword in fridge_keywords:
            if keyword in query_lower:
                print(f"[ProductSearch] Detected category: Refrigerator")
                return "Refrigerator"

        return None

    def is_meta_query(self, query: str) -> bool:
        """
        Detect if user is asking about what types/categories exist
        rather than searching for specific parts
        """
        query_lower = query.lower()
        meta_keywords = [
            "what types",
            "what kind",
            "what categories",
            "all types",
            "all parts",
            "list all",
            "show all",
            "available types",
            "types available",
            "what do you have",
            "what's available",
            "what is available",
        ]
        return any(keyword in query_lower for keyword in meta_keywords)

    def extract_context_from_history(
        self, user_query: str, conversation_history: List[Dict]
    ) -> Dict:
        """
        Extract relevant context from conversation history for ambiguous queries

        Handles queries like:
        - "Show me similar parts" (needs to know which part)
        - "Find alternatives" (needs category context)
        - "What about the ice maker?" (needs appliance type)

        Returns:
            Dict with extracted context (part_number, category, keywords)
        """
        context = {
            "part_number": None,
            "part_name": None,
            "category": None,
            "model_number": None,
            "keywords": [],
        }

        if not conversation_history or len(conversation_history) == 0:
            return context

        # Look through recent conversation (last 4 messages)
        recent_messages = conversation_history[-4:]

        for message in recent_messages:
            content = message.get("content", "")

            # Extract part numbers (PS12345678)
            part_matches = re.findall(r"PS\d+", content, re.IGNORECASE)
            if part_matches and not context["part_number"]:
                context["part_number"] = part_matches[-1].upper()

            # Extract model numbers
            model_matches = re.findall(
                r"\b[A-Z]{2,4}[A-Z0-9]{5,}\b", content, re.IGNORECASE
            )
            if model_matches and not context["model_number"]:
                context["model_number"] = model_matches[-1].upper()

            # Extract categories
            if "refrigerator" in content.lower() and not context["category"]:
                context["category"] = "Refrigerator"
            elif "dishwasher" in content.lower() and not context["category"]:
                context["category"] = "Dishwasher"

            # Extract part names (common patterns)
            part_keywords = [
                "ice maker",
                "water inlet valve",
                "spray arm",
                "pump",
                "motor",
                "filter",
                "gasket",
                "seal",
                "door",
                "handle",
                "shelf",
                "drawer",
                "light",
                "thermostat",
                "compressor",
            ]

            for keyword in part_keywords:
                if keyword.lower() in content.lower():
                    context["keywords"].append(keyword)
                    if not context["part_name"]:
                        context["part_name"] = keyword

        # Remove duplicates from keywords
        context["keywords"] = list(set(context["keywords"]))

        print(f"[ProductSearch] Extracted context: {context}")
        return context

    def get_available_parts_by_category(self, category: str = None) -> Dict:
        """
        Get overview of available parts grouped by subcategory
        For meta-queries like "what types of parts are available"
        """
        db = SessionLocal()

        try:
            query = db.query(Part)

            if category:
                query = query.filter(Part.category == category)

            all_parts = query.all()

            # Group by subcategory
            parts_by_subcategory = {}
            for part in all_parts:
                subcategory = part.subcategory or "Other"
                if subcategory not in parts_by_subcategory:
                    parts_by_subcategory[subcategory] = []
                parts_by_subcategory[subcategory].append(part.to_dict())

            return {
                "category": category or "All",
                "subcategories": parts_by_subcategory,
                "total_parts": len(all_parts),
            }
        finally:
            db.close()

    def generate_meta_response(self, parts_overview: Dict, user_query: str) -> str:
        """
        Generate response for meta-queries about available parts
        """
        category = parts_overview["category"]
        subcategories = parts_overview["subcategories"]
        total_parts = parts_overview["total_parts"]

        # Build context about available parts
        parts_summary = f"Category: {category}\n"
        parts_summary += f"Total parts: {total_parts}\n\n"
        parts_summary += "Available by subcategory:\n"

        for subcategory, parts in subcategories.items():
            parts_summary += f"\n{subcategory} ({len(parts)} parts):\n"
            for part in parts[:2]:  # Show first 2 examples per subcategory
                parts_summary += f"  - {part['name']} (Part #{part['part_number']}) - ${part['price']}\n"
            if len(parts) > 2:
                parts_summary += f"  ... and {len(parts) - 2} more\n"

        system_prompt = f"""You are a helpful PartSelect.com customer service agent.
The user asked about what types of parts are available in our catalog.

Here's what we have:
{parts_summary}

Provide a friendly overview that:
1. Lists the main categories/types we have
2. Gives a few examples from each category
3. Encourages them to ask about specific parts or issues

Keep it organized and easy to scan."""

        response = self.client.chat_with_system(
            system_prompt=system_prompt, user_message=user_query, temperature=0.7
        )

        return response

    def search_parts(
        self, query: str, category: str = None, reference_part_number: str = None
    ) -> List[Dict]:
        """
        Search for parts using vector similarity

        Args:
            query: User's search query
            category: Optional category filter (Refrigerator/Dishwasher)
            reference_part_number: Optional part to find similar alternatives

        Returns:
            List of matching parts with details
        """
        print(f"[ProductSearch] Searching with category filter: {category}")

        # If searching for similar parts to a specific part
        if reference_part_number:
            db = SessionLocal()
            reference_part = (
                db.query(Part).filter(Part.part_number == reference_part_number).first()
            )

            if reference_part:
                # Search using the reference part's details
                search_query = f"{reference_part.name} {reference_part.category} {reference_part.subcategory or ''}"
                print(f"[ProductSearch] Searching for similar parts to: {search_query}")

                results = self.vector_store.search(
                    query=search_query,
                    n_results=6,  # Get more results
                    category_filter=reference_part.category,
                )

                # Filter out the reference part itself
                parts = []
                for metadata in results["metadatas"][0]:
                    part_number = metadata["part_number"]
                    if part_number != reference_part_number:  # Exclude reference
                        part = (
                            db.query(Part)
                            .filter(Part.part_number == part_number)
                            .first()
                        )
                        if part:
                            parts.append(part.to_dict())

                db.close()
                return parts[:5]  # Return top 5 alternatives

            db.close()

        # Standard search
        results = self.vector_store.search(
            query=query, n_results=5, category_filter=category
        )

        # Get full part details from SQL database
        db = SessionLocal()
        parts = []

        for metadata in results["metadatas"][0]:
            part_number = metadata["part_number"]
            part = db.query(Part).filter(Part.part_number == part_number).first()

            if part:
                parts.append(part.to_dict())

        db.close()
        return parts

    def generate_response(
        self, user_query: str, parts: List[Dict], context: Dict = None
    ) -> str:
        """
        Generate natural language response with part recommendations
        """
        if not parts:
            return "I couldn't find any parts matching your search. Could you provide more details about what you're looking for?"

        # Create context from parts
        parts_context = "\n\n".join(
            [
                f"Part {i+1}:\n"
                f"- Name: {part['name']}\n"
                f"- Part Number: {part['part_number']}\n"
                f"- Price: ${part['price']}\n"
                f"- Description: {part['description']}\n"
                f"- Category: {part['category']} - {part.get('subcategory', '')}"
                for i, part in enumerate(parts[:3])  # Top 3 results
            ]
        )

        # Add conversation context if available
        context_info = ""
        if context and any(context.values()):
            context_info = "\n\nConversation context:\n"
            if context.get("part_number"):
                context_info += f"- Previous part discussed: {context['part_number']}\n"
            if context.get("category"):
                context_info += f"- Appliance type: {context['category']}\n"
            if context.get("keywords"):
                context_info += f"- Keywords: {', '.join(context['keywords'][:3])}\n"

        system_prompt = f"""You are a helpful PartSelect.com customer service agent.
Based on the user's query and the parts found, provide a helpful response that:
1. Briefly explains what you found (acknowledge if this is a follow-up question)
2. Highlights the most relevant part(s)
3. Mentions key details like price and what the part does
4. Is friendly and conversational

Available parts:
{parts_context}
{context_info}

Keep your response concise (2-4 sentences) and natural."""

        response = self.client.chat_with_system(
            system_prompt=system_prompt, user_message=user_query, temperature=0.7
        )

        return response

    def handle_query(
        self,
        user_query: str,
        category: str = None,
        conversation_history: List[Dict] = None,
    ) -> Dict:
        """
        Main handler for product search queries with conversation history support

        Args:
            user_query: User's search query
            category: Optional category filter
            conversation_history: List of previous messages for context

        Returns:
            Dict with 'response' text and 'parts' list
        """
        # Extract context from conversation history
        context = self.extract_context_from_history(
            user_query, conversation_history or []
        )

        # Extract category from query if not provided
        if not category:
            category = self.extract_category_from_query(user_query)

        # Use category from context if still not found
        if not category and context.get("category"):
            category = context["category"]

        # Check if this is a meta-query about available parts
        if self.is_meta_query(user_query):
            print(f"[ProductSearch] Detected meta-query, listing available parts")
            parts_overview = self.get_available_parts_by_category(category)
            response_text = self.generate_meta_response(parts_overview, user_query)

            # Get sample parts to show
            sample_parts = []
            for subcategory, parts in parts_overview["subcategories"].items():
                sample_parts.extend(parts[:1])  # One from each subcategory

            return {
                "response": response_text,
                "parts": sample_parts[:5],  # Return up to 5 sample parts
                "agent": "product_search",
            }

        # Detect if this is a "similar parts" or follow-up query
        is_similar_query = any(
            keyword in user_query.lower()
            for keyword in ["similar", "alternative", "other", "different", "like this"]
        )

        # Enhance query with context for vague questions
        enhanced_query = user_query
        reference_part = None

        if is_similar_query and context.get("part_number"):
            # User asked for similar parts and we have a reference
            reference_part = context["part_number"]
            print(f"[ProductSearch] Finding alternatives to {reference_part}")
        elif len(user_query.split()) <= 3 and context.get("keywords"):
            # Short query - add context keywords
            enhanced_query = f"{user_query} {' '.join(context['keywords'][:2])}"
            print(f"[ProductSearch] Enhanced query: {enhanced_query}")

        # Search for parts
        parts = self.search_parts(
            enhanced_query, category=category, reference_part_number=reference_part
        )

        # Generate response with context
        response_text = self.generate_response(user_query, parts, context)

        return {
            "response": response_text,
            "parts": parts[:3],  # Return top 3 parts
            "agent": "product_search",
        }


# Test function
def test_product_search():
    agent = ProductSearchAgent()

    # Test with conversation history
    test_conversation = [
        {"role": "user", "content": "Is PS11739232 compatible with my Samsung fridge?"},
        {
            "role": "assistant",
            "content": "The water inlet valve PS11739232 is compatible...",
        },
    ]

    test_queries = [
        ("Show me ice makers for refrigerators", None, None),
        ("I need a dishwasher spray arm", None, None),
        ("Tell me what all types of dishwasher parts are available", None, None),
        ("Show me similar parts", None, test_conversation),  # Should use context
        ("What about alternatives?", None, test_conversation),  # Should use context
    ]

    print("Testing Product Search Agent (FINAL VERSION):\n")
    for query, category, history in test_queries:
        print(f"Query: {query}")
        if history:
            print(f"History: {len(history)} previous messages")
        result = agent.handle_query(
            query, category=category, conversation_history=history
        )
        print(f"Response: {result['response'][:150]}...")
        print(f"Parts found: {len(result['parts'])}")
        for part in result["parts"][:2]:
            print(f"  - {part['name']} ({part['part_number']}) - ${part['price']}")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    test_product_search()
