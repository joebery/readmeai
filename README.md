# ReadmeAI ![JavaScript](https://img.shields.io/badge/javascript-ES6%2B-yellow) ![Python](https://img.shields.io/badge/python-3.12-blue) ![CSS](https://img.shields.io/badge/css-3%2B-blue) ![TypeScript](https://img.shields.io/badge/typescript-4%2B-blue) ![Docker](https://img.shields.io/badge/docker-20%2B-blue) ![License](https://img.shields.io/badge/license-not%20specified-lightgrey)

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
| Python             | The programming language used for the backend. |
| CSS                | Styles the frontend application.              |
| TypeScript         | Used for type safety in the frontend code.   |
| Docker             | Containerization for easy deployment.         |

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
To estimate the README generation for a repository, send a POST request to the estimate endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/analyses/estimate \
-H "Content-Type: application/json" \
-d '{
  "repo_url": "https://github.com/yourusername/yourrepo",
  "github_token": "your_github_token",
  "style": "professional"
}'
```

### Confirm and Generate README
Once you have the estimate, confirm the generation:
```bash
curl -X POST http://localhost:8000/api/v1/analyses \
-H "Content-Type: application/json" \
-d '{
  "analysis_id": "your_analysis_id",
  "github_token": "your_github_token",
  "openai_key": "your_openai_key",
  "confirmed": true
}'
```

## Recent Updates
- **2026-06-10**: Merged branch 'main' of https://github.com/joebery/readmeai.
- **2026-06-10**: Added multi-language badges, preview before push, regenerate with feedback, discard, and style picker features.
- **2026-06-10**: Updated README documentation.
- **2026-06-10**: Implemented frontend scaffold, analyze page, style picker, and preview/push/regenerate endpoints.
- **2026-06-04**: Introduced mode 2 webhook, bot loop prevention, locked sections, and recent updates functionality.
- **2026-06-04**: Updated README documentation.
- **2026-06-04**: Fixed README.md license section formatting.
- **2026-06-04**: Generated README with ReadmeAI.
- **2026-06-04**: Updated README to include testing functionality section.
- **2026-06-04**: Refactored README content and formatting.

## Contributing
Contributions to ReadmeAI are welcome! Please feel free to submit a pull request or open an issue for any enhancements, bug fixes, or suggestions.

## License
This project is not licensed under any specific license. Please check the repository for more details.