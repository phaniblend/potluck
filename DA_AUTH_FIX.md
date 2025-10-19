# Delivery Agent Authentication Fix

## Issue
The Delivery Agent dashboard was showing 500 errors for all API endpoints, even though the user was logged in correctly. The HAR logs showed that the Authorization header was being sent, but the backend was still failing.

## Root Cause
The `potluck/backend/routes/delivery.py` file had its **own local `@require_auth` decorator** that was incomplete:
- It checked for the Authorization header
- But it **did NOT extract the `user_id` from the JWT token**
- It **did NOT pass the `user_id` to the decorated functions**

Meanwhile, all the delivery route functions expected `user_id` as their first parameter (e.g., `def available_jobs(user_id)`), causing a mismatch.

## Solution
1. **Removed the local `@require_auth` decorator** from `delivery.py`
2. **Imported the proper `@require_auth`** from `middleware/auth.py` which:
   - Verifies the JWT token using `AuthUtils.verify_token()`
   - Extracts the `user_id` from the token payload
   - Passes `user_id` as the first argument to decorated functions

3. **Updated ALL delivery route functions** to accept `user_id` as their first parameter:
   - `dashboard(user_id)`
   - `service_areas(user_id)`
   - `available_jobs(user_id)` ✅ (already had it)
   - `recent_deliveries(user_id)`
   - `verification_status(user_id)`
   - `submit_verification(user_id)`
   - `update_status(user_id)`

4. **Replaced all hardcoded `user_id = 1`** with the actual `user_id` parameter in SQL queries

## Files Modified
- `potluck/backend/routes/delivery.py`
  - Line 11: Added `from middleware.auth import require_auth`
  - Lines 21-32: Removed local `@require_auth` decorator
  - Updated all route functions to accept and use `user_id`

## Test Status
✅ Backend server restarted successfully
⏳ Ready for user to refresh DA dashboard and test

## Next Steps
1. User should **hard refresh** the DA dashboard (Ctrl+Shift+R)
2. Click **"Refresh"** button in the Available Jobs section
3. The 500 errors should be resolved
4. Available jobs should load (if Tom has added service area 75205)

