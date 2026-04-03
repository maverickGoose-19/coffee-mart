# Supabase Setup

This folder contains a Supabase-ready database setup for the Indian Specialty Coffee Sourcing Platform.

## Files

- `migrations/20260316_initial_schema.sql` creates the core tables and views
- `migrations/20260317_auth_and_live_inquiries.sql` adds auth/session tables and richer inquiry fields
- `migrations/20260318_reviews_and_surveys.sql` adds supplier reviews, buyer reviews, richer interaction types, and buyer recommendation surveys
- `seed.sql` inserts starter buyers, suppliers, lots, inquiries, interactions, and recommendation snapshots
- `.env.example` shows which environment variables the eventual app should use

## How To Apply In Supabase Dashboard

1. Open your project at [app.supabase.com](https://app.supabase.com/).
2. Go to `SQL Editor`.
3. Create a new query.
4. Paste the contents of `migrations/20260316_initial_schema.sql`.
5. Run it.
6. Open another query.
7. Paste the contents of `migrations/20260317_auth_and_live_inquiries.sql`.
8. Run it.
9. Open another query.
10. Paste the contents of `migrations/20260318_reviews_and_surveys.sql`.
11. Run it.
12. Open another query.
13. Paste the contents of `seed.sql`.
14. Run it.
15. Go to `Table Editor` and open the `public` schema.

Tables you should then see:

- `buyers`
- `suppliers`
- `coffee_lots`
- `buyer_inquiries`
- `buyer_lot_interactions`
- `lot_recommendation_snapshots`
- `app_users`
- `app_sessions`
- `supplier_reviews`
- `buyer_reviews`
- `buyer_recommendation_surveys`

Views you should then see:

- `supplier_readiness`
- `recommendation_eligible_lots`
- `supplier_review_summary`
- `buyer_review_summary`

## Where To View Data

- `Table Editor` for row browsing
- `SQL Editor` for custom queries
- `Database` or `API Docs` for schema browsing

Example query:

```sql
select * from public.recommendation_eligible_lots;
```

## Security Note

Do not commit your real Supabase credentials into source files. Keep real values in environment variables or Supabase secrets.
