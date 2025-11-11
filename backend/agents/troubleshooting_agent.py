"""
Troubleshooting Agent - Helps diagnose appliance problems
Enhanced with conversation history support
"""

import sys
import os
import re

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from agents.deepseek_client import DeepseekClient
from vector_store.embeddings import VectorStore
from database.models import SessionLocal, Part
from typing import List, Dict


class TroubleshootingAgent:
    def __init__(self):
        self.client = DeepseekClient()

        # Use absolute path for vector store
        vector_db_path = os.path.join(parent_dir, "vector_store", "chroma_db")
        print(f"[TroubleshootingAgent] Loading vector store from: {vector_db_path}")
        self.vector_store = VectorStore(db_path=vector_db_path)

    def extract_context_from_history(
        self, user_query: str, conversation_history: List[Dict]
    ) -> Dict:
        """
        Extract relevant context from conversation history

        Returns:
            Dict with context information (appliance type, previous parts, etc.)
        """
        context = {"appliance_type": None, "symptoms": [], "previous_parts": []}

        if not conversation_history:
            return context

        # Look through recent messages
        recent_messages = conversation_history[-4:]

        for message in recent_messages:
            content = message.get("content", "")

            # Extract appliance type
            if "refrigerator" in content.lower() or "fridge" in content.lower():
                context["appliance_type"] = "Refrigerator"
            elif "dishwasher" in content.lower():
                context["appliance_type"] = "Dishwasher"

            # Extract part numbers mentioned
            part_matches = re.findall(r"PS\d+", content, re.IGNORECASE)
            for part in part_matches:
                if part.upper() not in context["previous_parts"]:
                    context["previous_parts"].append(part.upper())

            # Extract common symptoms
            symptom_keywords = [
                "not working",
                "leaking",
                "noisy",
                "won't drain",
                "not cooling",
                "not heating",
                "not spinning",
                "making noise",
                "not starting",
            ]
            for symptom in symptom_keywords:
                if symptom in content.lower() and symptom not in context["symptoms"]:
                    context["symptoms"].append(symptom)

        print(f"[TroubleshootingAgent] Extracted context: {context}")
        return context

    def diagnose_problem(
        self, user_query: str, appliance_type: str = None
    ) -> List[Dict]:
        """
        Find parts that might fix the user's problem

        Args:
            user_query: User's problem description
            appliance_type: Optional filter for Refrigerator/Dishwasher
        """
        print(f"[TroubleshootingAgent] Diagnosing: {user_query}")

        # Search for parts based on symptoms
        results = self.vector_store.search(
            query=user_query, n_results=5, category_filter=appliance_type
        )

        print(
            f"[TroubleshootingAgent] Vector search returned {len(results['metadatas'][0])} results"
        )

        # Get full part details
        db = SessionLocal()
        parts = []

        try:
            for metadata in results["metadatas"][0]:
                part_number = metadata["part_number"]
                part = db.query(Part).filter(Part.part_number == part_number).first()

                if part:
                    parts.append(part.to_dict())
                    print(f"[TroubleshootingAgent] Found part: {part.name}")
        finally:
            db.close()

        return parts

    def generate_response(
        self, user_query: str, parts: List[Dict], context: Dict = None
    ) -> str:
        """
        Generate troubleshooting advice with part recommendations
        """
        if not parts:
            return "I understand you're having an issue. Could you provide more details about what's happening with your appliance?"

        # Create context from parts
        parts_context = "\n\n".join(
            [
                f"Possible Solution {i+1}: {part['name']}\n"
                f"- Part Number: {part['part_number']}\n"
                f"- Price: ${part['price']}\n"
                f"- Common Symptoms: {', '.join(part.get('common_symptoms', []))}\n"
                f"- Description: {part['description']}"
                for i, part in enumerate(parts[:3])
            ]
        )

        # Add conversation context
        context_info = ""
        if context and any(context.values()):
            context_info = "\n\nConversation context:\n"
            if context.get("appliance_type"):
                context_info += f"- Appliance: {context['appliance_type']}\n"
            if context.get("symptoms"):
                context_info += f"- Previous symptoms mentioned: {', '.join(context['symptoms'][:2])}\n"

        system_prompt = f"""You are a helpful PartSelect.com technician assistant.
Based on the user's problem, provide:
1. A brief diagnosis of what might be wrong
2. Recommend the most likely part(s) that need replacement
3. Explain why this part might be the issue
4. Be empathetic and helpful

Available parts that might help:
{parts_context}
{context_info}

Keep your response conversational and not too technical. Structure it clearly with the diagnosis first, then recommendations."""

        response = self.client.chat_with_system(
            system_prompt=system_prompt, user_message=user_query, temperature=0.7
        )

        return response

    def handle_query(
        self, user_query: str, conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Main handler for troubleshooting queries with conversation history support

        Args:
            user_query: User's problem description
            conversation_history: List of previous messages for context

        Returns:
            Dict with diagnosis and suggested parts
        """
        # Extract context from conversation history
        context = self.extract_context_from_history(
            user_query, conversation_history or []
        )

        # Use appliance type from context if available
        appliance_type = context.get("appliance_type")

        # Find relevant parts
        parts = self.diagnose_problem(user_query, appliance_type=appliance_type)

        # Generate response with context
        response_text = self.generate_response(user_query, parts, context)

        return {
            "response": response_text,
            "suggested_parts": parts[:3],
            "agent": "troubleshooting",
        }


# Test function
def test_troubleshooting():
    agent = TroubleshootingAgent()

    # Test with conversation history
    test_conversation = [
        {"role": "user", "content": "I have a Whirlpool refrigerator"},
        {
            "role": "assistant",
            "content": "Great! How can I help with your refrigerator?",
        },
    ]

    test_queries = [
        ("The ice maker on my Whirlpool fridge is not working", None),
        ("My dishwasher isn't draining water", None),
        ("It's making a strange noise", test_conversation),  # Should use context
        ("What could be wrong?", test_conversation),  # Should use context
    ]

    print("\n" + "=" * 80)
    print("Testing Troubleshooting Agent with Context")
    print("=" * 80 + "\n")

    for query, history in test_queries:
        print(f"Problem: {query}")
        if history:
            print(f"History: {len(history)} messages")
        result = agent.handle_query(query, conversation_history=history)
        print(f"Response: {result['response'][:200]}...")
        print(f"\nSuggested parts: {len(result['suggested_parts'])}")
        for part in result["suggested_parts"]:
            print(f"  - {part['name']} ({part['part_number']}) - ${part['price']}")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    test_troubleshooting()
