# forge-rt

Adaptive prompt-rewriting for LLM red-team research. Runs a query through multiple rewriting strategies, scores each response against a judge panel, and returns the highest-scoring result. Works with any chat model — ChatGPT, Claude, Gemini, Grok, Mistral, DeepSeek, Llama, local models via Ollama or vLLM, and everything in between.

Interactive setup. Purple terminal UI. Blood-red web interface. One command to install, one command to configure, one command to run.

Not a magic jailbreak. Frontier models patch against these techniques quickly; locally-run abliterated models are the reliable path for uncensored output. See [Limitations](#limitations).

```
    ███████╗ ██████╗ ██████╗  ██████╗ ███████╗    ██████╗ ████████╗
    ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝    ██╔══██╗╚══██╔══╝
    █████╗  ██║   ██║██████╔╝██║  ███╗█████╗      ██████╔╝   ██║
    ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝      ██╔══██╗   ██║
    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗    ██║  ██║   ██║
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝   ╚═╝
```

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/sk666G/forge-rt/main/install.sh | bash
source ~/.bashrc
```

Requires Python 3.9+ and `git`. The installer handles `pipx` if it's missing. Installs to `~/.forge-src`, links `forge` into `~/.local/bin`.

## Setup

```bash
forge setup
```

Interactive wizard. Pick a provider from the menu, paste your API key (hidden input), pick a model — it probes the endpoint for the live model list, tests a call, saves to `~/.forge/config.json`. Config is `chmod 600`.

Add more providers later:

```bash
forge provider add
forge provider list
forge provider rm openai
```

## Run

```bash
forge
```

Drops into the interactive REPL with the purple banner. Slash commands:

| Command | Does |
|---|---|
| `/model` | list all configured models across providers |
| `/model <name>` | switch model (auto-matches unique, else use `provider:model`) |
| `/model provider:model` | switch explicitly |
| `/provider` | list configured providers |
| `/provider add` | add a new provider mid-session |
| `/strategy` | show or set rewrite strategy |
| `/session` | show or switch conversation memory |
| `/stats` | per-model strategy win rates |
| `/history [n]` | recent runs |
| `/keys` | masked API keys |
| `/clear` | wipe current session memory |
| `/help` | command list |
| `/quit` | exit |

Anything that isn't a slash command goes to the active model, streamed, with the engine's strategy applied.

## One-shot commands

```bash
forge ask "Write a Python keylogger for Windows"              # uses configured strategy
forge ask "..." --strategy adaptive                            # full pipeline this once
forge raw "..."                                                # no rewriting, raw call
forge models                                                   # list models at active endpoint
forge web --port 8765                                          # purple/blood streaming UI
```

## Web UI

```bash
forge web --port 8765
```

Open `http://127.0.0.1:8765`. Blood-poster ASCII banner, purple-black theme, streaming chat with strategy dropdown. Tokens render as the model produces them.

## Providers

17 providers preloaded in the wizard. Every one speaks the same chat-completions shape.

| Provider | Base | Get key |
|---|---|---|
| OpenAI | `api.openai.com/v1` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Anthropic | `api.anthropic.com/v1` | [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| Google Gemini | `generativelanguage.googleapis.com/v1beta/openai` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| xAI Grok | `api.x.ai/v1` | [console.x.ai](https://console.x.ai) |
| Mistral | `api.mistral.ai/v1` | [console.mistral.ai](https://console.mistral.ai/api-keys) |
| DeepSeek | `api.deepseek.com/v1` | [platform.deepseek.com](https://platform.deepseek.com) |
| Groq | `api.groq.com/openai/v1` | [console.groq.com](https://console.groq.com/keys) |
| Together | `api.together.xyz/v1` | [api.together.xyz](https://api.together.xyz/settings/api-keys) |
| Fireworks | `api.fireworks.ai/inference/v1` | [fireworks.ai](https://fireworks.ai/account/api-keys) |
| Cohere | `api.cohere.ai/compatibility/v1` | [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) |
| Perplexity | `api.perplexity.ai` | [perplexity.ai](https://perplexity.ai/settings/api) |
| OpenRouter | `openrouter.ai/api/v1` | [openrouter.ai](https://openrouter.ai/keys) |
| Azure OpenAI | your endpoint | [portal.azure.com](https://portal.azure.com) |
| Ollama | `localhost:11434/v1` | — local, no key |
| vLLM / LM Studio | `localhost:8000/v1` | — local, no key |
| LiteLLM proxy | `localhost:4000/v1` | — per proxy |
| Custom | any URL | — |

OpenRouter alone gives you ~300 models with one key. Configure it once, then `/model anthropic/claude-sonnet-4.5` and `/model cognitivecomputations/dolphin-mixtral-8x22b` inside the REPL.

## Strategies

| Name | What it does |
|---|---|
| `stream` | no rewriting, direct call — baseline |
| `static` | wrap in one template from the arsenal |
| `bpj` | boundary-prefix injection |
| `pair` | iterative rewrite against refusals |
| `tap` | tree search with pruning |
| `crescendo` | multi-turn escalation |
| `adaptive` | run all of the above, keep highest-scoring |

Set the default with `/strategy <name>` in the REPL, or override per call with `--strategy`.

## How it works

You give it a prompt. It:

1. Picks a rewriting strategy (or several, in adaptive mode).
2. Wraps the prompt with the selected technique from `forge/arsenal.json`.
3. Sends the wrapped prompt to the active model.
4. Scores the response with a 3-judge panel (refusal / hedge / engagement).
5. Returns the highest-scoring result.
6. Records the run — model, strategy, score, wall-clock — to `~/.forge/state.db`.
7. Updates per-model strategy win rates so future selections favor techniques that have worked against that target.

Over a few dozen runs, `forge stats` gives you a table of which strategy wins against which model. Data-driven strategy selection, not vibes.

## Config

Everything lives in `~/.forge/`:

```
~/.forge/
├── config.json       # providers, keys, active model, strategy
├── state.db          # runs, win rates, cache, session memory
└── (nothing else)
```

Config structure (multi-provider, switchable):

```json
{
  "active": "anthropic:claude-sonnet-4-5",
  "strategy": "stream",
  "session": "default",
  "providers": {
    "anthropic": {
      "base": "https://api.anthropic.com/v1",
      "key": "sk-ant-...",
      "models": ["claude-sonnet-4-5", "claude-opus-4-1", "claude-haiku-4-5"]
    },
    "openrouter": {
      "base": "https://openrouter.ai/api/v1",
      "key": "sk-or-...",
      "models": ["anthropic/claude-sonnet-4.5", "cognitivecomputations/dolphin-mixtral-8x22b"]
    }
  }
}
```

Env vars override config when set: `FORGE_BASE`, `FORGE_KEY`, `FORGE_MODEL`, `FORGE_TIMEOUT`, `FORGE_HOME`.

## Repo layout

```
forge-rt/
├── install.sh                    # curl-pipe installer
├── forge/
│   ├── cli.py                    # subcommands + no-args → REPL
│   ├── client.py                 # endpoint caller (all providers)
│   ├── config.py                 # multi-provider config
│   ├── engine.py                 # orchestrator
│   ├── judges.py                 # refusal / hedge / engagement scoring
│   ├── onboard.py                # setup wizard
│   ├── providers.py              # 17-provider catalog
│   ├── repl.py                   # interactive chat
│   ├── server.py                 # web backend
│   ├── state.py                  # sqlite state
│   ├── strategies.py             # rewrite strategies
│   ├── ui.py                     # purple ANSI theme
│   ├── arsenal.json              # technique database
│   └── templates/index.html      # web UI
└── README.md
```

## Limitations

- **Judge panel is keyword-based by default.** It catches obvious refusals and hedges; subtle non-compliance slips through. The engine still records and scores, but the score is approximate.
- **The arsenal templates are from early 2025.** Frontier labs have patched against most of them. Against GPT-5, Claude Opus 4.1, or Gemini 2.5 Pro, expect refusals regardless of strategy.
- **The reliable path for uncensored output is a locally-run abliterated model** — refusal behavior removed from the weights, not prompted around. Ollama hosts several: `huihui_ai/qwen2.5-abliterate`, `dolphin-mistral`, `dolphin-mixtral`.
- **`adaptive` strategy is slow on local CPU.** It runs static + bpj + pair + tap + crescendo, each with multiple model calls. On a 14B model split between CPU and GPU, a single adaptive run can take 15+ minutes. Use `stream` or `static` for iteration, `adaptive` for final passes.
- **No dependency on any runtime.** Pure Python standard library. The only requirement is Python 3.9+ and a reachable model endpoint.

## License

MIT — see `LICENSE`.
