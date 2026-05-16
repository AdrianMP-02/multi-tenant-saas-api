# Billing API

Base path: `/api/v1/tenants/{tenant_id}/billing`

Billing endpoints manage subscriptions and invoices. All endpoints require authentication and tenant membership.

**Note:** Stripe payment processing is marked as pending. Subscribe and cancel endpoints return informational messages. The data model (Subscription, Invoice) is ready for integration.

## POST /subscribe

Subscribe a tenant to a plan. Creates or updates the tenant's subscription.

**Authorization:** Requires `owner` or `admin` role.

### Request

```
POST /api/v1/tenants/{tenant_id}/billing/subscribe?plan_id={plan_id}
Authorization: Bearer <access_token>
```

| Query param | Type | Description |
|---|---|---|
| `plan_id` | UUID | ID of the plan to subscribe to |

### Response 200

```json
{
  "message": "Subscription created (Stripe integration pending)"
}
```

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | Insufficient role — requires `owner` or `admin` |
| `404 Not Found` | `Tenant not found` or `Plan not found` |
| `400 Bad Request` | `Plan is not active` |

---

## POST /cancel

Cancel the tenant's current subscription. The tenant may revert to a free/trial status.

**Authorization:** Requires `owner` or `admin` role.

### Request

```
POST /api/v1/tenants/{tenant_id}/billing/cancel
Authorization: Bearer <access_token>
```

### Response 200

```json
{
  "message": "Subscription canceled (Stripe integration pending)"
}
```

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | Insufficient role |

---

## GET /invoices

List invoices for a tenant.

### Request

```
GET /api/v1/tenants/{tenant_id}/billing/invoices
Authorization: Bearer <access_token>
```

### Response 200

```json
[]
```

Currently returns an empty list (Stripe integration pending).

### Errors

| Status | Description |
|---|---|
| `403 Forbidden` | `You are not a member of this tenant` |
