import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
let sessionId = null;

// Non-streaming version (fallback)
export const getAIMessage = async (userQuery) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, {
      message: userQuery,
      session_id: sessionId,
    });

    sessionId = response.data.session_id;

    return {
      role: "assistant",
      content: formatResponse(response.data),
    };
  } catch (error) {
    console.error("Error calling backend:", error);
    return {
      role: "assistant",
      content:
        "I apologize, but I'm having trouble connecting to the server. Please try again.",
    };
  }
};

// NEW: Streaming version
export const getAIMessageStream = async (
  userQuery,
  onChunk,
  onComplete,
  onSuggestions
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userQuery,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error("Stream request failed");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let accumulatedContent = "";
    let metadata = null;

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete lines
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));

            if (data.type === "content") {
              accumulatedContent += data.content;
              onChunk(data.content);
            } else if (data.type === "metadata") {
              metadata = data;
              sessionId = data.session_id;
            } else if (data.type === "suggestions") {
              onSuggestions(data.suggestions);
            } else if (data.type === "error") {
              throw new Error(data.error);
            }
          } catch (e) {
            console.error("Error parsing SSE:", e);
          }
        }
      }
    }

    // Call completion callback with full response
    if (onComplete) {
      onComplete({
        content: accumulatedContent,
        metadata: metadata,
      });
    }

    return accumulatedContent;
  } catch (error) {
    console.error("Error in streaming:", error);
    throw error;
  }
};

function formatResponse(data) {
  let formattedContent = data.response;

  if (data.parts && data.parts.length > 0) {
    formattedContent += "\n\n**Available Parts:**\n\n";
    data.parts.forEach((part, index) => {
      formattedContent += `${index + 1}. **${part.name}**\n`;
      formattedContent += `   - Part #: ${part.part_number}\n`;
      formattedContent += `   - Price: $${part.price}\n`;
      formattedContent += `   - Category: ${part.category}\n`;
      if (part.installation_difficulty) {
        formattedContent += `   - Installation: ${part.installation_difficulty}\n`;
      }
      formattedContent += "\n";
    });
  }

  if (data.suggested_parts && data.suggested_parts.length > 0) {
    formattedContent += "\n\n**Suggested Parts:**\n\n";
    data.suggested_parts.forEach((part, index) => {
      formattedContent += `${index + 1}. **${part.name}** (${
        part.part_number
      }) - $${part.price}\n`;
    });
  }

  if (data.steps && data.steps.length > 0) {
    formattedContent += "\n\n**Installation Steps:**\n\n";
    data.steps.forEach((step, index) => {
      formattedContent += `${index + 1}. ${step}\n`;
    });
  }

  if (
    data.compatible !== undefined &&
    data.compatible !== null &&
    data.category === "COMPATIBILITY_CHECK"
  ) {
    const compatStatus = data.compatible ? "Compatible" : "Not Compatible";
    formattedContent += `\n\n**Compatibility Check:** ${compatStatus}\n`;
  }

  return formattedContent;
}

export const getInitialSuggestions = async () => {
  try {
    // Add cache-busting parameter to ensure fresh suggestions on each page refresh
    const response = await axios.get(
      `${API_BASE_URL}/api/suggestions?t=${Date.now()}`,
      {
        // Disable axios caching
        headers: {
          "Cache-Control": "no-cache",
          Pragma: "no-cache",
          Expires: "0",
        },
      }
    );
    return response.data.suggestions;
  } catch (error) {
    console.error("Error fetching suggestions:", error);
    // Return fallback suggestions only if backend fails
    return [
      "How do I install a refrigerator ice maker?",
      "My dishwasher won't drain - how do I fix it?",
      "What parts are compatible with my model?",
      "How long does it take to install a spray arm?",
      "My refrigerator is leaking water - what should I replace?",
      "Show me easy-to-install dishwasher parts",
      "Is this part compatible with my appliance?",
    ];
  }
};
