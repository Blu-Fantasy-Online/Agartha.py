# Products and earnings

Approved developers can prepare app subscriptions in the developer panel. Selling and cashout require monetization approval, a verified beneficiary, and active platform payment configuration. Drafting a product does not charge customers.

## Prepare a paid application

1. Select the developer team that owns the app.
2. Open **Monetization** and complete the team's beneficiary onboarding through BFO's Stripe Connect flow.
3. Submit the requested monetization and beneficiary review information.
4. Prepare the app's product, price, and user/server subscription scope.
5. Publish only when review and payment activation permit it.

Finance actions require the relevant team authority and current two-factor verification. A monetized team ownership change requires staff review. Check the panel's current status; enabled SDK code does not activate payments.

## Read entitlements with Agartha.py

An entitlement states which current subscription benefit the application may provide. Read it through the authenticated Client:

```python
async def read_entitlements(client):
    result = await client.request("GET", "/applications/@me/entitlements")
    if not isinstance(result, list):
        raise ValueError("Expected an entitlement list.")
    return result
```

Each entry includes `id`, `product_id`, `user_id`, optional `server_id`, `status`, and `current_period_end`.

```json
{
  "id": "100000000000000401",
  "product_id": "100000000000000402",
  "user_id": "100000000000000039",
  "server_id": "100000000000000088",
  "status": "active",
  "current_period_end": "2026-11-08T12:00:00Z"
}
```

Match the intended product and user/server scope, require the entitlement's authorized current status, and check its expiry before granting a paid feature. A successful checkout redirect alone is not an entitlement. Cancellation, refund, dispute, access loss, or expiry can affect current availability; refresh entitlement data when deciding access.

Product configuration, checkout, billing portal, and payout requests are panel workflows. Agartha.py does not expose helpers that create products, charge buyers, or transfer funds.

## Buyer subscriptions

Buyers can subscribe for their own account or an installed server they can manage. They can view subscriptions and open the scoped billing portal at [My app subscriptions](https://blufantasy.online/agartha/developers/subscriptions). Developer membership is not required to manage a purchased subscription.

A server subscription stays scoped to that server. Deleting a server does not convert it into a personal subscription.

## Platform fee

The team's growth rate is **5%** until its verified lifetime gross sales across all bots reach **USD $1,000,000**. At that threshold, the approved standard rate applies, up to **15%**; the default standard rate is 15%.

The sale that crosses the threshold uses the rate that applied before that sale. Subsequent verified sales use the standard rate. Refunds do not reset lifetime gross. Renewals are evaluated at their verified receipt time. Each receipt retains the fee applied to that sale. Stripe processing fees are recorded separately and absorbed by the platform.

## Combined team cashout

Cashout combines available earnings from **all bots owned by the selected developer team**. The minimum available total is **USD $20**, after the seven-day hold and applicable refund/dispute adjustments.

Separate teams have separate beneficiaries and balances. The eligible owner requests cashout through the panel. Concurrent requests cannot reserve the same earnings twice; transfer status can remain pending while provider acknowledgement or reconciliation completes. Refunds and disputes can reduce available earnings or reverse a transfer.

The panel provides the current gross sales, platform commission, adjustments, available balance, and payout status. Never treat an indicative checkout estimate as a finalized earnings receipt.
