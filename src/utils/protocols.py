# src/utils/protocols.py

ENGINEERING_PROTOCOLS = """
1. DATA ENCAPSULATION: Functions MUST NOT return storage-specific objects (e.g., sqlite3.Row) or raw indexed tuples. Explicitly map results to structured Python types (Dataclasses or TypedDicts) so attributes are accessed by name (e.g., project.github_url) rather than index. This decouples the business logic from the database schema.
2. DATABASE PATTERNS: Use standard 'sqlite3'. Manage connections and cursors explicitly with standard 'with' blocks. Avoid 'contextlib' decorators unless native context managers are unavailable.
3. ERROR HANDLING: Avoid generic 'except sqlite3.Error' or 'except Exception'. Catch specific errors (e.g., sqlite3.IntegrityError) and raise descriptive, project-specific exceptions.
4. SCHEMA IDEMPOTENCY: Use 'CREATE TABLE IF NOT EXISTS'. Implementation must be idempotent and handle existing data gracefully without using 'health check' functions that parse schema metadata.
5. BEHAVIORAL VERIFICATION: Implementation must be verifiable via state change (INSERT then SELECT) rather than internal metadata inspection. Do not implement internal functions solely for 'schema verification'.
6. RESOURCE HYGIENE: Use context managers for all file, socket, and database operations. Ensure transactional boundaries (commit/rollback) are explicit and follow the resource lifecycle.
7. IMPORT HYGIENE: Absolute imports only: 'from {package_name}.module import ...'. No relative imports or 'sys.path' hacks.
8. TYPE INTEGRITY: Include strict type hints for all function arguments and return types to satisfy Mypy strict mode. No 'Any' types unless strictly necessary.
""".strip()
