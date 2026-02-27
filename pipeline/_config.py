"""
Shared configuration for the FlowBridge.ai pipeline.
"""

# Native ADK Gemini model — no LiteLLM wrapper needed.
# ADK reads GOOGLE_API_KEY from the environment automatically.
GEMINI_MODEL = "gemini-2.5-pro"
