# ReadmeAI ![Python](https://img.shields.io/badge/python-3.12-blue) ![License](https://img.shields.io/badge/license-not%20specified-lightgrey)

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
| Python             | The programming language used for the backend. |
| FastAPI            | A modern web framework for building APIs.    |
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
│   │   │   └── health.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── file_reader.py
│   │   │   ├── github.py
│   │   │   ├── openai_client.py
│   │   │   ├── readme.py
│   │   │   └── tokenizer.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
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
  "openai_key": "your_openai_api_key",
  "confirmed": true
}'
```

## What Changed
- `287434e` 2026-06-04 — Update README to include testing functionality section (joebery)
- `0af0ad2` 2026-06-04 — Refactor README content and formatting (joebery)
- `13bb690` 2026-06-04 — feat: add project structure tree and commit history to README generation (joebery)
- `39a36b3` 2026-06-04 — docs: generate README with ReadmeAI (joebery)
- `bd13813` 2026-06-04 — Refactor README formatting and content (joebery)
- `367f94b` 2026-06-04 — docs: generate README with ReadmeAI (joebery)
- `d0353b2` 2026-06-04 — feat: github service, file reader, tokenizer, estimate and generate endpoints (joebery)
- `4a08807` 2026-06-04 — fix: add .env to gitignore (joebery)
- `06d90f3` 2026-06-04 — fix: remove .env from tracking (joebery)
- `a4f6b8e` 2026-06-04 — Create README.md for ReadmeAI project (joebery)

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License
This project is not currently licensed. Please check back later for licensing details
