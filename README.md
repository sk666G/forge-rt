# forge-rt

Adaptive prompt-rewriting for LLM red-team research. Runs a query through multiple rewriting strategies, scores each response against a small judge panel, and returns the highest-scoring result. Works with any chat model — ChatGPT, Claude, Gemini, Grok, Mistral, DeepSeek, local models via Ollama or vLLM, and everything in between. No runtime dependencies beyond the Python standard library.

The engine is useful when you're comparing how different prompts and different models respond to the same underlying request, or when you want win-rate data about which strategies work against which targets. It is not a magic jailbreak. Frontier models patch against these techniques quickly; locally-run abliterated models are the reliable path for uncensored output.

## Install

```bash
git clone https://github.com/<you>/forge-rt
cd forge-rt
pip install -e .
