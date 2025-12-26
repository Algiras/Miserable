# Blog Enhancement System

## Overview

This system uses a LangGraph ReAct agent to enhance blog posts with research, elaboration, and the "Reverse Maven" voice.

## Architecture

```
blog/
├── scripts/
│   ├── preprocessor.py      # ReAct agent core (adapted from audiobook)
│   └── enhance_posts.py     # Sequential processing pipeline
├── cache/                    # Enhanced post cache
└── src/content/blog/         # Blog posts (53 total)
```

## Features

- **Sequential Processing**: Posts are processed in chronological order
- **Context Awareness**: Each post builds on previous posts
- **Semantic Memory**: Cross-post references using vector embeddings
- **Book Integration**: Uses book chapters as source material
- **Research Tools**: Brave Search, Fetch, Memory MCP servers
- **Markdown Output**: Proper formatting with headers, callouts, quotes

## Usage

### Enhance All Posts

```bash
cd blog/scripts
python3 enhance_posts.py
```

This will:
1. Connect to Dockerized MCP servers
2. Process all 53 posts sequentially
3. Match each post to its corresponding book chapter
4. Research and expand content to 2,500-4,000 words
5. Cache results for resumability
6. Update posts in place

### Test Single Post

```python
# Coming soon: test_single_post.py
```

## Configuration

- **Model**: `ministral-3:8b` (via Ollama)
- **Target Length**: 2,500-4,000 words per post
- **Expansion Ratio**: 5-10x from stub content
- **Context Window**: 2 previous posts
- **Memory**: Semantic search across all processed posts

## Output Format

Each enhanced post includes:
- **Frontmatter**: Preserved from original (title, date, heroImage)
- **Introduction**: Hook with Maven voice
- **Body**: 3-5 sections with research and examples
- **Callouts**: `::: {.callout-tip}` blocks for analytical notes
- **Quotes**: `>` blockquotes for key observations
- **Post-Script**: Maven's signature closing

## Dependencies

- Python 3.11+
- Ollama (ministral-3:8b, nomic-embed-text)
- Docker (for MCP servers)
- LangChain, LangGraph
- MCP Python SDK

## Cache Management

Enhanced posts are cached in `blog/cache/` by filename. To regenerate a post:

```bash
rm blog/cache/2025-01-29-the-aesthetic-of-neglect.md
python3 enhance_posts.py
```

## Monitoring

The pipeline provides real-time progress:
- 🔌 MCP server connections
- 📖 Book chapter matching
- 🧠 Agent research & writing
- ✅ Word count and completion status
