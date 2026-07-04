# Testing Direction: Real Systems Over Mocks

Use real systems in tests across the repository.

Do not use fake mocks/stubs unless explicitly approved by the Lead Developer/Programmer.

When an exception is approved, include a short note in the test explaining why real-system coverage is not feasible.

Examples where an approved exception may be acceptable:
- External systems that are unavailable in CI.
- Nondeterministic behavior that cannot be stabilized with normal test controls.
- Extremely slow or high-cost dependencies that would make CI impractical.
