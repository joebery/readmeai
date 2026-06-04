# ReadmeAI
![Python](https://img.shields.io/badge/language-Python-blue) ![License](https://img.shields.io/badge/license-Not%20Specified-lightgrey)

## Description
ReadmeAI is an AI-powered README generator that automates the creation of professional README files for GitHub repositories. By simply pasting a GitHub repository URL, ReadmeAI reads the repository's files, estimates the token cost for generating a README, and upon your confirmation, generates and pushes a polished README directly to your repository.

## Features
- **AI-Powered Generation**: Utilizes OpenAI's GPT-4o-mini to create high-quality README files.
- **Token Cost Estimation**: Provides an estimate of the token cost before generating the README.
- **Direct Integration**: Pushes the generated README directly to your GitHub repository.
- **File Scanning**: Reads through repository files to gather relevant information for the README.

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

## Tech Stack
- **Backend**: FastAPI, PostgreSQL, Redis
- **Containerization**: Docker Compose
- **AI Model**: OpenAI GPT-4o-mini
- **Frontend**: Next.js (coming soon)

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the terms of the MIT license.

## Status
Work in progress. Features and improvements are being actively developed.
