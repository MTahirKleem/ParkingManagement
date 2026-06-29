# Phase 9 Next.js Frontend Design

## Scope

Implement only the frontend workflows backed by Phase 7 and Phase 8 APIs: authentication, protected role-aware navigation, operational parking workflows, record details and Admin maintenance, and Admin Guard management.

No analytics, OCR, reports, exports, pricing management, payments beyond cash confirmation, device integrations, tenancy, or invented backend data are included.

## Application Architecture

The Next.js App Router application uses:

```text
pages/components -> React Query hooks -> typed services -> Axios -> FastAPI
```

The root layout installs React Query, auth context, tooltip, and toast providers. Auth context owns the localStorage token, current user, initial `/auth/me` hydration, login/logout, and role redirects. Axios adds the Bearer token and globally handles unauthorized responses.

Dashboard, parking, and users layouts compose `ProtectedLayout`; the users layout additionally requires Admin. Components never call Axios directly.

## Visual System

The interface is a restrained operational dashboard: warm off-white canvas, deep navy navigation, teal action accents, compact borders, and large primary controls on Guard workflows. Geist typography, lucide icons, shadcn primitives, generous spacing, and consistent status badges keep dense tables readable.

Desktop uses a fixed sidebar and content header. Mobile uses a compact header and sheet navigation, stacked filters, horizontally scrollable tables, and full-width operational buttons.

## Authentication and Routing

`parkingmanagement_access_token` is the sole browser token key. On startup, a present token triggers `/auth/me`; failure clears auth and redirects to login. Login stores the token and user, then routes Admin to `/dashboard` and Guard to `/parking/entry`. Root and login routes use the same role-aware redirect rules.

Admin navigation includes Guards. Guard navigation omits it. Direct Guard access to `/users` shows a forbidden state and routes back to an allowed screen.

## Parking Workflows

Vehicle Entry uses React Hook Form and Zod, displays backend errors, resets after success, and links to Active Vehicles.

Active Vehicles supports search, vehicle type, pagination, refresh, details, and explicit cash-confirmed exit. A completed exit displays duration and fee and invalidates active/history/detail queries.

Search accepts all plate formats and optional status. History supports the complete backend filter set. Both use responsive tables with loading, error, empty, and refresh states.

Details display every available record, payment, and pricing-snapshot field. Admin receives edit and soft-delete controls; Guard sees read-only details.

## Guard Management

The Admin-only Guards page lists paginated Guard accounts with search and status filters. Dialog forms create Guards, update only name/phone/status, reset passwords, and confirm soft deletion. Mutations invalidate the users query and never offer Admin creation.

## Error and State Handling

The Axios error helper maps backend codes to the prompt's user-facing messages. Forms show field errors and request errors without leaking credentials. Data pages share skeleton, empty, and retry components. Toasts report successful mutations.

## Verification

Vitest covers formatting/error helpers, API authorization behavior, auth redirects/state, role navigation, and core forms. ESLint, TypeScript, and production build must pass. Browser verification checks responsive login, Admin navigation/workflows, Guard navigation restrictions, parking entry/search/details/exit/history, console errors, and backend integration.
