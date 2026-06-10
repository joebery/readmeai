# ReadmeAI ![JavaScript](https://img.shields.io/badge/javascript-ES6%2B-yellow) ![License](https://img.shields.io/badge/license-not%20specified-lightgrey)

## Description
ReadmeAI is an AI-powered README generator that creates comprehensive and professional README files for your GitHub repositories. By leveraging OpenAI's language model, ReadmeAI analyzes your repository's structure, files, and recent commits to generate a tailored README that enhances your project's visibility and usability.

## Features
- Automatically generates README files based on repository content.
- Analyzes file types and recent commits to provide relevant information.
- Pushes generated README directly to your GitHub repository.
- Supports various programming languages and file formats.

## Tech Stack

| Technology         | Description                                   |
|--------------------|-----------------------------------------------|
| JavaScript         | The programming language used for the frontend. |
| FastAPI            | A modern web framework for building APIs in the backend. |
| PostgreSQL         | A powerful, open-source relational database.  |
| Redis              | In-memory data structure store for caching.   |
| OpenAI             | AI model used for generating README content.  |

## Project Structure
```
.
├── backend
│   ├── app
│   │   ├── routers
│   │   │   ├── __init__.py
│   │   │   ├── analyses.py
│   │   │   ├── health.py
│   │   │   ├── repos.py
│   │   │   └── webhook.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── file_reader.py
│   │   │   ├── github.py
│   │   │   ├── openai_client.py
│   │   │   ├── readme.py
│   │   │   ├── tokenizer.py
│   │   │   └── update.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── app
│   │   ├── analyses
│   │   │   └── [id]
│   │   │       └── page.jsx
│   │   ├── analyze
│   │   │   └── page.jsx
│   │   ├── globals.css
│   │   ├── layout.jsx
│   │   └── page.jsx
│   ├── components
│   │   └── StylePicker.jsx
│   ├── Dockerfile
│   ├── next.config.js
│   ├── package.json
│   ├── postcss.config.js
│   └── tailwind.config.js
├── postgres
│   └── init.sql
├── README.md
└── docker-compose.yml
```

## Installation

### Prerequisites
- Docker and Docker Compose installed on your machine.
- A GitHub account with a personal access token for API access.
- An OpenAI API key for generating README content.

### Clone the Repository
```bash
git clone https://github.com/joebery/readmeai.git
cd readmeai
```

### Configure Environment Variables
Create a `.env` file in the root directory and add your GitHub token and OpenAI API key:
```
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

### Build and Run the Application
```bash
docker-compose up --build
```

## Usage

### Estimate README Generation
To estimate the README generation for a repository, send a POST request to the `/api/v1/analyses/estimate` endpoint:
```bash
curl -X POST "http://localhost:8000/api/v1/analyses/estimate" \
-H "Content-Type: application/json" \
-d '{
  "repo_url": "https://github.com/owner/repo",
  "github_token": "your_github_token"
}'
```

### Confirm and Generate README
Once you've received the estimate, confirm the analysis and generate the README by sending a POST request to the `/api/v1/analyses` endpoint:
```bash
curl -X POST "http://localhost:8000/api/v1/analyses" \
-H "Content-Type: application/json" \
-d '{
  "analysis_id": "your_analysis_id",
  "github_token": "your_github_token",
  "openai_key": "your_openai_key",
  "confirmed": true
}'
```

## Recent Updates
- **2026-06-10**: Frontend scaffold, analyze page, style picker, preview/push/regenerate endpoints implemented.
- **2026-06-04**: Added mode 2 webhook, bot loop prevention, locked sections, and recent updates functionality.
- **2026-06-04**: Updated README formatting and content for clarity and completeness.
- **2026-06-04**: Enhanced README generation capabilities with additional project structure and commit history details.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bugs you encounter.

## License
This project is licensed under an unspecified license. Please check the repository for more details.