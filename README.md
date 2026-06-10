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
│   │   ├── ReadmeComparison.jsx
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

### Run the Application
To run the application, use Docker Compose:
```bash
docker-compose up --build
```

## Usage
1. Navigate to `http://localhost:3000` in your web browser.
2. Paste your GitHub repository URL into the designated field.
3. Enter your GitHub token and OpenAI API key.
4. Select a style for your README.
5. Click on "Generate README" to initiate the process.

## Recent Updates
- `c4ed04c` 2026-06-10 — feat: multi-language badges, preview before push, regenerate with feedback, discard, style picker (joebery)
- `8c1c5f1` 2026-06-10 — feat: frontend scaffold, analyze page, style picker, preview/push/regenerate endpoints (joebery)
- `0076c17` 2026-06-04 — feat: mode 2 webhook, bot loop prevention, locked sections, recent updates (joebery)

## Contributing
We welcome contributions to ReadmeAI! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## License
This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.