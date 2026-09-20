# How to Give Ollama Agents Live Web Access with Zenrows MCP

A local Ollama agent that reads live web pages, including bot-protected ones, through the Zenrows MCP server. The model runs on your machine and never contacts the target site directly.

## Features
- Connects the Zenrows MCP server to a local Ollama model over STDIO
- Runs a research agent that fetches and reads protected pages
- Uses the `extract` tool with Adaptive Stealth Mode for structured JSON output
- Tests against a Cloudflare-fronted target and a purpose-built antibot challenge page
- Includes a control script showing what a plain HTTP request returns on the same URL
- Filters invented tool arguments before they reach the MCP server

## Prerequisites
- Python 3.10 or later
- Node.js (the MCP server runs through `npx`)
- Ollama installed and running, with a tool-capable model such as `qwen3`
- A Zenrows API key from [app.zenrows.com](https://app.zenrows.com/register)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bennykillua/ollama-agent-web-access-zenrows-mcp.git
cd ollama-agent-web-access-zenrows-mcp
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

```bash
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate`.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install and start Ollama

```bash
brew install ollama
brew services start ollama
ollama pull qwen3
```

## Configuration

Create a `.env` file in the project root:

```
ZENROWS_API_KEY=your_api_key
```

The key is 41 characters: one digit followed by 40 hexadecimal characters. Copy it from your [Zenrows dashboard](https://app.zenrows.com/settings/api-keys).

`zenrows-mcp.json` holds the MCP server configuration used by the ollmcp bridge. Replace the placeholder key before running it:

```json
{
  "mcpServers": {
    "zenrows": {
      "command": "npx",
      "args": ["-y", "@zenrows/mcp"],
      "env": {
        "ZENROWS_API_KEY": "YOUR_ZENROWS_API_KEY"
      }
    }
  }
}
```

Both `.env` and `zenrows-mcp.json` are excluded from version control.

## Project structure

```
.
├── agent.py
├── cloudflare_site.py
├── without_zenrows.py
├── zenrows-mcp.json.example
├── requirements.txt
├── .gitignore
└── README.md
```

- `agent.py` runs the agent against the antibot challenge page
- `cloudflare_site.py` runs the same loop against a Cloudflare-fronted target
- `without_zenrows.py` is the control: a plain HTTP request to the same URL

## How it works

The agent has four layers, and the model never touches the target site.

```
You ask a question
  ↓
Ollama picks a tool and its arguments
  ↓
Zenrows MCP fetches the page through managed proxies and a browser
  ↓
The model reads clean content from its context and answers
```

Ollama returns tool calls but does not execute them. The script calls the MCP server, feeds the result back as a `tool` message, and asks the model again.

## Running the project

Verify the MCP connection first:

```bash
ollmcp --servers-json zenrows-mcp.json --model qwen3:latest
```

Then run the agent:

```bash
python agent.py
```

The Cloudflare target:

```bash
python cloudflare_site.py
```

The control, for comparison:

```bash
python without_zenrows.py
```

## Output

`agent.py` prints the tool call, the first 300 characters of the tool result, and the model's answer. The result is structured JSON with an `ok` flag, the extraction mode, and a `data` object holding the fields.

`without_zenrows.py` prints a status code and response length. On a protected target it returns 403 and a challenge page rather than content.

## Technologies
- Python
- Ollama
- Zenrows
- Model Context Protocol
- ollmcp


## Related article

This repository accompanies the Zenrows article:

[How to Give Ollama Agents Live Web Access with Zenrows MCP]()