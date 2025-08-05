# Admin Analytics Dashboard: Basic Usage Metrics

Provide an admin-only dashboard or endpoint to view basic usage metrics: PDFs processed, approval/rejection rates, chat frequency.

Goals:
- Allow admins to monitor tool usage and key metrics.

Acceptance Criteria:
- Admins can view: total PDFs processed, approval/rejection rates, chat interaction counts.
- Metrics are accurate and updated in near real-time.
- Access is restricted to admin users.

Technical Details:
- Architecture/Module Changes: Add admin dashboard UI or analytics API endpoint.
- Interfaces and Types: Define metrics response types; ensure admin authentication/authorization.
- Integration Points: Aggregate data from analytics event logs.
- Database/Schema Changes: None if using event logs; otherwise, add summary tables as needed.
- Side Effects/Dependencies: None beyond admin access control.
- Examples/Conventions: Follow admin UI/API conventions.
- Testing: Add tests for metrics accuracy, access control, and error handling.
