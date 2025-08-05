# Monorepo Structure and Tooling Setup

Implement the initial monorepo structure for the agentic PDF extraction tool.

Goals:
- Establish a clear separation between frontend and backend codebases.
- Enable rapid development and deployment workflows.

Acceptance Criteria:
- The repository contains top-level directories for `/frontend` (React) and `/backend` (FastAPI).
- Shared configuration (e.g., linting, formatting, pre-commit hooks) is set up at the root.
- README at the root describes the structure and how to run each part.

Technical Details:
- Architecture/Module Changes: Create `/frontend` and `/backend` directories. Add a root-level README and configuration files (e.g., .gitignore, .editorconfig).
- Integration Points: None yet, but ensure both apps can be run independently for development.
- Examples/Conventions: Follow standard monorepo conventions (e.g., Yarn workspaces or plain directories).
- Testing: No tests required at this step.
- Side Effects/Dependencies: None.

