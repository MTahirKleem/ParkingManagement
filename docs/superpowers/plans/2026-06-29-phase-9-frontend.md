# Phase 9 Next.js Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete responsive Phase 9 frontend against the existing authentication, users, and parking APIs.

**Architecture:** Use App Router layouts and focused UI components over React Query hooks, typed service modules, and one Axios client. Auth context owns local token/user lifecycle while protected layouts and role guards control access.

**Tech Stack:** Next.js, TypeScript, Tailwind CSS, shadcn/ui, React Query, Axios, React Hook Form, Zod, Vitest

---

### Task 1: Scaffold and Frontend Foundations

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/globals.css`
- Create: `frontend/components.json`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/tests/setup.ts`
- Create: `frontend/.env.local`

- [ ] Scaffold the requested TypeScript/Tailwind/App Router project and install runtime plus test dependencies.
- [ ] Initialize shadcn and add the prompt's primitives plus sheet, tooltip, sonner, and alert-dialog.
- [ ] Add a failing utility smoke test and run `npm test -- --run`; expect missing application helpers.
- [ ] Configure Vitest/jsdom and the root visual tokens, then make the smoke test pass.

### Task 2: Types, Axios, Services, and Query Hooks

**Files:**
- Create: `frontend/types/api.ts`
- Create: `frontend/types/auth.ts`
- Create: `frontend/types/parking.ts`
- Create: `frontend/types/user.ts`
- Create: `frontend/lib/api.ts`
- Create: `frontend/lib/auth.ts`
- Create: `frontend/lib/query-client.tsx`
- Create: `frontend/services/auth.service.ts`
- Create: `frontend/services/parking.service.ts`
- Create: `frontend/services/users.service.ts`
- Create: `frontend/hooks/useParking.ts`
- Create: `frontend/hooks/useUsers.ts`

- [ ] Write failing tests for token helpers, friendly backend errors, Axios authorization/401 behavior, and service paths.
- [ ] Run the focused tests and confirm expected failures.
- [ ] Implement exact API types, localStorage token utilities, Axios interceptors, service methods, query keys, queries, mutations, and invalidations.
- [ ] Re-run focused tests and confirm they pass.

### Task 3: Auth Context, Login, and Protected Shell

**Files:**
- Create: `frontend/lib/auth-context.tsx`
- Create: `frontend/hooks/useAuth.ts`
- Create: `frontend/components/auth/LoginForm.tsx`
- Create: `frontend/components/layout/AppSidebar.tsx`
- Create: `frontend/components/layout/AppHeader.tsx`
- Create: `frontend/components/layout/ProtectedLayout.tsx`
- Create: `frontend/components/layout/RoleGuard.tsx`
- Create: `frontend/app/login/page.tsx`
- Create: `frontend/app/page.tsx`

- [ ] Write failing component tests for login validation, role redirects, protected loading, logout, and the missing Guard Users link.
- [ ] Run focused tests and confirm failures.
- [ ] Implement auth hydration/login/logout, protected/role states, responsive navigation, and login/root behavior.
- [ ] Re-run focused tests and confirm they pass.

### Task 4: Common UI and Dashboard

**Files:**
- Create: `frontend/components/common/PageHeader.tsx`
- Create: `frontend/components/common/LoadingState.tsx`
- Create: `frontend/components/common/EmptyState.tsx`
- Create: `frontend/components/common/ErrorState.tsx`
- Create: `frontend/app/dashboard/layout.tsx`
- Create: `frontend/app/dashboard/page.tsx`
- Create: `frontend/app/parking/layout.tsx`
- Create: `frontend/app/users/layout.tsx`

- [ ] Write a failing dashboard test proving role-specific quick actions and absence of fake analytics.
- [ ] Implement shared page states and role-aware quick-action dashboards within protected layouts.
- [ ] Run the focused test and confirm it passes.

### Task 5: Parking Entry, Active, Search, and Exit

**Files:**
- Create: `frontend/components/parking/VehicleEntryForm.tsx`
- Create: `frontend/components/parking/ActiveVehiclesTable.tsx`
- Create: `frontend/components/parking/ParkingSearchForm.tsx`
- Create: `frontend/components/parking/CompleteExitDialog.tsx`
- Create: `frontend/app/parking/entry/page.tsx`
- Create: `frontend/app/parking/active/page.tsx`
- Create: `frontend/app/parking/search/page.tsx`

- [ ] Write failing tests for entry validation/reset, duplicate messaging, search formats, cash confirmation, and exit result display.
- [ ] Implement forms, filters, pagination, tables, details links, cash-confirmed exit, invalidations, and shared states.
- [ ] Run focused tests and confirm they pass.

### Task 6: History, Details, and Admin Parking Actions

**Files:**
- Create: `frontend/components/parking/ParkingHistoryTable.tsx`
- Create: `frontend/components/parking/ParkingRecordDetails.tsx`
- Create: `frontend/app/parking/history/page.tsx`
- Create: `frontend/app/parking/[id]/page.tsx`

- [ ] Write failing tests for history filters, full record rendering, Admin-only controls, edit fields, delete confirmation, and post-delete routing.
- [ ] Implement history and detail queries, complete field display, Admin edit dialog, and soft-delete confirmation.
- [ ] Run focused tests and confirm they pass.

### Task 7: Admin Guard Management

**Files:**
- Create: `frontend/components/users/GuardForm.tsx`
- Create: `frontend/components/users/GuardsTable.tsx`
- Create: `frontend/components/users/ResetPasswordDialog.tsx`
- Create: `frontend/app/users/page.tsx`

- [ ] Write failing tests for fixed Guard role, password validation, update-field restrictions, reset password, filters, pagination, and deletion confirmation.
- [ ] Implement the complete Admin-only Guard management UI and query invalidation.
- [ ] Run focused tests and confirm they pass.

### Task 8: Quality and Browser Verification

**Files:**
- Modify only files identified by verification failures.

- [ ] Run `npm test -- --run`, `npm run lint`, `npx tsc --noEmit`, and `npm run build`; require clean output.
- [ ] Start the backend and frontend development servers.
- [ ] Verify login, redirects, responsive shell, Admin Guard CRUD, Guard navigation, entry, duplicate handling, active/search/detail/exit/history, Admin parking edit/delete, and forbidden behavior in a real browser.
- [ ] Check browser console/network failures and correct regressions with failing tests first.
