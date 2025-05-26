<!-- README.md – modern & user-friendly -->
<div align="center">

<!-- Logo (scaled) -->
<img src="https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7" width="160" alt="LlamaBot logo">

# **LlamaBot**

_The open-source AI coding agent that chats, writes, and live-previews your web apps._

[![Live Site](https://img.shields.io/badge/Visit-LlamaPress.ai-brightgreen?style=for-the-badge&logo=safari)](https://llamapress.ai)
[![LLM Prompts](https://img.shields.io/badge/LangSmith-Prompts-blue?style=for-the-badge&logo=langchain)](https://smith.langchain.com/hub/llamabot)
[![MIT License](https://img.shields.io/github/license/KodyKendall/LlamaBot?style=for-the-badge)](LICENSE)
[![Stars last 10d](https://img.shields.io/badge/dynamic/json?style=for-the-badge&label=stars%20last%2010d&labelColor=555&color=brightgreen&query=%24.count&url=https://raw.githubusercontent.com/kodykendall/llamabot/main/.github/badges/stars_last10.json)](https://github.com/KodyKendall/LlamaBot/stargazers)
[![Discord](https://img.shields.io/badge/Join-Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/HtVVSxrK)

<!-- Demo GIF -->
<br>
<img src="https://llamapress-ai-image-uploads.s3.us-west-2.amazonaws.com/d7zial72abpkblr9n6lf8cov8lp4" width="600" alt="LlamaBot live demo">

</div>

---

## ✨ What is LlamaBot?

**LlamaBot** is an AI agent (built on **LangGraph + FastAPI**) that _converses_ with you while writing and modifying **HTML / CSS / JavaScript** in real time. Perfect for:

- 🎮 Mini-games (Canvas-based)  
- 🖥️ Portfolio & static sites  
- 💼 Business landing pages  
- 🧮 Interactive calculators & quote tools  
- …and a growing list of web-dev use cases!

---

## 🚀 Key Features

| Feature                | Description                                   |
|------------------------|-----------------------------------------------|
| **Chat-driven coding** | Type plain English; get instant code          |
| **Live preview**       | See changes render side-by-side as you chat   |
| **Hot-reload**         | Edits appear without refresh                  |
| **Multi-file support** | Handles HTML, CSS, and JS seamlessly          |
| **Zero-config start**  | Clone → `pip install` → `uvicorn` → create    |

---

## ⚡ Quick Start

```bash
# 1 — Clone
git clone https://github.com/KodyKendall/LlamaBot.git
cd LlamaBot

# 2 — Create & activate virtual env (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3 — Install deps
pip install -r requirements.txt

# 4 — Add your secrets
cat <<EOF > .env
OPENAI_API_KEY=sk-...
EOF
```

# 5 — Run it
uvicorn app:app --reload
Browse to http://localhost:8000/chat and start building.

## 🛠️ How It Works
Chat input → parsed by LlamaBot

Intent detection → reply naturally or generate code

LangGraph workflow produces / edits code snippets

WebSocket push updates the preview pane instantly

All orchestration logic lives in agents folder.

## 🧠 Agent Architecture
<div align="center">
<img src="https://llamapress-ai-image-uploads.s3.us-west-2.amazonaws.com/jpx9zdi6xirmo7xmfhmq6nsoiuhg" width="400" alt="LlamaBot Agent Architecture">
</div>

## 📂 Project Structure

```
LlamaBot/
├── app.py           # FastAPI + LangGraph server
├── chat.html        # Chat interface
├── page.html        # Live preview
├── agents/ 
│   ├── base_agent.py
│   ├── design_and_plan.py
│   ├── write_code.py
│   ├── respond_naturally.py
│   ├── route_initial_user_request.py
│   ├── nodes.py
│   └── state.py
└── requirements.txt
```

## View the key prompts this agent uses here: 
[![LLM Prompts](https://img.shields.io/badge/LangSmith-Prompts-blue?style=for-the-badge&logo=langchain)](https://smith.langchain.com/hub/llamabot)

## 💡 Example Prompts to Try

| Goal | Prompt |
|------|--------|
| Build Snake game | "Create a simple Snake game with arrow-key controls." |
| Personal portfolio | "Generate a minimal personal site with About, Projects, and Contact sections." |
| SaaS landing page | "Design a SaaS landing page hero with CTA and pricing table." |
| Mortgage calculator | "Make a responsive mortgage calculator that outputs monthly payment." |

## 🤝 Contributing
Fork the repo

Create a feature branch: git checkout -b feat/awesome

Commit, push, and open a PR 🎉

## 📜 License
Distributed under the MIT License – see LICENSE for full text.

<div align="center">
Made with ❤️ in San Francisco, by Kody Kendall — inspired by the next wave of AI code-gen tools.
</div>