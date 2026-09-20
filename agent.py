from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "@zenrows/mcp"],
    env={**os.environ, "ZENROWS_API_KEY": os.environ["ZENROWS_API_KEY"]},
)
MODEL = "qwen3:latest"
QUESTION = "Extract the page heading from https://www.scrapingcourse.com/antibot-challenge."
ALLOWED_ARGS = {"url", "mode", "css_extractor"}

async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listed = await session.list_tools()
            tools = [
                {"type": "function", "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                }}
                for t in listed.tools if t.name == "extract"
            ]

            messages = [{"role": "user", "content": QUESTION}]
            reply = ollama.chat(model=MODEL, messages=messages, tools=tools)
            messages.append(reply["message"])

            for call in reply["message"].get("tool_calls", []):
                args = {k: v for k, v in call.function.arguments.items() if k in ALLOWED_ARGS}
                args["mode"] = "auto"
                args["mode_auto"] = True
                print("calling", call.function.name, args)
                result = await session.call_tool(call.function.name, args)
                text = result.content[0].text
                print("result:", text[:300])
                messages.append({"role": "tool", "content": text})

            print(ollama.chat(model=MODEL, messages=messages, tools=tools)["message"]["content"])

asyncio.run(main())