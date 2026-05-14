# MEMBRA Protocol

Membra_api is the system of record.

This repo follows the shared Membra protocol for vendor fulfillment adapters, media kit ordering, shipment status, vendor webhooks, and manual fulfillment workflows.

Core rule: vendors manufacture or ship media kits; they do not decide campaign truth, proof approval, or payout release.

Shared IDs: own_, adv_, ast_, cmp_, crt_, plc_, kit_, qr_, nfc_, proof_, aud_.

Fulfillment states used here: planned, generated, ordered, in_production, shipped, delivered, confirmed_received, lost, damaged.

Vendor events must report back to Membra_api and should be audit-linked.
