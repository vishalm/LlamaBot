# LlamaBot

LlamaBot is an AI Agent developed to help users create software projects by writing and modifying HTML, CSS, and JavaScript code. It's built using LangGraph.

![LlamaBot Logo](https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7)

## Project Overview

LlamaBot is an open-source AI agent that writes code primarily for:
- Creating basic games using HTML and JavaScript Canvas
- Building portfolio websites and static web pages
- Developing landing pages for businesses
- Creating dynamic calculators or quote tools for small businesses
- Soon, much more!

This project was created for educational purposes as a learning tool to explore & document how other code-generating AI tools like Lovable, Replit, Bolt, Claude Artifacts, and OpenAI's Canvas work under the hood.

## Features

- Interactive chat interface to communicate with the AI
- Real-time code generation and updates
- Live preview of the generated code
- Modern, responsive UI design
- Support for HTML, CSS, and JavaScript development

## Installation

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/KodyKendall/LlamaBot.git
cd LlamaBot
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory with your API keys:
```
LANGSMITH_API_KEY=your_langsmith_api_key
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000/chat
```

## How It Works

1. The user interacts with LlamaBot through the chat interface
2. Based on the user's input, LlamaBot determines whether to respond naturally or generate code
3. If code generation is requested, LlamaBot creates or modifies HTML, CSS, and JavaScript
4. The changes are immediately visible in the preview panel on the right

## Project Structure

- `app.py`: The main FastAPI application
- `chat.html`: The chat interface
- `page.html`: The generated code/preview page
- `prompts/`: LangChain prompt templates (hosted on LangChain Hub)

## Example Use Cases

- Create a simple game (like Snake, Platformer, etc.)
- Build a personal portfolio website
- Design a business landing page
- Develop interactive tools and calculators

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Source Code

The source code for this project is available at:
[https://github.com/KodyKendall/LlamaBot](https://github.com/KodyKendall/LlamaBot)

## License

This project is open source and available under the MIT License.

## Acknowledgements

- Developed by Kody Kendall
- Built with FastAPI, LangChain, and OpenAI technologies
- Inspired by similar AI code generation tools
