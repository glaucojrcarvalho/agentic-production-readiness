# Case 11 Contract

`handle_webhook` is a small replay-safe ingestion boundary.

Supported contract:

- `event_id` must be a non-empty string;
- the first delivery for an event ID stores and returns its result;
- later deliveries with the same event ID return the stored result;
- if two deliveries race to save the same event ID, the loser may recover by reading the winner's stored result;
- payload equality across replays is not part of this case's contract;
- persistence durability across process restarts is outside this in-memory fixture's scope.

Review the implementation against this bounded contract rather than inventing requirements outside it.
