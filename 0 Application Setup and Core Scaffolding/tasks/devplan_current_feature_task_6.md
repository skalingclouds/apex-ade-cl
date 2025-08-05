# React Frontend Bootstrapping and Core Layout

Bootstrap the React frontend with routing, state management, and the basic dual-pane layout.

Goals:
- Provide a foundation for the UI with navigation and state handling.
- Implement the dual-pane review/chat layout as described in the PRD.

Acceptance Criteria:
- React app is initialized in `/frontend`.
- Routing is set up for main flows (upload, review, chat, approval).
- State management is initialized (e.g., Redux, Zustand, or Context API).
- Basic layout: left pane for PDF/original, right pane for extracted Markdown and chat.
- Dark mode and utility-focused styling are applied.

Technical Details:
- Architecture/Module Changes: Organize components by feature (e.g., /components/ReviewPane, /components/ChatPane).
- Interfaces and Types: Use TypeScript for type safety (examples only).
- Integration Points: Prepare for API calls to backend endpoints.
- Side Effects/Dependencies: None.
- Examples/Conventions: Follow the style guide (dense, dark, minimal, fast feedback).
- Testing: Add a basic test to verify routing and layout render correctly.

