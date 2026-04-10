# Leadership Module - Ranked War Payout Calculator

## Overview

The Ranked War Payout Calculator is exposed through the `/api/payouts/*` endpoints and the frontend page at `/payouts`.

This implementation is fully automated from stored Ranked War logs:

- Leaders only provide `war_id`, `total_pool`, `faction_cut`, and `payout_mode`
- Member hits/respect are aggregated server-side from `torn.WarLog`
- Payout history is persisted in dedicated payout models

## Backend Components

### Service Layer

- `leadership/services/payout_service.py`
  - `generate_rw_payout(war_id, total_pool, faction_cut, payout_mode, created_by)`
  - `RankedWarPayoutService.get_war_contributions(war_id)`
  - `RankedWarPayoutService.list_ranked_wars()`

### Models

- `leadership.RankedWarPayout`
  - `war_id`, `total_pool`, `faction_cut`, `payout_mode`, `distributable_pool`, `created_by`, `created_at`
- `leadership.RankedWarPayoutMember`
  - `payout`, `member`, `total_hits`, `total_respect`, `contribution_percentage`, `payout_amount`
- `torn.WarLog`
  - Added `war_id` for war-scoped aggregation

### API Endpoints

- `POST /api/payouts/calculate`
- `GET /api/payouts/history`
- `GET /api/payouts/{id}`
- `GET /api/payouts/war-contributions/{war_id}`
- `GET /api/payouts/wars`

## Calculation

- `distributable_pool = total_pool - (total_pool * faction_cut / 100)`
- Hits mode:
  - `share = member_hits / total_hits`
- Respect mode:
  - `share = member_respect / total_respect`
- `member_payout = distributable_pool * share`

All percentages and payouts are rounded to 2 decimal places using `ROUND_HALF_UP`.

## Frontend

Route: `/payouts`

Features:

- Ranked War selector with active/previous options
- Manual war ID search
- Total pool input
- Faction cut input
- Payout mode radio selection (hits/respect)
- Generate payout button
- Sortable payout table (payout/hits/respect)
- CSV export (`member_name,hits,respect,share,payout`)
- Validation and error states

## Tests

### Backend

`python manage.py test leadership`

Covers:

- Payout by hits
- Payout by respect
- Faction cut calculation
- War aggregation logic
- API response structure

### Frontend

`npx jest src/app/payouts/__tests__/page.test.tsx --runInBand`

Covers:

- Rendering required payout UI controls
- CSV export workflow
