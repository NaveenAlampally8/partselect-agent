import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.deepseek_client import DeepseekClient
from database.models import SessionLocal, Part
from typing import Dict, Optional, List


class InstallationAgent:
    def __init__(self):
        self.client = DeepseekClient()
        # Initialize vector store for part searching
        try:
            from vector_store.embeddings import VectorStore

            vector_store_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "vector_store",
                "chroma_db",
            )
            self.vector_store = VectorStore(db_path=vector_store_path)
        except Exception as e:
            print(
                f"[InstallationAgent] Warning: Could not initialize vector store: {e}"
            )
            self.vector_store = None

    def find_relevant_parts(self, user_query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for relevant parts based on user query
        Used when user doesn't provide a part number
        """
        if not self.vector_store:
            return []

        try:
            # Extract category from query
            query_lower = user_query.lower()
            category = None
            if any(kw in query_lower for kw in ["dishwasher", "dish washer"]):
                category = "Dishwasher"
            elif any(kw in query_lower for kw in ["refrigerator", "fridge", "freezer"]):
                category = "Refrigerator"

            # Search vector store
            results = self.vector_store.search(
                query=user_query, n_results=n_results, category_filter=category
            )

            # Get full part details from database
            db = SessionLocal()
            parts = []
            for metadata in results["metadatas"][0]:
                part_number = metadata["part_number"]
                part = db.query(Part).filter(Part.part_number == part_number).first()
                if part:
                    parts.append(part.to_dict())
            db.close()

            return parts
        except Exception as e:
            print(f"[InstallationAgent] Error finding relevant parts: {e}")
            return []

    def get_installation_instructions(self, part_number: str) -> Optional[Dict]:
        """
        Get installation instructions for a specific part
        """
        db = SessionLocal()
        part = db.query(Part).filter(Part.part_number == part_number).first()
        db.close()

        if not part:
            return None

        return {
            "part": part.to_dict(),
            "steps": part.installation_steps or [],
            "difficulty": part.installation_difficulty or "Unknown",
        }

    def extract_part_number(self, user_query: str) -> Optional[str]:
        """
        Extract part number from user query using regex first, then LLM
        """
        # Try regex first (faster)
        match = re.search(r"PS\d+", user_query, re.IGNORECASE)
        if match:
            return match.group(0).upper()

        # Fallback to LLM if regex fails
        system_prompt = """Extract the part number from the user's query.
Part numbers look like: PS11752778, PS11739232, etc.

Respond with ONLY the part number, or "NONE" if no part number is found.

Examples:
User: "How do I install PS11752778?"
Response: PS11752778

User: "How do I install the ice maker?"
Response: NONE"""

        response = self.client.chat_with_system(
            system_prompt=system_prompt, user_message=user_query, temperature=0.3
        )

        part_number = response.strip()
        return None if part_number == "NONE" else part_number

    def extract_part_from_history(
        self, conversation_history: List[Dict]
    ) -> Optional[str]:
        """
        Extract most recently discussed part number from conversation history
        """
        if not conversation_history:
            return None

        # Check last 4 messages for part numbers
        for message in reversed(conversation_history[-4:]):
            content = message.get("content", "")
            match = re.search(r"PS\d+", content, re.IGNORECASE)
            if match:
                part_num = match.group(0).upper()
                print(f"[InstallationAgent] Found part from history: {part_num}")
                return part_num

        return None

    def handle_time_estimate_query(
        self,
        user_query: str,
        part_number: str = None,
        conversation_history: List[Dict] = None,
    ) -> Dict:
        """
        Handle queries specifically about installation time/duration
        """
        # If no part number, need clarification
        if not part_number:
            return {
                "response": "I'd be happy to give you a time estimate! Which part are you asking about?\n\n"
                "**General time estimates by difficulty:**\n"
                "- 🟢 **Easy:** 10-20 minutes (spray arms, baskets, filters, handles)\n"
                "- 🟡 **Moderate:** 30-60 minutes (valves, motors, door parts, thermostats)\n"
                "- 🔴 **Difficult:** 1-2 hours (pumps, control boards, heating elements)\n\n"
                "💡 Tell me the part number or name, and I'll give you a specific estimate!",
                "agent": "installation",
                "error": "NO_PART_NUMBER_FOR_TIME_ESTIMATE",
            }

        # Get part details
        instructions = self.get_installation_instructions(part_number)

        if not instructions:
            return {
                "response": f"I couldn't find part number **{part_number}** to provide a time estimate.\n\n"
                "Could you double-check the part number?",
                "agent": "installation",
                "error": "PART_NOT_FOUND",
            }

        part = instructions["part"]
        difficulty = instructions.get("difficulty", "Unknown")
        steps = instructions.get("steps", [])

        # Determine time estimate based on difficulty
        time_estimates = {
            "Easy": "10-20 minutes",
            "Moderate": "30-60 minutes",
            "Difficult": "1-2 hours",
        }

        estimated_time = time_estimates.get(difficulty, "30-45 minutes")

        # Build response
        response = f"**Installation Time for {part['name']}**\n\n"
        response += f"⏱️ **Estimated Time:** {estimated_time}\n"
        response += f"🔧 **Difficulty:** {difficulty}\n"
        response += f"📋 **Steps:** {len(steps)} steps to complete\n\n"

        # Add context based on difficulty
        if difficulty == "Easy":
            response += "This is a straightforward repair that most people can complete quickly. You'll mainly be removing the old part and installing the new one."
        elif difficulty == "Moderate":
            response += "This repair requires some disassembly and careful reconnection of components. Take your time to ensure everything is properly connected."
        elif difficulty == "Difficult":
            response += "This is a more complex repair that requires careful attention to detail. Consider taking photos of wire connections before disconnecting."

        response += f"\n\n💡 **Want detailed instructions?** Ask: 'How do I install {part_number}?'"

        return {
            "response": response,
            "part": part,
            "difficulty": difficulty,
            "estimated_time": estimated_time,
            "agent": "installation",
        }

    def generate_response(self, instructions: Dict, user_query: str) -> str:
        """
        Generate natural language installation guide
        """
        part = instructions["part"]
        steps = instructions["steps"]
        difficulty = instructions["difficulty"]

        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])

        time_estimates = {
            "Easy": "10-20 minutes",
            "Moderate": "30-60 minutes",
            "Difficult": "1-2 hours",
        }
        estimated_time = time_estimates.get(difficulty, "30-45 minutes")

        system_prompt = f"""You are a helpful PartSelect.com installation guide.
        The user asked how to install a SPECIFIC part they already have.

        Part Information:
        - Name: {part['name']}
        - Part Number: {part['part_number']}
        - Category: {part['category']}
        - Difficulty: {difficulty}
        - Estimated Time: {estimated_time}
        - Installation Steps:
        {steps_text}

        Provide a complete installation guide with this structure:

        ## 1. About the Part
        Brief 1-2 sentence explanation of what this part does.

        ## 2. Difficulty & Time Estimate
        - **Difficulty:** {difficulty}
        - **Time:** About {estimated_time}

        ## 3. Installation Steps
        Provide the numbered steps clearly (use the exact steps above).

        ## 4. Safety Reminder
        Always include a safety note about disconnecting power.

        CRITICAL RULES:
        - Do NOT suggest alternative parts - the user already has this specific part
        - Do NOT ask if they want to see similar parts
        - Focus ONLY on installation instructions for this exact part
        - Be clear, encouraging, and safety-focused
        - Keep response professional and well-organized"""

        response = self.client.chat_with_system(
            system_prompt=system_prompt, user_message=user_query, temperature=0.7
        )

        return response

    def handle_query(
        self,
        user_query: str,
        part_number: str = None,
        conversation_history: List[Dict] = None,
    ) -> Dict:
        """
        Main handler for installation queries with comprehensive error handling

        Args:
            user_query: User's installation query
            part_number: Optional part number (extracted if not provided)
            conversation_history: Optional conversation history for context
        """
        # Extract part number if not provided
        if not part_number:
            part_number = self.extract_part_number(user_query)

        # If still no part number, check conversation history
        if not part_number and conversation_history:
            part_number = self.extract_part_from_history(conversation_history)

        # Handle time estimate queries specifically
        if any(
            keyword in user_query.lower()
            for keyword in [
                "how long",
                "how much time",
                "time estimate",
                "duration",
                "take to install",
            ]
        ):
            return self.handle_time_estimate_query(
                user_query, part_number, conversation_history
            )

        # Error 1: No part number found
        if not part_number:
            # Search for relevant parts based on the query
            relevant_parts = self.find_relevant_parts(user_query, n_results=3)

            if relevant_parts:
                # Found relevant parts - suggest them
                suggestions = "\n\n**Here are some parts that might match what you're looking for:**\n"
                for i, part in enumerate(relevant_parts, 1):
                    suggestions += (
                        f"\n{i}. **{part['name']}** (Part #{part['part_number']})\n"
                    )
                    suggestions += f"   - ${part['price']} | {part.get('installation_difficulty', 'Unknown')} difficulty\n"
                    suggestions += f"   - {part['description'][:80]}...\n"

                suggestions += "\n💡 **To get installation instructions, ask:** 'How do I install PS[part number]?'"

                return {
                    "response": f"I'd be happy to help with installation! I need the specific **part number** to provide detailed instructions.{suggestions}",
                    "agent": "installation",
                    "suggested_parts": relevant_parts,
                    "error": "NO_PART_NUMBER",
                }
            else:
                # No relevant parts found - generic help
                return {
                    "response": "I'd be happy to help with installation! Could you provide the **part number**? It typically looks like **PS** followed by 8 digits.\n\n"
                    + "You can find the part number:\n"
                    + "- On the part packaging\n"
                    + "- In your order confirmation\n"
                    + "- By searching for the part name in our catalog\n\n"
                    + "Or tell me what part you need (e.g., 'dishwasher spray arm', 'ice maker assembly') and I can help you find it!",
                    "agent": "installation",
                    "error": "NO_PART_NUMBER",
                }

        # Get installation instructions
        instructions = self.get_installation_instructions(part_number)

        # Error 2: Part not found in database
        if not instructions:
            # Extract category from query for better filtering
            query_lower = user_query.lower()
            category = None
            if any(kw in query_lower for kw in ["dishwasher", "dish washer"]):
                category = "Dishwasher"
            elif any(kw in query_lower for kw in ["refrigerator", "fridge", "freezer"]):
                category = "Refrigerator"

            # Try to find similar parts
            search_query = user_query.replace(part_number, "").strip()
            if not search_query:
                search_query = f"part {part_number}"

            # Add category to search if detected
            if category:
                search_query = f"{category} {search_query}"

            similar_parts = self.find_relevant_parts(search_query, n_results=3)

            # Filter by category if detected
            if category and similar_parts:
                similar_parts = [
                    p for p in similar_parts if p.get("category") == category
                ][:3]

            response = (
                f"I couldn't find part number **{part_number}** in our catalog.\n\n"
            )

            if similar_parts:
                response += "**Did you mean one of these parts?**\n"
                for i, part in enumerate(similar_parts, 1):
                    response += (
                        f"\n{i}. **{part['name']}** (Part #{part['part_number']})\n"
                    )
                    response += f"   - ${part['price']} | {part.get('installation_difficulty', 'Unknown')} difficulty\n"

                response += "\n💡 Ask: 'How do I install PS[correct part number]?'"
            else:
                response += "**What you can do:**\n"
                response += "- Double-check the part number\n"
                response += "- Search by part name or symptom\n"
                response += "- Browse available parts by category\n"

            return {
                "response": response,
                "agent": "installation",
                "part_number": part_number,
                "suggested_parts": similar_parts if similar_parts else [],
                "error": "PART_NOT_FOUND",
            }

        # Error 3: No installation steps available
        if not instructions["steps"] or len(instructions["steps"]) == 0:
            part_info = instructions["part"]
            return {
                "response": f"I found **{part_info['name']}** (Part #{part_number}), but detailed installation instructions are not currently available for this part.\n\n"
                + f"**What this means:**\n"
                + f"- This is typically a simple replacement part that doesn't require complex installation\n"
                + f"- You can usually install it by removing the old part and snapping in the new one\n\n"
                + f"**Need more help?**\n"
                + f"- Contact PartSelect customer service at 1-800-PARTSELECT\n"
                + f"- Check YouTube for '{part_info['name']} installation'\n"
                + f"- Ask: 'What tools do I need for {part_number}?'\n\n"
                + f"💰 **Price:** ${part_info['price']}\n"
                + f"🔧 **Difficulty:** {instructions['difficulty']}",
                "agent": "installation",
                "part": part_info,
                "part_number": part_number,
                "error": "NO_INSTALLATION_STEPS",
            }

        # Success: Generate full response
        try:
            response_text = self.generate_response(instructions, user_query)

            return {
                "response": response_text,
                "part": instructions["part"],
                "steps": instructions["steps"],
                "difficulty": instructions["difficulty"],
                "agent": "installation",
                "no_suggestions": True,
            }
        except Exception as e:
            # Fallback if LLM fails
            print(f"[InstallationAgent] LLM error: {e}")

            part_info = instructions["part"]
            steps = instructions["steps"]
            difficulty = instructions["difficulty"]

            fallback_response = (
                f"**Installation Instructions for {part_info['name']}**\n\n"
            )
            fallback_response += f"**Part Number:** {part_number}\n"
            fallback_response += f"**Difficulty:** {difficulty}\n"
            fallback_response += f"**Price:** ${part_info['price']}\n\n"
            fallback_response += "**Steps:**\n"

            for i, step in enumerate(steps, 1):
                fallback_response += f"{i}. {step}\n"

            fallback_response += "\n⚠️ **Safety First:** Always disconnect power before starting any repair!"

            return {
                "response": fallback_response,
                "part": part_info,
                "steps": steps,
                "difficulty": difficulty,
                "agent": "installation",
            }


# Test function
def test_installation():
    agent = InstallationAgent()

    test_queries = [
        "How can I install part number PS11752778?",  # Valid part
        "Installation instructions for PS99999999?",  # Invalid part
        "How do I install the ice maker assembly?",  # No part number
        "Install PS11722146",  # Valid part
    ]

    print("Testing Installation Agent:\n")
    for query in test_queries:
        print(f"Query: {query}")
        result = agent.handle_query(query)
        print(f"Response: {result['response'][:200]}...")
        print(f"Error: {result.get('error', 'None')}")
        if "steps" in result:
            print(f"Steps: {len(result['steps'])} steps")
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    test_installation()
