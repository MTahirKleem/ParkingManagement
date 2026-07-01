# Parking User Names Design

## Goal

Display human-readable user names instead of MongoDB user IDs for the `Created by`, `Completed by`, and payment `Received by` fields in parking record details for both Admin and Guard.

## API Design

Parking responses retain their existing ID fields for audit compatibility and add nullable `created_by_name`, `completed_by_name`, and `payment.received_by_name` fields. `ParkingService` resolves all referenced users in one batched users query per response operation. Missing or deleted users do not break parking retrieval; their name field is null and the frontend falls back to the existing ID.

This avoids exposing the Admin-only Users API to Guard, avoids client-side N+1 requests, supports historical records, and remains backward compatible.

## Frontend Design

The parking types model the optional name fields. The details page displays each resolved name and uses the corresponding ID only when no name is available. Name values use normal text styling rather than identifier monospace styling.

## Verification

Backend tests cover batch name lookup, response enrichment, missing users, and the response schema. Frontend tests cover name preference and ID fallback. The complete backend and frontend test, type, lint, and build checks must pass.
