# ReadmeAI
![Python](https://img.shields.io/badge/language-Python-blue) ![License](https://img.shields.io/badge/license-Not%20Specified-lightgrey)

## Description
ReadmeAI is an AI-powered README generator that automates the creation of professional README files for GitHub repositories. By simply pasting a GitHub repository URL, ReadmeAI reads the repository's files, estimates the token cost for generating a README, and upon your confirmation, generates and pushes a polished README directly to your repository.

## Features
- **AI-Powered Generation**: Utilizes OpenAI's GPT-4o-mini to create high-quality README files.
- **Token Cost Estimation**: Provides an estimate of the token cost before generating the README.
- **Direct Integration**: Pushes the generated README directly to your GitHub repository.
- **File Scanning**: Reads through repository files to gather relevant information for the README.

## Tech Stack
| Technology        | Description                                      |
|-------------------|--------------------------------------------------|
| **Backend**       | FastAPI, PostgreSQL, Redis                       |
| **Containerization** | Docker Compose                               |
| **AI Model**      | OpenAI GPT-4o-mini                              |
| **Frontend**      | Next.js (coming soon)                           |

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
- Docker
- Docker Compose

### Clone the Repository
```bash
git clone https://github.com/joebery/readmeai.git
cd readmeai
```

### Build and Run
```bash
docker-compose up --build
```

## Usage
1. Start the application using Docker Compose.
2. Access the API at `http://localhost:8000`.
3. Use the `/api/v1/analyses/estimate` endpoint to estimate the token cost by providing your GitHub repository URL and GitHub token.
4. Confirm the token cost and proceed to generate the README using the `/api/v1/analyses` endpoint.

## What Changed
- `bd13813` 2026-06-04 — Refactor README formatting and content (joebery)
- `367f94b` 2026-06-04 — docs: generate README with ReadmeAI (joebery)
- `d0353b2` 2026-06-04 — feat: github service, file reader, tokenizer, estimate and generate endpoints (joebery)
- `4a08807` 2026-06-04 — fix: add .env to gitignore (joebery)
- `06d90f3` 2026-06-04 — fix: remove .env from tracking (joebery)
- `a4f6b8e` 2026-06-04 — Create README.md for ReadmeAI project (joebery)
- `8a7bdb3` 2026-06-04 — feat: initial project scaffold (joebery)

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the terms of the MIT license.