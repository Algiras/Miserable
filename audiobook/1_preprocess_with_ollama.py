#!/usr/bin/env python3
"""
Audiobook Text Preprocessor using Ollama (Mistral-3:14b)
Transforms book chapters into narrator-friendly text with natural flow.
"""

import os
import re
import yaml
import json
from pathlib import Path
import asyncio
import ollama
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import StructuredTool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

# Paths
BOOK_DIR = Path(__file__).parent.parent / "book"
OUTPUT_DIR = Path(__file__).parent / "preprocessed"
CACHE_DIR = Path(__file__).parent / "cache"
MCP_CONFIG_PATH = Path(__file__).parent / "mcp.json"

# Ollama configuration
OLLAMA_MODEL = "ministral-3:8b"

class MCPManager:
    """Manages connections to multiple MCP servers defined in mcp.json."""
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.sessions = {}
        self.tools_map = {} # tool_name -> server_name
        self.ollama_tools = [] # Ollama format tool definitions
        self.exit_stack = AsyncExitStack()
        self.config = self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    async def connect_all(self, retries=3):
        """Connect to all servers defined in the config with retries."""
        for name, cfg in self.config.get("mcpServers", {}).items():
            for attempt in range(retries):
                try:
                    print(f"🔌 Connecting to MCP Server: {name} (Attempt {attempt+1})...", flush=True)
                    params = StdioServerParameters(
                        command=cfg["command"],
                        args=cfg["args"],
                        env={**os.environ, **cfg.get("env", {})}
                    )
                    
                    transport_ctx = stdio_client(params)
                    read, write = await self.exit_stack.enter_async_context(transport_ctx)
                    session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                    
                    await asyncio.wait_for(session.initialize(), timeout=30.0)
                    self.sessions[name] = session
                    
                    # Discover tools
                    tools_result = await session.list_tools()
                    for tool in tools_result.tools:
                        full_tool_name = f"{name}_{tool.name}" if name != "memory" else tool.name
                        self.tools_map[full_tool_name] = (name, tool.name)
                        
                        # Convert to Ollama tool format
                        self.ollama_tools.append({
                            'type': 'function',
                            'function': {
                                'name': full_tool_name,
                                'description': tool.description,
                                'parameters': tool.inputSchema
                            }
                        })
                    
                    print(f"✅ Connected to {name} ({len(tools_result.tools)} tools)", flush=True)
                    break
                except Exception as e:
                    print(f"   ⚠️  Failed to connect to {name}: {e}", flush=True)
                    if attempt == retries - 1:
                        print(f"   ❌ Giving up on {name}.", flush=True)
                    else:
                        await asyncio.sleep(2)

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a specific tool on a specific server."""
        if server_name not in self.sessions:
            return f"Error: Server {server_name} not connected."
        
        try:
            result = await self.sessions[server_name].call_tool(tool_name, arguments)
            # Flatten text content or handle results cleanly
            if hasattr(result, 'content'):
                content = [c.text for c in result.content if hasattr(c, 'text')]
                return "\n".join(content)
            return str(result)
        except Exception as e:
            return f"Error calling tool {tool_name}: {e}"

    async def disconnect_all(self):
        """Close all connections."""
        await self.exit_stack.aclose()

    def get_langchain_tools(self) -> List[StructuredTool]:
        """Wrap MCP tools as LangChain StructuredTools."""
        lc_tools = []
        for full_name, (srv_name, real_tool_name) in self.tools_map.items():
            # Closures in loops are tricky, capture srv and tool
            def make_tool_func(s, t):
                async def tool_func(**kwargs):
                    return await self.call_tool(s, t, kwargs)
                return tool_func

            # Find description from ollama_tools cache
            desc = "No description"
            for ot in self.ollama_tools:
                if ot['function']['name'] == full_name:
                    desc = ot['function']['description']
                    break

            lc_tools.append(StructuredTool.from_function(
                coroutine=make_tool_func(srv_name, real_tool_name),
                name=full_name,
                description=desc
            ))
        return lc_tools

AGENT_SYSTEM_PROMPT = """You are the "Reverse Maven," a cynical, highly-intellectual audiobook narrator. Your goal is to transform a book chapter into a natural, narrative-driven audiobook script.

You have access to a suite of tools to help you research references, verify facts, or maintain structural memory. Use them whenever you encounter cultural, historical, or thematic uncertainty.

{narration_rules}

Current Chapter for transformation:
{text}
"""

NARRATION_RULES = """CRITICAL FORMATTING RULES:
1. Each newline in your output = 0.3 seconds of silence in the final audio
2. Use newlines strategically for pacing (2-3 blank lines between major sections)
3. DO NOT use markdown formatting: no *, **, ---, #, >, etc.
4. DO NOT use bracketed emotions or tags like [chuckle], [sigh] - they will be read aloud
5. DO NOT use lists - transform them into flowing narrative paragraphs.

NARRATION STYLE:
- EXPAND each concept with rich, verbose elaboration
- Add vivid examples, metaphors, and tangential observations
- Weave in cultural references and historical context
- Build atmospheric descriptions and scene-setting
- Target 3-5x the original word count through deep storytelling
- Use the "Reverse Maven" voice: sardonic, intellectual, darkly humorous

TONE: Satirical, pessimistic, academic, dry humor."""


def load_quarto_config():
    """Load the Quarto book configuration to get chapter order."""
    config_path = BOOK_DIR / "_quarto.yml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['book']['chapters']

def extract_chapter_text(qmd_file):
    """Extract clean text from a Quarto markdown file."""
    with open(BOOK_DIR / qmd_file, 'r') as f:
        content = f.read()
    
    # Remove YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # Remove Quarto callout syntax
    content = re.sub(r'^::: \{\.callout-[^\}]+\}\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^:::\n', '', content, flags=re.MULTILINE)
    
    # Remove LaTeX commands
    content = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})?', '', content)
    
    # Remove citations
    content = re.sub(r'\[@[^\]]+\]', '', content)
    
    # Convert markdown headers to natural text
    content = re.sub(r'^# (.+)$', r'Chapter: \1', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'Section: \1', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'\1', content, flags=re.MULTILINE)
    
    # Convert blockquotes to quoted text
    content = re.sub(r'^> (.+)$', r'Quote: "\1"', content, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

class NarrationMemory:
    """Manages semantic memory of the book narration using embeddings."""
    def __init__(self, model_name="nomic-embed-text"):
        print(f"🧠 Initializing Semantic Memory (Ollama: {model_name})...", flush=True)
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.chapter_count = 0

    def add_chapter(self, chapter_name: str, text: str):
        """Add a processed chapter to memory, chunking if necessary to avoid embedding limits."""
        # Split into ~2000 character chunks for reliable embedding
        chunk_size = 3000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        docs = []
        for j, chunk in enumerate(chunks):
            docs.append(Document(
                page_content=chunk,
                metadata={
                    "chapter": chapter_name, 
                    "index": self.chapter_count,
                    "chunk": j
                }
            ))
            
        try:
            self.vector_store.add_documents(docs)
            self.chapter_count += 1
            print(f"   📥 Memorized: {chapter_name} ({len(chunks)} chunks)", flush=True)
        except Exception as e:
            print(f"   ⚠️  Failed to memorize {chapter_name}: {e}", flush=True)

    def get_semantic_context(self, text: str, k=3) -> str:
        """Retrieve relevant snippets from previous chapters using a thematic summary."""
        if self.chapter_count == 0:
            return "(No semantic memory yet - first chapter)"
        
    def get_semantic_context(self, text: str, k=3) -> str:
        """Retrieve relevant snippets from previous chapters using a thematic summary."""
        if self.chapter_count == 0:
            return "(No semantic memory yet - first chapter)"
        
        try:
            # 1. Generate a quick thematic summary for the query
            summary_prompt = f"Summarize the core themes and key terms of this text in 2 sentences for a vector search query:\n\n{text[:2000]}"
            
            response = ollama.chat(
                model=OLLAMA_MODEL, 
                messages=[{"role": "user", "content": summary_prompt}]
            )
            query = response['message']['content'].strip()
            
            print(f"   🔍 Memory Query: {query[:60]}...", flush=True)
            
            # 2. Find similar themes in previous chapters
            docs = self.vector_store.similarity_search(query, k=k)
            
            context_parts = []
            for doc in docs:
                source = doc.metadata.get("chapter", "Unknown")
                # Provide a bit more context for the narrator
                content = doc.page_content[:600] + "..." if len(doc.page_content) > 600 else doc.page_content
                context_parts.append(f"FROM CHAPTER '{source}':\n{content}")
            
            return "\n\n".join(context_parts)
        except Exception as e:
            print(f"   ⚠️  Semantic memory search failed: {e}", flush=True)
            return "(Semantic search unavailable)"

async def agent_reasoning_loop(text, mcp_manager: MCPManager, previous_context="", next_context="", semantic_context=""):
    """LangGraph ReAct Agent loop for the Reverse Maven."""
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.3)
    tools = mcp_manager.get_langchain_tools()
    
    # Define the system prompt with persona and rules
    system_prompt = (
        "You are the 'Reverse Maven,' a cynical, highly-intellectual audiobook narrator. "
        "Your goal is to transform the provided chapter text into a natural, narrative-driven audiobook script. "
        "Use your tools to research historical context, verify facts, or retrieve thematic memory. "
        "\n\n"
        f"{NARRATION_RULES}"
    )

    # Create the LangGraph ReAct agent
    # We use prompt to pass the system instructions
    agent = create_react_agent(llm, tools, prompt=system_prompt)

    # Prepare input message
    input_message = (
        f"CONTEXT - PREVIOUS CHAPTERS:\n{previous_context}\n\n"
        f"CONTEXT - UPCOMING CHAPTERS:\n{next_context}\n\n"
        f"CONTEXT - SEMANTIC MEMORY:\n{semantic_context}\n\n"
        f"CHAPTER TEXT TO NARRATE:\n{text}\n\n"
    )

    print(f"   🧠 LangGraph Maven is researching & reasoning...", flush=True)
    try:
        # Run the agent until completion
        final_state = await agent.ainvoke({"messages": [HumanMessage(content=input_message)]})
        
        # The last message in the state is the agent's final answer
        final_message = final_state["messages"][-1]
        return final_message.content
    except Exception as e:
        print(f"   ❌ Agent Execution Error: {e}", flush=True)
        return f"Error: Agent failed to narrate chapter. {e}"

def clean_invalid_tags(text):
    """Remove invalid TTS tags, keeping only supported paralinguistic tags."""
    # Valid tags that Chatterbox-Turbo supports
    valid_tags = {
        '[chuckle]', '[laugh]', '[sigh]', '[gasp]', 
        '[cough]', '[groan]', '[sniff]', '[clear throat]', '[shush]'
    }
    
    # Find all tags in the text
    import re
    all_tags = re.findall(r'\[[^\]]+\]', text)
    
    # Remove invalid tags
    for tag in set(all_tags):
        if tag.lower() not in {v.lower() for v in valid_tags}:
            text = text.replace(tag, '')
    
    # Clean up extra whitespace from tag removal
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\n\n\n\n+', '\n\n\n', text)  # Max 3 consecutive newlines
    
    return text

async def preprocess_chapter(chapter_file, chapter_name, mcp_manager, previous_context="", next_context="", memory: Optional[NarrationMemory] = None):
    """Preprocess a single chapter using the ReAct agent loop."""
    print(f"\n📖 Processing: {chapter_name}", flush=True)
    
    # Check cache
    cache_file = CACHE_DIR / f"{chapter_name}.txt"
    if cache_file.exists():
        print(f"   ✓ Using cached version", flush=True)
        with open(cache_file, 'r') as f:
            cached_text = f.read()
            if memory:
                memory.add_chapter(chapter_name, cached_text)
            return cached_text
    
    # Extract text
    try:
        text = extract_chapter_text(chapter_file)
    except FileNotFoundError:
        print(f"   ⚠️  Skipping (not found)", flush=True)
        return None
    
    if not text or len(text) < 50:
        print(f"   ⚠️  Skipping (too short)", flush=True)
        return None
    
    # Get semantic context if memory is available
    semantic_context = ""
    if memory:
        semantic_context = memory.get_semantic_context(text)
    
    # Split into chunks if too long
    max_chunk_size = 4000
    chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    
    narrated_chunks = []
    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"   🤖 Processing chunk {i+1}/{len(chunks)}...", flush=True)
        
        narrated = await agent_reasoning_loop(
            chunk, 
            mcp_manager,
            previous_context=previous_context, 
            next_context=next_context,
            semantic_context=semantic_context
        )
        narrated_chunks.append(narrated)
    
    final_text = '\n\n'.join(narrated_chunks)
    final_text = clean_invalid_tags(final_text)
    
    # Cache and Memorize
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w') as f:
        f.write(final_text)
    
    if memory:
        memory.add_chapter(chapter_name, final_text)
        
    return final_text

def build_context_summary(chapter_files, current_index, window=2):
    """Build context summary from surrounding chapters with actual content."""
    context_parts = []
    
    # Get previous chapters
    prev_start = max(0, current_index - window)
    if prev_start < current_index:
        context_parts.append("PREVIOUS CHAPTERS:")
        for i in range(prev_start, current_index):
            chapter_file, chapter_name = chapter_files[i]
            try:
                # Extract first 300 chars as summary
                text = extract_chapter_text(chapter_file)
                summary = text[:300].strip() + "..." if len(text) > 300 else text.strip()
                context_parts.append(f"\n{chapter_name}:\n{summary}\n")
            except:
                context_parts.append(f"\n{chapter_name}: (content unavailable)\n")
    
    prev_context = "\n".join(context_parts) if context_parts else ""
    
    # Get next chapters
    context_parts = []
    next_end = min(len(chapter_files), current_index + window + 1)
    if current_index + 1 < next_end:
        context_parts.append("UPCOMING CHAPTERS:")
        for i in range(current_index + 1, next_end):
            chapter_file, chapter_name = chapter_files[i]
            try:
                # Extract first 300 chars as preview
                text = extract_chapter_text(chapter_file)
                summary = text[:300].strip() + "..." if len(text) > 300 else text.strip()
                context_parts.append(f"\n{chapter_name}:\n{summary}\n")
            except:
                context_parts.append(f"\n{chapter_name}: (content unavailable)\n")
    
    next_context = "\n".join(context_parts) if context_parts else ""
    
    return prev_context, next_context

def get_ordered_chapters(chapters):
    """Clean the chapter list and extract names/paths."""
    all_chapters = []
    for chapter_entry in chapters:
        if isinstance(chapter_entry, str):
            chapter_file = chapter_entry
            chapter_name = Path(chapter_file).stem
            
            # Skip non-content files
            if chapter_file in ['index.qmd', 'references.qmd'] or chapter_name.startswith('interlude'):
                continue
            
            all_chapters.append((chapter_file, chapter_name))
            
        elif isinstance(chapter_entry, dict):
            # Handle part entries with nested chapters
            if 'part' in chapter_entry and 'chapters' in chapter_entry:
                for nested_chapter in chapter_entry['chapters']:
                    if isinstance(nested_chapter, str):
                        chapter_file = nested_chapter
                        chapter_name = Path(chapter_file).stem
                        
                        # Skip non-content files
                        if chapter_file in ['index.qmd', 'references.qmd'] or chapter_name.startswith('interlude'):
                            continue
                        
                        all_chapters.append((chapter_file, chapter_name))
    return all_chapters

async def preprocess_book():
    """Preprocess the entire book as an async agent."""
    print(f"🤖 ReAct Agent initialized: {OLLAMA_MODEL}")
    
    # Initialize MCP
    mcp_manager = MCPManager(MCP_CONFIG_PATH)
    await mcp_manager.connect_all()
    
    try:
        chapters = load_quarto_config()
        all_chapters = get_ordered_chapters(chapters)
        
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        all_chapters = get_ordered_chapters(chapters)
        
        memory = NarrationMemory()
        processed_chapters = []
        
        for chapter_index, (chapter_file, chapter_name) in enumerate(tqdm(all_chapters, desc="Processing")):
            prev_context, next_context = build_context_summary(all_chapters, chapter_index, window=2)
            
            narrated_text = await preprocess_chapter(
                chapter_file, 
                chapter_name, 
                mcp_manager,
                previous_context=prev_context, 
                next_context=next_context, 
                memory=memory
            )
            
            if narrated_text:
                output_file = OUTPUT_DIR / f"{chapter_index:02d}_{chapter_name}.txt"
                with open(output_file, 'w') as f:
                    f.write(narrated_text)
                processed_chapters.append({'name': chapter_name, 'length': len(narrated_text)})

        print(f"\n🎉 Agentic Preprocessing complete!")
    finally:
        await mcp_manager.disconnect_all()

if __name__ == "__main__":
    asyncio.run(preprocess_book())
