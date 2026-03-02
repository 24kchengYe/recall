# Recall — Cross-Project Session Manager for Claude Code

> **One command to manage all your Claude Code conversations, across every project.**

## The Problem

Claude Code stores conversation history **per project directory**. Each project has its own isolated session index under `~/.claude/projects/<encoded-project-path>/`. This means:

- Sessions from **Project A are invisible** when you're working in **Project B**
- You cannot browse, search, or resume conversations across projects
- Built-in `/resume` only shows sessions from the **current** project directory
- There is no way to organize conversations by topic — they are locked to whichever directory you happened to open

This is true whether you use VS Code, JetBrains, Cursor, Windsurf, or the terminal CLI. It's a fundamental architectural limitation.

### "But Claude Code can read files from other directories..."

Yes — Claude Code's agent can read, write, and search files anywhere on your machine. **But that's file access, not session management.** The conversation history itself (who said what, tool calls, context windows) is stored in `.jsonl` files tied to a specific project. There is no built-in mechanism to:

- **Discover** what conversations happened in other projects
- **Load past conversation content** as context reference in a new session
- **Categorize** conversations by topic (research vs. coding vs. writing)
- **Search** across all your conversations by keyword
- **Resume** a conversation that lives in a different project directory

Recall fills this gap.

## What Recall Does

Recall creates a **centralized session index** — a management layer that maps to original session files while keeping backup copies organized by user-defined categories.

```
D:\claude-sessions\               ← Central directory (configurable)
├── _config.json                   ← Categories & settings
├── 论文/
│   ├── BSAS论文修改_meta.json     ← Metadata + mapping to original
│   └── BSAS论文修改.jsonl         ← Full session backup
├── 代码/
│   ├── WebApp重构_meta.json
│   └── WebApp重构.jsonl
├── 学习/
└── ...
```

**Key design**: The central directory is an **index layer**, not a replacement for Claude Code's native storage. Recall copies sessions as backups and maintains bidirectional metadata links to the originals.

## Commands

| Command | Description |
|---------|-------------|
| `/recall` | Show interactive action menu |
| `/recall save` | Save current session to central directory |
| `/recall browse` | Visual hierarchical browsing (categories → sessions → actions) |
| `/recall list` | List all saved sessions in a table |
| `/recall list search <keyword>` | Search sessions by name, summary, or tags |
| `/recall list recent [N]` | Show N most recently modified sessions |
| `/recall list stats` | Statistics overview (counts, categories, largest session) |
| `/recall load` | Load a past session as reference context in current conversation |
| `/recall resume` | Find and resume a session from any project |
| `/recall rename` | Rename a session (bidirectional sync with original project) |
| `/recall move` | Move session to a different category |
| `/recall manage` | Manage categories (add, remove, view stats) |

## Core Features

### Save & Organize
Save any conversation to a central location with a custom name and category. Default categories: 学习, 生活, 代码, 算法, 论文, 工作, 杂项 — fully customizable.

**Auto-update**: If you save a session that was previously saved, Recall automatically updates the backup without asking — no need to re-select name or category. Just `/recall save` again whenever you want a fresh snapshot.

**Filesystem-first session detection**: Recall identifies the current session by checking which `.jsonl` file was most recently modified on disk, not by relying on `sessions-index.json` (which can be stale). This ensures accurate detection even when Claude Code hasn't updated its index.

### Cross-Project Context Loading (`/recall load`)
The killer feature. Load content from a past conversation into your **current** session as reference context. Two modes:
- **Brief**: User questions + assistant text answers only
- **Detailed**: Includes tool usage summaries (which files were edited, what commands ran)

This enables cross-project knowledge transfer — discuss an algorithm in Project A, then load that context while working in Project B.

### Interactive Browse (`/recall browse`)
Visual, clickable hierarchical navigation designed for managing large numbers of sessions:
1. **Layer 1**: Category overview (with session counts)
2. **Layer 2**: Session list within a category (paginated, 3 per page)
3. **Layer 3**: Session detail + executable actions (load, resume, rename, move)

### Search & Statistics
- **Search**: Find sessions by keyword across name, summary, first prompt, and tags
- **Recent**: Quick view of your N most recently modified sessions
- **Stats**: Overview of total sessions, messages, per-category counts, most active category, largest session

### Resume from Anywhere
Browse your central index, select a session, and Recall helps you resume it — even if it's from a different project:

- **Same project**: Shows the `claude --resume` command directly
- **Different project**: Offers to open a **new VSCode window** or **new terminal** at the target project directory, then provides the resume command to paste
- **Original deleted**: Restores from backup automatically, then provides the resume command

No more manually hunting for which directory a conversation lives in.

### Bidirectional Rename
When you rename a session in Recall, it updates **both** the central index and the original project's `sessions-index.json`. No desync.

## Installation

### From Skills CLI (Recommended)

```bash
npx skills add 24kchengYe/recall
```

### Manual Installation

```bash
# macOS / Linux
git clone https://github.com/24kchengYe/recall.git ~/.claude/skills/recall

# Windows
git clone https://github.com/24kchengYe/recall.git %USERPROFILE%\.claude\skills\recall
```

## Requirements

- Claude Code (VS Code, JetBrains, Cursor, Windsurf, or terminal CLI)
- Python 3.8+ (for the helper script that parses `.jsonl` session files)

## Configuration

On first `/recall save`, Recall initializes:
- **Storage path**: Default `D:\claude-sessions\` — you'll be prompted to confirm or customize
- **Categories**: Default set provided, fully customizable via `/recall manage`

All settings stored in `<basePath>/_config.json`.

## How Claude Code Stores Sessions (Background)

For those curious about the internals:

- Each project maps to a directory: `~/.claude/projects/<encoded-path>/`
- Sessions are stored as `.jsonl` files (one JSON object per line)
- A `sessions-index.json` per project tracks session metadata
- Message types include: `user`, `assistant`, `system`, `progress`, and more
- Context compression creates `compact_boundary` markers in long sessions

Recall reads these native files and builds an index on top of them — it doesn't modify or replace Claude Code's storage, just adds a cross-project management layer.

**Important finding**: `sessions-index.json` is **not always up to date**. Claude Code uses incremental updates — it adds entries on session creation and rename, but does NOT rebuild the full index. Many sessions may exist as `.jsonl` files on disk without having an entry in the index. Recall handles this by using filesystem modification times as the primary session detection method.

## Recall vs. Built-in Commands

| Capability | Built-in `/resume` | Recall |
|---|---|---|
| See sessions from other projects | No | Yes |
| Organize by topic/category | No | Yes |
| Search across all conversations | No | Yes |
| Load past conversation as context | No | Yes |
| Resume from any directory | No | Yes |
| Rename with bidirectional sync | No | Yes |
| Central backup of all sessions | No | Yes |
| Statistics & overview | No | Yes |

## License

MIT
