# Membra Vendor Adapters

**Membra Vendor Adapters is the fulfillment adapter namespace for MEMBRA Labs and the MEMBRA Proof Network.**

It provides the abstraction layer between MEMBRA-controlled campaign/proof workflows and external production vendors such as Printful, Printify, Gelato, sticker vendors, sign shops, NFC batch suppliers, and manual local printers.

## Company Context

- Company: **MEMBRA Labs**
- Flagship product: **MEMBRA Proof Network**
- Commercial wedge supported: **Membra Ads**
- Module: **Membra Vendor Adapters**
- Category: fulfillment rails, media-kit ordering, vendor abstraction, production status sync

## One-Line Thesis

Vendor APIs are rails, not the control plane. MEMBRA owns campaign state, proof rules, QR/NFC identity, and payout eligibility.

## Product Role

This repo should support:

- Printful adapter
- Printify adapter
- Gelato adapter
- sticker vendor adapter
- NFC supplier adapter
- local print shop/manual adapter
- vendor order creation
- mockup/file handoff
- kit shipment status
- kit delivery confirmation
- vendor exception handling

## Control-Plane Rule

Owners, advertisers, and dashboards should call MEMBRA APIs only.

Vendor APIs sit behind MEMBRA.

MEMBRA must retain source-of-truth control over:

- campaign approval
- creative approval
- QR/NFC identity
- media-kit state
- proof requirements
- payout eligibility
- audit records

## Suggested Adapter Contract

```json
{
  "vendor": "printful",
  "campaign_id": "camp_123",
  "media_kit_id": "kit_123",
  "asset_type": "shirt",
  "creative_file_url": "https://example.com/file.png",
  "qr_id": "qr_123",
  "nfc_id": null,
  "recipient_profile_id": "owner_123",
  "status": "ready_to_order"
}
```

## Vendor States

- `draft`
- `ready_to_order`
- `ordered`
- `in_production`
- `shipped`
- `delivered`
- `failed`
- `cancelled`
- `manual_review`

## Integration Points

| Repo | Vendor Relationship |
|---|---|
| `overandor/Membra_ads` | requests media-kit generation and vendor order state |
| `overandor/Membra_wear` | defines wearable media catalog and proof requirements |
| `overandor/Membra_admin-` | reviews vendor failures, manual orders, exceptions |
| `overandor/Membra_wallet` | prevents reward release until kit/proof states are valid |
| `overandor/Membra_proofbook` | records kit order/delivery proof hashes |
| `overandor/membra-qr-gateway` | displays kit status and vendor lifecycle |
| `overandor/Membra_kpi` | vendor performance and kit fulfillment metrics |

## Safety Rules

- no vendor order without approved campaign state
- no kit activation without MEMBRA QR/NFC identity
- no payout eligibility from vendor shipment alone; proof review is still required
- no direct frontend-to-vendor API calls
- no committed vendor API keys
- no private customer shipping data in public proof records

## Productization Priority

This repo should be implemented after the proof/media-kit state machine is stable in `Membra_ads`.

Recommended build order:

1. define adapter interface
2. build manual vendor adapter
3. build mock adapter for demos
4. add Printful/Printify/Gelato adapters only after demo flow works
5. add vendor exception handling
6. connect status into Admin, QR Gateway, and KPI

## Current Stage

Fulfillment adapter namespace and vendor-control charter. Not yet a production vendor integration layer.