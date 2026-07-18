# Contributing to CourseForge

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to CourseForge. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by the [CourseForge Code of Conduct](.github/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Branch Strategy

- `main` — Production-ready code. All PRs eventually merge here.
- `develop` — Active development branch. Feature branches merge here.
- `feature/name-of-feature` — Use this format for new features.
- `bugfix/issue-description` — Use this format for bug fixes.
- `hotfix/critical-issue` — Emergency fixes straight into `main`.

## Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

**Format:**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

## Pull Request Process

1. Ensure your code conforms to the established Coding Standards.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent.
4. Your PR must pass all CI/CD workflows (`backend.yml` & `frontend.yml`).
5. You may merge the Pull Request in once you have the sign-off of at least one core developer.

## Coding Standards

### Backend (Python)
- Format code using `black` and `ruff`.
- Ensure type hints are used across the codebase (`mypy` compliant).
- Maintain SOLID principles.
- Use `AsyncSession` for all database interactions.
- Avoid circular imports.

### Frontend (React/Vite)
- Use standard functional components with hooks.
- Follow the provided Design System components (`src/components/ui`).
- No direct DOM manipulation; rely on React state.
- Keep `useEffect` usage minimal and well-documented.
- Maintain strict CSS scoping or use Vanilla CSS variables globally.

## Project Structure Guidelines

Please respect the existing project structure. 

- `backend/api/` — API routes and Pydantic schemas.
- `backend/db/models/` — SQLAlchemy ORM Models.
- `backend/services/` — Business logic (Keep routes thin).
- `frontend/src/components/` — Reusable React components.
- `frontend/src/pages/` — View-level components mapping to specific URLs.
- `frontend/src/api/` — React Query hooks and Axios configurations.
