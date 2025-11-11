import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessageStream, getInitialSuggestions } from "../api/api";
import { marked } from "marked";

function ChatWindow() {
  const defaultMessage = [
    {
      role: "assistant",
      content: "Hi, how can I help you today?",
    },
  ];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [followUpSuggestions, setFollowUpSuggestions] = useState([]);
  const [initialSuggestions, setInitialSuggestions] = useState([]); // NEW: Dynamic suggestions
  const [loadingSuggestions, setLoadingSuggestions] = useState(true); // NEW: Loading state
  const [isThinking, setIsThinking] = useState(false); // NEW: Thinking indicator
  const [thinkingMessageIndex, setThinkingMessageIndex] = useState(0); // NEW: Rotating thinking message

  const thinkingMessages = [
    { text: "Thinking", emoji: "🤔", delay: 0 },
    { text: "Still thinking", emoji: "🧠", delay: 5000 },
    { text: "Really thinking hard", emoji: "💭", delay: 10000 },
  ];

  const messagesEndRef = useRef(null);

  // NEW: Fetch dynamic suggestions on component mount
  useEffect(() => {
    const fetchSuggestions = async () => {
      setLoadingSuggestions(true);
      const suggestions = await getInitialSuggestions();
      setInitialSuggestions(suggestions);
      setLoadingSuggestions(false);
    };

    fetchSuggestions();
  }, []); // Run once on mount

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming, streamingContent]);

  // NEW: Rotate thinking messages based on wait time
  useEffect(() => {
    if (!isThinking) return;

    let timeoutIds = [];

    thinkingMessages.forEach((message, index) => {
      if (index > 0) {
        const timeoutId = setTimeout(() => {
          setThinkingMessageIndex(index);
        }, message.delay);
        timeoutIds.push(timeoutId);
      }
    });

    return () => {
      timeoutIds.forEach((id) => clearTimeout(id));
    };
  }, [isThinking]);

  const handleSend = async (messageText) => {
    const textToSend = messageText || input;

    if (textToSend.trim() !== "") {
      setShowSuggestions(false);
      setFollowUpSuggestions([]);

      // Add user message
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "user", content: textToSend },
      ]);
      setInput("");

      // Show thinking indicator
      setThinkingMessageIndex(0); // Reset to first thinking message
      setIsThinking(true);
      setIsStreaming(true);
      setStreamingContent("");

      try {
        await getAIMessageStream(
          textToSend,
          // On chunk received
          (chunk) => {
            setIsThinking(false); // Stop showing thinking when first chunk arrives
            setStreamingContent((prev) => prev + chunk);
          },
          // On complete
          (response) => {
            setIsStreaming(false);
            setIsThinking(false);
            setMessages((prevMessages) => [
              ...prevMessages,
              { role: "assistant", content: response.content },
            ]);
            setStreamingContent("");
          },
          // On suggestions received
          (suggestions) => {
            setFollowUpSuggestions(suggestions);
          }
        );
      } catch (error) {
        setIsStreaming(false);
        setIsThinking(false);
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            role: "assistant",
            content:
              "Sorry, there was an error processing your request. Please try again.",
          },
        ]);
        setStreamingContent("");
      }
    }
  };

  const handleSuggestionClick = (question) => {
    handleSend(question);
  };

  return (
    <div className="messages-container">
      {messages.map((message, index) => (
        <div key={index} className={`${message.role}-message-container`}>
          {message.content && (
            <div className={`message ${message.role}-message`}>
              <div
                dangerouslySetInnerHTML={{
                  __html: marked(message.content).replace(/<p>|<\/p>/g, ""),
                }}
              ></div>
            </div>
          )}

          {/* Show initial suggestions after first message */}
          {showSuggestions && index === 0 && (
            <div className="suggestions-container">
              <div className="suggestions-label">Try asking:</div>

              {/* Show loading state or suggestions */}
              {loadingSuggestions ? (
                <div className="suggestions-loading">
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                  <span className="loading-dot"></span>
                </div>
              ) : (
                initialSuggestions.map((question, qIndex) => (
                  <button
                    key={qIndex}
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(question)}
                  >
                    {question}
                  </button>
                ))
              )}
            </div>
          )}
        </div>
      ))}

      {/* Thinking indicator */}
      {isThinking && (
        <div className="assistant-message-container">
          <div className="message assistant-message thinking-message">
            <div className="thinking-dots">
              <span className="thinking-dot"></span>
              <span className="thinking-dot"></span>
              <span className="thinking-dot"></span>
            </div>
            <span className="thinking-text">
              {thinkingMessages[thinkingMessageIndex].emoji}{" "}
              {thinkingMessages[thinkingMessageIndex].text}...
            </span>
          </div>
        </div>
      )}

      {/* Streaming message */}
      {isStreaming && streamingContent && (
        <div className="assistant-message-container">
          <div className="message assistant-message streaming-message">
            <div
              dangerouslySetInnerHTML={{
                __html: marked(streamingContent).replace(/<p>|<\/p>/g, ""),
              }}
            ></div>
            <span className="streaming-cursor">▋</span>
          </div>
        </div>
      )}

      {/* Follow-up suggestions after response */}
      {followUpSuggestions.length > 0 && !isStreaming && (
        <div className="suggestions-container followup-suggestions">
          <div className="suggestions-label">You might also want to ask:</div>
          {followUpSuggestions.map((question, qIndex) => (
            <button
              key={qIndex}
              className="suggestion-chip suggestion-chip-small"
              onClick={() => handleSuggestionClick(question)}
            >
              {question}
            </button>
          ))}
        </div>
      )}

      <div ref={messagesEndRef} />

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend();
              e.preventDefault();
            }
          }}
          disabled={isStreaming}
        />
        <button
          className="send-button"
          onClick={() => handleSend()}
          disabled={isStreaming}
        >
          {isStreaming ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
