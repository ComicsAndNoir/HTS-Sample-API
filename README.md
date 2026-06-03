# HTS API Marketplace — Mock API (v1 wedge prototype)

A scrappy, **queryable** mock of the first sellable slice of the HTS API
Marketplace. It is intentionally narrow: lodging connectivity (HTS Connect) with
content, ranking, pricing, and taxes on top — the capabilities I'd argue are
commercially-ready enough to be the v1 wedge. The point isn't completeness; it's
to put a concrete integration surface in front of partners and capability PMs to
surface hidden requirements before we write a line of production code.

The distinctive bit: every response carries a `_marketplace` block exposing the
partner's commercial tier, take rate, and which capabilities were invoked — so
the commercial model is visible in the API itself, not buried in a pricing deck.

## Run it

```bash
pip install fastapi uvicorn          # add --break-system-packages on some systems
uvicorn main:app --reload --port 8000
```

Then **query from the spec interactively** at:

- Swagger UI (click "Try it out" on any endpoint): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Raw OpenAPI spec: http://127.0.0.1:8000/openapi.json  (also exported as `openapi.json`)

> Running this inside Claude Code: point it at this folder and ask it to start
> the server, then iterate on endpoints or data live — adding a capability is a
> few lines in `main.py` + `data.py`.

## Auth (mock)

Send a partner key as a bearer token. The key sets the commercial tier + take rate:

| Partner key          | Partner               | Tier       | Take rate |
|----------------------|-----------------------|------------|-----------|
| `hts_demo_ent_001`   | Capital One Travel    | enterprise | 4.0%      |
| `hts_demo_std_002`   | Acme Travel           | standard   | 7.0%      |

## Example queries (curl)

```bash
# Search Lisbon (ranked "recommended")
curl -s -X POST http://127.0.0.1:8000/v1/lodging/search \
  -H "Authorization: Bearer hts_demo_ent_001" -H "Content-Type: application/json" \
  -d '{"destination":"Lisbon","check_in":"2026-09-12","check_out":"2026-09-15","sort":"recommended"}'

# Property content
curl -s http://127.0.0.1:8000/v1/lodging/properties/hts_lis_4412 \
  -H "Authorization: Bearer hts_demo_ent_001"

# Itemized quote — supplier net, taxes, marketplace take, sell price
curl -s -X POST http://127.0.0.1:8000/v1/lodging/quote \
  -H "Authorization: Bearer hts_demo_ent_001" -H "Content-Type: application/json" \
  -d '{"property_id":"hts_lis_4412","rate_id":"r_4412_a","check_in":"2026-09-12","check_out":"2026-09-15"}'
```

Swap the bearer token to `hts_demo_std_002` on the quote call to watch the take
rate (and sell price) change — the same booking returns a different marketplace
take for an enterprise vs. self-serve partner.

## Endpoints

| Method | Path                                   | Capabilities surfaced                 |
|--------|----------------------------------------|---------------------------------------|
| GET    | `/v1/health`                           | —                                     |
| POST   | `/v1/lodging/search`                   | HTS Connect, Ranking, Pricing         |
| GET    | `/v1/lodging/properties/{property_id}` | Content & Property Mapping            |
| POST   | `/v1/lodging/quote`                    | Pricing, Taxes (+ marketplace take)   |

## What this is NOT

Not production code, not real supply, no persistence, no real auth. Deliberately
so — it's a conversation prop for week 3–4 of the plan, not an engineering
deliverable.
