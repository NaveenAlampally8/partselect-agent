"""
Compatibility Agent - Checks if parts are compatible with specific models
Enhanced with conversation history support and comprehensive error handling
"""

import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.deepseek_client import DeepseekClient
from database.models import SessionLocal, Part, Model
from typing import Dict, Optional, List


class CompatibilityAgent:
    def __init__(self):
        self.client = DeepseekClient()

    def extract_from_history(self, conversation_history: List[Dict]) -> Dict:
        """
        Extract part numbers and model numbers from conversation history

        Returns:
            Dict with part_number and model_number if found
        """
        context = {"part_number": None, "model_number": None}

        if not conversation_history:
            return context

        # Look through recent messages (last 4)
        recent_messages = conversation_history[-4:]

        for message in recent_messages:
            content = message.get("content", "")

            # Extract part numbers (PS12345678)
            if not context["part_number"]:
                part_match = re.search(r"PS\d+", content, re.IGNORECASE)
                if part_match:
                    context["part_number"] = part_match.group(0).upper()

            # Extract model numbers (e.g., WDT780SAEM1, WRS325SDHZ)
            if not context["model_number"]:
                model_match = re.search(
                    r"\b[A-Z]{2,4}[A-Z0-9]{5,}\b", content, re.IGNORECASE
                )
                if model_match:
                    # Exclude part numbers that look like model numbers
                    potential_model = model_match.group(0).upper()
                    if not potential_model.startswith("PS"):
                        context["model_number"] = potential_model

        print(f"[CompatibilityAgent] Extracted from history: {context}")
        return context

    def check_compatibility(self, part_number: str, model_number: str) -> Dict:
        """
        Check if a part is compatible with a model

        Returns:
            Dict with compatibility status and explanation
        """
        db = SessionLocal()

        # Find part
        part = db.query(Part).filter(Part.part_number == part_number).first()

        if not part:
            db.close()
            return {
                "compatible": None,
                "confidence": "high",
                "explanation": f"Part number {part_number} not found in our database.",
                "error": "PART_NOT_FOUND",
            }

        # Check if model exists in compatible models
        compatible_model_numbers = [m.model_number for m in part.compatible_models]

        is_compatible = model_number.upper() in [
            m.upper() for m in compatible_model_numbers
        ]

        db.close()

        if is_compatible:
            return {
                "compatible": True,
                "confidence": "high",
                "explanation": f"Yes! The {part.name} (part #{part_number}) is compatible with model {model_number}.",
                "part": part.to_dict(),
            }
        else:
            # Not compatible or unknown
            return {
                "compatible": False,
                "confidence": "medium",
                "explanation": f"The {part.name} (part #{part_number}) is not listed as compatible with model {model_number}.",
                "part": part.to_dict(),
                "compatible_models": compatible_model_numbers[:5],  # Show first 5
            }

    def extract_part_and_model(self, user_query: str) -> Dict[str, Optional[str]]:
        """
        Extract part number and model number from user query using regex first, then LLM
        """
        # Try regex first (faster)
        part_match = re.search(r"PS\d+", user_query, re.IGNORECASE)
        part_number = part_match.group(0).upper() if part_match else None

        # Model number: 2-4 letters followed by 5+ alphanumeric characters
        model_match = re.search(
            r"\b[A-Z]{2,4}[A-Z0-9]{5,}\b", user_query, re.IGNORECASE
        )
        model_number = model_match.group(0).upper() if model_match else None

        # If regex found both, return them
        if part_number and model_number:
            return {"part_number": part_number, "model_number": model_number}

        # Fallback to LLM if regex didn't find everything
        system_prompt = """Extract the part number and model number from the user's query.

Part numbers typically look like: PS11752778, PS11739232, etc.
Model numbers typically look like: WDT780SAEM1, WRF555SDFZ, KDFE104HPS, etc.

Respond in this EXACT format:
PART_NUMBER: <part_number or NONE>
MODEL_NUMBER: <model_number or NONE>

Examples:
User: "Is part PS11752778 compatible with WDT780SAEM1?"
Response:
PART_NUMBER: PS11752778
MODEL_NUMBER: WDT780SAEM1

User: "Will this work with my dishwasher model KDFE104HPS?"
Response:
PART_NUMBER: NONE
MODEL_NUMBER: KDFE104HPS"""

        response = self.client.chat_with_system(
            system_prompt=system_prompt, user_message=user_query, temperature=0.3
        )

        # Parse response
        extracted_part = part_number  # Keep regex result if found
        extracted_model = model_number  # Keep regex result if found

        for line in response.strip().split("\n"):
            if line.startswith("PART_NUMBER:"):
                value = line.split(":", 1)[1].strip()
                if value != "NONE" and not extracted_part:
                    extracted_part = value
            elif line.startswith("MODEL_NUMBER:"):
                value = line.split(":", 1)[1].strip()
                if value != "NONE" and not extracted_model:
                    extracted_model = value

        return {"part_number": extracted_part, "model_number": extracted_model}

    def generate_response(self, compatibility_result: Dict, user_query: str) -> str:
        """
        Generate natural language response about compatibility
        """
        # Handle error cases with specific messages
        if compatibility_result.get("error") == "PART_NOT_FOUND":
            return compatibility_result["explanation"]

        compatible = compatibility_result["compatible"]
        part = compatibility_result.get("part", {})

        if compatible:
            # Positive response
            response = f"✅ **Great news!** {compatibility_result['explanation']}\n\n"
            response += f"💰 **Price:** ${part.get('price', 'N/A')}\n"
            response += f"🔧 **Installation:** {part.get('installation_difficulty', 'Unknown')} difficulty\n\n"
            response += "Would you like installation instructions for this part?"
            return response
        else:
            # Negative response
            response = f"❌ {compatibility_result['explanation']}\n\n"

            if compatibility_result.get("compatible_models"):
                response += "**This part is compatible with models like:**\n"
                for model in compatibility_result["compatible_models"][:3]:
                    response += f"- {model}\n"
                response += "\n"

            response += "**What to do next:**\n"
            response += "1. Double-check your model number (usually on a sticker inside the door or on the back)\n"
            response += "2. Try searching: 'Show me parts for [your model]'\n"
            response += "3. Contact support for help finding the right part\n\n"
            response += f"💰 Part price: ${part.get('price', 'N/A')}"

            return response

    def handle_query(
        self,
        user_query: str,
        part_number: str = None,
        model_number: str = None,
        conversation_history: List[Dict] = None,
    ) -> Dict:
        """
        Main handler for compatibility queries with conversation history support

        Args:
            user_query: User's query
            part_number: Optional part number
            model_number: Optional model number
            conversation_history: List of previous messages for context

        Returns:
            Dict with compatibility result
        """
        # Extract from current query
        if not part_number or not model_number:
            extracted = self.extract_part_and_model(user_query)
            part_number = part_number or extracted["part_number"]
            model_number = model_number or extracted["model_number"]

        # If still missing, try to get from conversation history
        if (not part_number or not model_number) and conversation_history:
            context = self.extract_from_history(conversation_history)
            part_number = part_number or context["part_number"]
            model_number = model_number or context["model_number"]

            if context["part_number"] or context["model_number"]:
                print(
                    f"[CompatibilityAgent] Used context - Part: {part_number}, Model: {model_number}"
                )

        # Error 1: Missing both identifiers
        if not part_number and not model_number:
            return {
                "response": "I need both a **part number** (like PS11752778) and a **model number** (like WDT780SAEM1) to check compatibility.\n\n"
                + "**Example:** 'Is part PS11752778 compatible with model WDT780SAEM1?'\n\n"
                + "Your model number is usually found on a sticker:\n"
                + "- Inside the refrigerator/dishwasher door\n"
                + "- On the back of the appliance\n"
                + "- On the side wall inside the unit",
                "agent": "compatibility",
                "compatible": None,
                "error": "MISSING_BOTH",
            }

        # Error 2: Missing part number
        if not part_number:
            return {
                "response": f"I found your model number **{model_number}**, but I need a **part number** too.\n\n"
                + "**Example:** 'Is PS11752778 compatible with {model_number}?'\n\n"
                + "Or you can search for compatible parts: 'Show me parts for {model_number}'",
                "agent": "compatibility",
                "compatible": None,
                "model_number": model_number,
                "error": "MISSING_PART_NUMBER",
            }

        # Error 3: Missing model number
        if not model_number:
            return {
                "response": f"I found part number **{part_number}**, but I need your **model number** too.\n\n"
                + "**Example:** 'Is {part_number} compatible with WDT780SAEM1?'\n\n"
                + "Your model number is on a sticker:\n"
                + "- Inside the door\n"
                + "- On the back panel\n"
                + "- Inside the unit",
                "agent": "compatibility",
                "compatible": None,
                "part_number": part_number,
                "error": "MISSING_MODEL_NUMBER",
            }

        # Check compatibility
        result = self.check_compatibility(part_number, model_number)

        # Error 4: Part not found
        if result.get("error") == "PART_NOT_FOUND":
            return {
                "response": f"I couldn't find part number **{part_number}** in our catalog.\n\n"
                + "**Please check:**\n"
                + "1. Part number is correct (format: PS12345678)\n"
                + "2. Try searching: 'Show me ice makers' or 'Show me dishwasher parts'\n\n"
                + "If you're sure it's correct, this part may not be in our current catalog.",
                "agent": "compatibility",
                "compatible": None,
                "part_number": part_number,
                "model_number": model_number,
                "error": "PART_NOT_FOUND",
            }

        # Generate natural language response
        try:
            response_text = self.generate_response(result, user_query)
        except Exception as e:
            print(f"[CompatibilityAgent] LLM error: {e}")
            # Fallback response
            if result["compatible"]:
                response_text = f"✅ Yes! Part {part_number} is compatible with model {model_number}."
            else:
                response_text = f"❌ Part {part_number} is not listed as compatible with model {model_number}."

        return {
            "response": response_text,
            "compatible": result["compatible"],
            "part_number": part_number,
            "model_number": model_number,
            "part": result.get("part"),
            "agent": "compatibility",
        }


# Test function
def test_compatibility():
    agent = CompatibilityAgent()

    # Test with conversation history
    test_conversation = [
        {"role": "user", "content": "Is PS11739232 compatible with WRS325SDHZ?"},
        {"role": "assistant", "content": "Yes, it's compatible!"},
    ]

    test_queries = [
        ("Is part PS11752778 compatible with my WDT780SAEM1 model?", None),
        ("Will PS11739232 work with model WRS325SDHZ?", None),
        ("Is PS11752778 compatible?", None),
        ("Will this work with WDT780SAEM1?", test_conversation),  # Should use history
        ("What about with my Samsung fridge?", test_conversation),  # Should use history
    ]

    print("Testing Compatibility Agent with Context:\n")
    for query, history in test_queries:
        print(f"Query: {query}")
        if history:
            print(f"History: {len(history)} messages")
        result = agent.handle_query(query, conversation_history=history)
        print(f"Response: {result['response'][:200]}...")
        print(f"Compatible: {result.get('compatible', 'N/A')}")
        print(f"Error: {result.get('error', 'None')}")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    test_compatibility()
