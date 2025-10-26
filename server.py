# from mcp.server.fastmcp import FastMCP
# import main  # 👈 this imports your tools automatically

# if __name__ == "__main__":
#     print("🚀 FastMCP Server (main tools) is running locally with uv...")
#     main.mcp.run()
from mcp.server.fastmcp import FastMCP
import os
import logging

logging.basicConfig(level=logging.INFO)

# ✅ Define MCP server
mcp = FastMCP("mcp-server")

# ✅ Example tool
NOTES_FILE = "notes.txt"

def ensure_file():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")

@mcp.tool()
def add_note(message: str) -> str:
    ensure_file()
    with open(NOTES_FILE, "a") as f:
        f.write(message + "\n")
    return "Note saved!"

# ✅ Run server
if __name__ == "__main__":
    logging.info("🚀 FastMCP Server is running locally... waiting for Claude")
    try:
        mcp.run()
    except Exception as e:
        logging.error("❌ MCP crashed", exc_info=e)

    # Keep process alive
    import time
    while True:
        time.sleep(5)
