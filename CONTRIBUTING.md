# Contributing to CloudShop

Thank you for your interest in contributing to CloudShop! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/-CloudShop.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up development environment: `docker-compose up -d`

## Development Standards

### Python
- Follow PEP 8
- Use Black for formatting: `black backend/`
- Use isort for imports: `isort backend/`
- Use mypy for type checking: `mypy backend/`
- Minimum 80% test coverage

### React/TypeScript
- Use ESLint: `npm run lint --prefix frontend`
- Use Prettier: `npm run format --prefix frontend`
- TypeScript strict mode enabled
- Minimum 80% test coverage

### Commit Messages
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `style:`, `chore:`
- Example: `feat: add user authentication endpoint`

### Pull Requests
1. Create PR from feature branch to `develop`
2. Fill out PR template completely
3. Ensure CI/CD pipeline passes
4. Request code review (minimum 2 approvals)
5. Address review comments
6. Squash commits before merge

## Testing Requirements

- Write unit tests for new code
- Write integration tests for API changes
- Run full test suite before pushing: `pytest backend/` && `npm test --prefix frontend`
- Update tests when modifying existing code

## Documentation

- Update README if adding new features
- Add docstrings to all functions/classes
- Update API documentation in docs/api/
- Include examples for new endpoints

## Deployment Process

1. Merge to `develop` (staging environment)
2. After testing, merge `develop` → `main` (production)
3. Tag releases: `git tag -a v1.0.0 -m "Release version 1.0.0"`
4. CD pipeline automatically deploys to GKE

## Reporting Issues

- Check existing issues first
- Provide reproduction steps
- Include environment details
- Attach error logs and screenshots

Thank you for contributing!
