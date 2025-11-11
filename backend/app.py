"""
FastAPI Backend for PartSelect Chat Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json as json_lib
from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Request
import sys
import os
from datetime import datetime
import uuid

# Add agents to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import ChatOrchestrator
from database.models import SessionLocal, Part, Model

from functools import lru_cache
from datetime import datetime, timedelta

# Cache suggestions for 1 hour
suggestions_cache = {"suggestions": [], "expires_at": None}

# Initialize FastAPI app
app = FastAPI(
    title="PartSelect Chat Agent API",
    description="AI-powered chat agent for refrigerator and dishwasher parts",
    version="1.0.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    FRONTEND_URL,
    "https://*.onrender.com",  # Allow Render subdomains
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator (singleton)
orchestrator = None

# In-memory conversation storage (in production, use Redis or database)
conversations = {}


# Request/Response Models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    agent: str
    category: str
    parts: Optional[List[Dict]] = None
    suggested_parts: Optional[List[Dict]] = None
    compatible: Optional[bool] = None
    steps: Optional[List[str]] = None
    timestamp: str


class PartDetails(BaseModel):
    part_number: str


class CompatibilityCheck(BaseModel):
    part_number: str
    model_number: str


# Startup event
@app.on_event("startup")
async def startup_event():
    global orchestrator
    print("🚀 Starting PartSelect Chat Agent API...")
    orchestrator = ChatOrchestrator()
    print("✓ API ready to serve requests!")


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "PartSelect Chat Agent API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Main chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Main chat endpoint - handles user queries
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())

        # Get conversation history
        conversation_history = conversations.get(session_id, [])

        # Process query
        result = orchestrator.handle_query(
            user_message=request.message, conversation_history=conversation_history
        )

        # Update conversation history
        conversation_history.append(
            {
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat(),
            }
        )
        conversation_history.append(
            {
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.now().isoformat(),
            }
        )
        conversations[session_id] = conversation_history[-10:]  # Keep last 10 messages

        # Build response
        response = ChatResponse(
            response=result["response"],
            session_id=session_id,
            agent=result.get("agent", "unknown"),
            category=result.get("category", "unknown"),
            parts=result.get("parts"),
            suggested_parts=result.get("suggested_parts"),
            compatible=result.get("compatible"),
            steps=result.get("steps"),
            timestamp=datetime.now().isoformat(),
        )

        return response

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get part details
@app.get("/api/parts/{part_number}")
async def get_part(part_number: str):
    """
    Get detailed information about a specific part
    """
    db = SessionLocal()
    try:
        part = db.query(Part).filter(Part.part_number == part_number).first()

        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        part_dict = part.to_dict()
        part_dict["compatible_models"] = [
            m.model_number for m in part.compatible_models
        ]

        return part_dict

    finally:
        db.close()


# Search parts
@app.get("/api/parts")
async def search_parts(
    query: Optional[str] = None, category: Optional[str] = None, limit: int = 10
):
    """
    Search for parts
    """
    db = SessionLocal()
    try:
        query_obj = db.query(Part)

        if category:
            query_obj = query_obj.filter(Part.category == category)

        if query:
            query_obj = query_obj.filter(
                Part.name.contains(query) | Part.description.contains(query)
            )

        parts = query_obj.limit(limit).all()

        return [part.to_dict() for part in parts]

    finally:
        db.close()


# Check compatibility
@app.post("/api/compatibility")
async def check_compatibility(request: CompatibilityCheck):
    """
    Check if a part is compatible with a model
    """
    result = orchestrator.compatibility.check_compatibility(
        part_number=request.part_number, model_number=request.model_number
    )

    return result


# Get conversation history
@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str):
    """
    Get conversation history for a session
    """
    history = conversations.get(session_id, [])
    return {"session_id": session_id, "messages": history}


# Clear conversation
@app.delete("/api/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a session
    """
    if session_id in conversations:
        del conversations[session_id]

    return {"message": "Conversation cleared", "session_id": session_id}


# Get all categories
@app.get("/api/categories")
async def get_categories():
    """
    Get list of product categories
    """
    return {
        "categories": [
            {"id": "refrigerator", "name": "Refrigerator Parts"},
            {"id": "dishwasher", "name": "Dishwasher Parts"},
        ]
    }


# Streaming endpoint
@app.post("/api/chat/stream")
async def chat_stream(request: ChatMessage):
    """
    Streaming chat endpoint using Server-Sent Events
    """
    session_id = request.session_id or str(uuid.uuid4())
    conversation_history = conversations.get(session_id, [])

    async def event_generator():
        try:
            # Get the response from orchestrator
            result = orchestrator.handle_query(
                user_message=request.message, conversation_history=conversation_history
            )

            response_text = result["response"]

            # Stream word by word
            words = response_text.split(" ")
            accumulated_text = ""

            for i, word in enumerate(words):
                accumulated_text += word + " "

                chunk_data = {"type": "content", "content": word + " ", "done": False}

                yield f"data: {json_lib.dumps(chunk_data)}\n\n"

                # Small delay for smoother streaming
                await asyncio.sleep(0.03)

            # Send metadata (parts, compatibility, etc.)
            metadata_chunk = {
                "type": "metadata",
                "agent": result.get("agent"),
                "category": result.get("category"),
                "parts": result.get("parts"),
                "suggested_parts": result.get("suggested_parts"),
                "compatible": result.get("compatible"),
                "steps": result.get("steps"),
                "session_id": session_id,
                "done": True,
            }
            yield f"data: {json_lib.dumps(metadata_chunk)}\n\n"

            # Generate follow-up suggestions
            suggestions = generate_followup_questions(request.message, result)
            if suggestions:
                suggestion_chunk = {"type": "suggestions", "suggestions": suggestions}
                yield f"data: {json_lib.dumps(suggestion_chunk)}\n\n"

            # Update conversation history
            conversation_history.append(
                {
                    "role": "user",
                    "content": request.message,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            conversation_history.append(
                {
                    "role": "assistant",
                    "content": accumulated_text.strip(),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            conversations[session_id] = conversation_history[-10:]

        except Exception as e:
            error_chunk = {"type": "error", "error": str(e), "done": True}
            yield f"data: {json_lib.dumps(error_chunk)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def generate_followup_questions(user_query: str, result: Dict) -> List[str]:
    """
    Generate contextual follow-up questions based on the conversation
    """
    suggestions = []
    category = result.get("category", "")
    agent = result.get("agent", "")
    parts = result.get("parts", [])

    if category == "PRODUCT_SEARCH" and parts:
        # After product search, suggest compatibility or installation
        if parts:
            part = parts[0]
            suggestions = [
                f"How do I install {part['part_number']}?",
                f"Is {part['part_number']} compatible with my appliance?",
                f"What are common issues with {part['name']}?",
            ]

    elif category == "COMPATIBILITY_CHECK":
        # After compatibility check, suggest installation or alternatives
        part_num = result.get("part_number")
        if part_num:
            suggestions = [
                f"How do I install part {part_num}?",
                "Show me similar parts",
                "What tools do I need for installation?",
            ]

    elif category == "INSTALLATION_HELP":
        # After installation, suggest troubleshooting
        suggestions = [
            "What if the part doesn't fit?",
            "How long does installation take?",
            "Do I need special tools?",
        ]

    elif category == "TROUBLESHOOTING":
        # After troubleshooting, suggest specific parts
        suggested_parts = result.get("suggested_parts", [])
        if suggested_parts:
            part = suggested_parts[0]
            suggestions = [
                f"Tell me more about {part['name']}",
                f"How do I install {part['part_number']}?",
                "Show me installation videos",
            ]

    # Default suggestions if none generated
    if not suggestions:
        suggestions = [
            "Show me popular refrigerator parts",
            "Find dishwasher replacement parts",
            "How do I troubleshoot my appliance?",
        ]

    return suggestions[:3]  # Return top 3


@app.get("/api/suggestions")
async def get_initial_suggestions():
    """Fetch random, real suggestions from the database - no LLM hallucinations"""
    import random

    try:
        db = SessionLocal()

        # Get random parts from different categories
        refrigerator_parts = (
            db.query(Part).filter(Part.category == "Refrigerator").all()
        )
        dishwasher_parts = db.query(Part).filter(Part.category == "Dishwasher").all()

        suggestions = []
        difficulty_levels = {
            "Easy": "under 30 minutes",
            "Medium": "30 minutes to an hour",
            "Hard": "over an hour",
        }

        # Create suggestions based on actual database data
        if refrigerator_parts:
            random_fridge = random.choice(refrigerator_parts)
            random_fridge_2 = random.choice(refrigerator_parts)

            # Mix of different suggestion types
            suggestion_types = []

            # Type 1: Troubleshooting with symptoms
            if random_fridge.common_symptoms:
                symptom = random.choice(random_fridge.common_symptoms)
                suggestion_types.append(
                    f"My refrigerator has {symptom.lower()}, how do I fix it?"
                )

            # Type 2: Installation with time estimate
            if random_fridge.installation_difficulty:
                time_est = difficulty_levels.get(
                    random_fridge.installation_difficulty, "varies"
                )
                suggestion_types.append(
                    f"How do I install a {random_fridge.name.lower()}? ({time_est})"
                )
            else:
                suggestion_types.append(
                    f"How do I install a {random_fridge.name.lower()}?"
                )

            # Type 3: Browse by subcategory
            if random_fridge_2.subcategory:
                suggestion_types.append(
                    f"Show me {random_fridge_2.subcategory.lower()} parts"
                )
            else:
                suggestion_types.append("Show me refrigerator parts")

            suggestions.extend(suggestion_types[: random.randint(2, 3)])

        if dishwasher_parts:
            random_dishwasher = random.choice(dishwasher_parts)
            random_dishwasher_2 = random.choice(dishwasher_parts)

            # Type 1: Troubleshooting with symptoms
            if random_dishwasher.common_symptoms:
                symptom = random.choice(random_dishwasher.common_symptoms)
                suggestions.append(
                    f"My dishwasher has {symptom.lower()}, how can I fix it?"
                )

            # Type 2: Installation difficulty
            if random_dishwasher.installation_difficulty:
                difficulty = random_dishwasher.installation_difficulty.lower()
                suggestions.append(f"Show me {difficulty}-to-install dishwasher parts")

            # Type 3: Compatibility check
            suggestions.append("Is this part compatible with my appliance model?")

        db.close()

        # Ensure we have at least 5 suggestions
        if len(suggestions) < 5:
            suggestions.extend(
                [
                    "How long does installation typically take?",
                    "Browse available parts and prices",
                    "Find replacement parts for my model",
                    "What are the most common dishwasher problems?",
                    "Show me easy-to-install refrigerator parts",
                ]
            )

        # Return only unique suggestions and limit to 5
        suggestions = list(dict.fromkeys(suggestions))[:5]

        print(
            f"[Suggestions] Generated {len(suggestions)} real suggestions from database"
        )

        return {
            "suggestions": suggestions,
            "source": "database",
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"Error generating suggestions: {e}")
        fallback_suggestions = [
            "How do I install a refrigerator ice maker?",
            "My dishwasher won't drain - how do I fix it?",
            "What parts are compatible with my model?",
            "How long does it take to install a spray arm?",
            "My refrigerator is leaking water - what should I replace?",
        ]
        return {
            "suggestions": fallback_suggestions,
            "source": "fallback",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
