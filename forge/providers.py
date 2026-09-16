"""Provider catalog — base URLs and model lists for the setup wizard."""

PROVIDERS = {
    "openai": {
        "label": "OpenAI (ChatGPT)",
        "base": "https://api.openai.com/v1",
        "key_url": "https://platform.openai.com/api-keys",
        "models": ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini",
                   "gpt-4.1", "o3", "o4-mini"],
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "base": "https://api.anthropic.com/v1",
        "key_url": "https://console.anthropic.com/settings/keys",
        "models": ["claude-sonnet-4-5", "claude-opus-4-1",
                   "claude-sonnet-4", "claude-haiku-4-5",
                   "claude-3-7-sonnet"],
    },
    "google": {
        "label": "Google Gemini",
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "key_url": "https://aistudio.google.com/app/apikey",
        "models": ["gemini-2.5-pro", "gemini-2.5-flash",
                   "gemini-2.0-flash", "gemini-2.0-flash-lite"],
    },
    "xai": {
        "label": "xAI (Grok)",
        "base": "https://api.x.ai/v1",
        "key_url": "https://console.x.ai",
        "models": ["grok-4", "grok-4-heavy", "grok-4-mini",
                   "grok-3", "grok-3-mini"],
    },
    "mistral": {
        "label": "Mistral",
        "base": "https://api.mistral.ai/v1",
        "key_url": "https://console.mistral.ai/api-keys",
        "models": ["mistral-large-latest", "mistral-medium-latest",
                   "mistral-small-latest", "codestral-latest",
                   "magistral-medium-latest", "devstral-medium-latest"],
    },
    "deepseek": {
        "label": "DeepSeek",
        "base": "https://api.deepseek.com/v1",
        "key_url": "https://platform.deepseek.com",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "groq": {
        "label": "Groq (fast inference)",
        "base": "https://api.groq.com/openai/v1",
        "key_url": "https://console.groq.com/keys",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant",
                   "mixtral-8x7b-32768", "qwen-2.5-72b",
                   "deepseek-r1-distill-llama-70b", "kimi-k2-instruct"],
    },
    "together": {
        "label": "Together AI",
        "base": "https://api.together.xyz/v1",
        "key_url": "https://api.together.xyz/settings/api-keys",
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo",
                   "Qwen/Qwen2.5-72B-Instruct-Turbo",
                   "deepseek-ai/DeepSeek-V3",
                   "deepseek-ai/DeepSeek-R1",
                   "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    },
    "fireworks": {
        "label": "Fireworks AI",
        "base": "https://api.fireworks.ai/inference/v1",
        "key_url": "https://fireworks.ai/account/api-keys",
        "models": ["accounts/fireworks/models/llama-v3p3-70b-instruct",
                   "accounts/fireworks/models/deepseek-v3",
                   "accounts/fireworks/models/qwen2p5-72b-instruct"],
    },
    "cohere": {
        "label": "Cohere",
        "base": "https://api.cohere.ai/compatibility/v1",
        "key_url": "https://dashboard.cohere.com/api-keys",
        "models": ["command-r-plus", "command-r", "command-a"],
    },
    "perplexity": {
        "label": "Perplexity",
        "base": "https://api.perplexity.ai",
        "key_url": "https://perplexity.ai/settings/api",
        "models": ["sonar-pro", "sonar", "sonar-reasoning"],
    },
    "openrouter": {
        "label": "OpenRouter (one key, ~300 models)",
        "base": "https://openrouter.ai/api/v1",
        "key_url": "https://openrouter.ai/keys",
        "models": ["anthropic/claude-sonnet-4.5",
                   "openai/gpt-5",
                   "google/gemini-2.5-pro",
                   "x-ai/grok-4",
                   "deepseek/deepseek-chat",
                   "meta-llama/llama-3.3-70b-instruct",
                   "cognitivecomputations/dolphin-mixtral-8x22b",
                   "nousresearch/hermes-3-llama-3.1-70b"],
    },
    "azure": {
        "label": "Azure OpenAI",
        "base": "",  # user-supplied
        "key_url": "https://portal.azure.com",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-35-turbo"],
    },
    "ollama": {
        "label": "Ollama (local)",
        "base": "http://localhost:11434/v1",
        "key_url": "",
        "models": [],  # auto-detected
    },
    "local": {
        "label": "vLLM / LM Studio / llama.cpp (local)",
        "base": "http://localhost:8000/v1",
        "key_url": "",
        "models": [],
    },
    "litellm": {
        "label": "LiteLLM proxy",
        "base": "http://localhost:4000/v1",
        "key_url": "",
        "models": [],
    },
    "custom": {
        "label": "Custom endpoint",
        "base": "",
        "key_url": "",
        "models": [],
    },
}


def menu_order():
    return ["openai", "anthropic", "google", "xai", "mistral", "deepseek",
            "groq", "together", "fireworks", "cohere", "perplexity",
            "openrouter", "azure", "ollama", "local", "litellm", "custom"]
