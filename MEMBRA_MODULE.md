# MEMBRA Module Contract — Vendor Adapters

## Role

Non-executing vendor package registry for MEMBRA media kits, QR labels, wearable kits, print packages, local shop jobs, and manual fulfillment requests.

## System inputs

- package requests
- subject IDs from KPI, ads, wear, relay, or QR modules
- recipient email
- creative URL
- QR URL
- proof requirements
- operator status updates

## System outputs

- package records
- package status updates
- vendor/manual references
- operator-ready fulfillment queue

## Health

```text
GET /api/health
```

## Replit role

`service`

Runs as a vendor-neutral fulfillment registry behind MEMBRA KPI and the MEMBRA OS workspace.

## Production boundary

This module records package requests. It does not call live vendor APIs by default and does not automatically order goods, ship packages, or spend money.
