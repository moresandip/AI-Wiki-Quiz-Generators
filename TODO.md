# TODO: Fix SQLite Database Issue for Vercel Deployment

## Approved Plan
- Switch to Supabase (free PostgreSQL database that works with Vercel).
- Update DATABASE_URL to use Supabase connection string.
- Models already support PostgreSQL.
- Add setup instructions for Supabase.

## Steps to Complete
- [x] Update backend/database.py to use PostgreSQL as default (with fallback to SQLite for local dev)
- [x] Update API_KEY_SETUP.md with Supabase setup instructions
- [ ] Test local setup with PostgreSQL
- [ ] Deploy and test on Vercel with Supabase DATABASE_URL

## Followup Steps (After Implementation)
- Set up Supabase account and project
- Get connection string and set as DATABASE_URL in Vercel environment variables
- Test deployment
