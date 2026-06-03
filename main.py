"""
HTS API Marketplace — mock API (v1 wedge prototype)

Purpose
-------
A scrappy, queryable mock of the first sellable slice of the HTS API
Marketplace: lodging connectivity (HTS Connect) with content, ranking, pricing,
and taxes layered on, and the *marketplace commercial model* surfaced directly
in every response via a `_marketplace` metadata block.

This is a prototype to surface hidden requirements with partners and capability
PMs — not production code. Responses are deterministic mock data.

Run
---
    uvicorn main:app --reload --port 8000

Then open http://127.0.0.1:8000/docs to query it interactively, or hit the
endpoints with curl (see README.md).

Auth
----
Send a partner key as a bearer token:  Authorization: Bearer hts_demo_ent_001
The key determines the partner's commercial tier and take rate.
"""
from datetime import date
from typing import Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from data import CAR_RENTALS, HOPPER_PRODUCTS, PARTNERS, PROPERTIES, TAX_RULES

app = FastAPI(
    title="HTS API Marketplace",
    version="0.1.0-wedge",
    description=(
        "Mock of the HTS API Marketplace v1 wedge: lodging connectivity "
        "(HTS Connect) + content, ranking, pricing, and taxes. Every response "
        "includes a `_marketplace` block showing which capabilities were "
        "invoked and the partner's take rate — making the commercial model "
        "visible in the API surface."
    ),
)


# --- Auth / partner resolution ------------------------------------------------
def get_partner(authorization: Optional[str] = Header(default=None)):
    """Resolve the partner from the bearer token and attach their commercial terms."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing 'Authorization: Bearer <partner_key>' header.")
    key = authorization.split(" ", 1)[1].strip()
    partner = PARTNERS.get(key)
    if not partner:
        raise HTTPException(403, f"Unknown partner key. Try: {', '.join(PARTNERS)}")
    return {"key": key, **partner}


_HOPPER_UPLIFT = {
    "cfar": 0.09, "lfar": 0.06, "price_freeze": 0.07, "price_drop": 0.11, "price_freeze_cars": 0.05,
}


def marketplace_block(partner: dict, capabilities: list[str],
                      hopper_products: Optional[list[str]] = None) -> dict:
    """The reusable commercial-model metadata attached to every response."""
    block: dict = {
        "partner": partner["partner_name"],
        "tier": partner["tier"],
        "commercial_model": partner["model"],
        "take_rate": partner["take_rate"],
        "capabilities_invoked": capabilities,
    }
    if hopper_products:
        uplift = sum(_HOPPER_UPLIFT.get(p, 0) for p in hopper_products)
        block["estimated_conversion_uplift"] = f"+{round(uplift * 100)}%"
    return block


# --- Schemas ------------------------------------------------------------------
class SearchRequest(BaseModel):
    destination: str = Field(..., examples=["Lisbon"])
    check_in: date = Field(..., examples=["2026-09-12"])
    check_out: date = Field(..., examples=["2026-09-15"])
    guests: int = Field(2, ge=1, le=8)
    sort: Literal["recommended", "price_asc", "rating_desc"] = "recommended"


class QuoteRequest(BaseModel):
    property_id: str = Field(..., examples=["hts_lis_4412"])
    rate_id: str = Field(..., examples=["r_4412_a"])
    check_in: date = Field(..., examples=["2026-09-12"])
    check_out: date = Field(..., examples=["2026-09-15"])
    hopper_products: list[str] = Field(
        default=[],
        examples=[["cfar"]],
        description="Optional Hopper fintech product IDs to add to this quote.",
    )


class CarSearchRequest(BaseModel):
    destination: str = Field(..., examples=["Lisbon"])
    pickup_location: Literal["airport", "city"] = Field("airport", examples=["airport"])
    pickup_date: date = Field(..., examples=["2026-09-12"])
    dropoff_date: date = Field(..., examples=["2026-09-15"])


class CarQuoteRequest(BaseModel):
    car_id: str = Field(..., examples=["car_lis_001"])
    pickup_location: Literal["airport", "city"] = Field(..., examples=["airport"])
    pickup_date: date = Field(..., examples=["2026-09-12"])
    dropoff_date: date = Field(..., examples=["2026-09-15"])
    hopper_products: list[str] = Field(
        default=[],
        examples=[["cfar"]],
        description="Optional Hopper fintech product IDs. Only products that apply to 'cars' are accepted.",
    )


class BundleQuoteRequest(BaseModel):
    property_id: str = Field(..., examples=["hts_lis_4412"])
    rate_id: str = Field(..., examples=["r_4412_a"])
    car_id: str = Field(..., examples=["car_lis_001"])
    pickup_location: Literal["airport", "city"] = Field(..., examples=["airport"])
    check_in: date = Field(..., examples=["2026-09-12"])
    check_out: date = Field(..., examples=["2026-09-15"])
    hopper_products: list[str] = Field(
        default=[],
        examples=[["cfar"]],
        description="Optional Hopper fintech product IDs. Only products that apply to 'bundle' are accepted.",
    )


# --- Routes -------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    return FileResponse("index.html")


@app.get("/v1/health", tags=["meta"])
def health():
    return {"status": "ok", "service": "hts-marketplace-mock", "version": app.version}


@app.get("/v1/partners", tags=["meta"])
def list_partners():
    """List all demo partner keys with their tier, commercial terms, and display metadata."""
    return {
        "partners": [
            {
                "key":         key,
                "name":        p["partner_name"],
                "tier":        p["tier"],
                "take_rate":   p["take_rate"],
                "model":       p["model"],
                "description": p["description"],
            }
            for key, p in PARTNERS.items()
        ]
    }


@app.get("/v1/products", tags=["products"])
def list_products():
    """List available Hopper fintech products that can be added to a lodging quote."""
    return {
        "products": [
            {
                "product_id": pid,
                "name": p["name"],
                "tagline": p["tagline"],
                "description": p["description"],
                "fee_type": p["fee_type"],
                "fee_value": p["fee_value"],
                "applies_to": p["applies_to"],
            }
            for pid, p in HOPPER_PRODUCTS.items()
        ]
    }


# --- Helpers ------------------------------------------------------------------
def _find_car(car_id: str) -> tuple[Optional[dict], Optional[dict]]:
    """Return (city_entry, car) for a given car_id, or (None, None)."""
    for city_entry in CAR_RENTALS.values():
        for car in city_entry["cars"]:
            if car["car_id"] == car_id:
                return city_entry, car
    return None, None


def _hopper_line_items(net: float, product_ids: list[str], context: str,
                       fee_overrides: Optional[dict] = None,
                       days: int = 1) -> tuple[dict, float]:
    """Compute Hopper fee line items.

    fee_overrides: {pid: rate_value} replaces the product's default fee_value.
    days: used for flat_per_day products (car RDW).
    """
    fee_overrides = fee_overrides or {}
    line_items: dict = {}
    total = 0.0
    for pid in product_ids:
        prod = HOPPER_PRODUCTS[pid]
        fee_value = fee_overrides.get(pid, prod["fee_value"])
        if prod["fee_type"] == "pct_of_net":
            fee = round(net * fee_value, 2)
        elif prod["fee_type"] == "flat_per_day":
            fee = round(fee_value * days, 2)
        else:  # flat
            fee = fee_value
        item: dict = {"name": prod["name"], "fee": fee}
        if pid in fee_overrides:
            item["note"] = "Non-refundable rate — higher risk premium applied"
        line_items[pid] = item
        total += fee
    return line_items, round(total, 2)


def _price_signal(property_id: str, nightly_rate: float) -> dict:
    """Deterministic mock Hopper price-prediction signal keyed to property_id."""
    h = sum(ord(c) for c in property_id)
    trends = ["rising", "rising", "stable", "volatile", "falling"]
    trend = trends[h % 5]
    confidence = round(0.72 + (h % 17) * 0.015, 2)
    pct = (h % 14) + 4

    if trend in ("rising", "volatile"):
        predicted_low = round(nightly_rate * (0.83 + (h % 10) * 0.01), 2)
        recommendation = "buy_now"
    elif trend == "falling":
        predicted_low = round(nightly_rate * (0.91 + (h % 6) * 0.01), 2)
        recommendation = "wait"
    else:
        predicted_low = round(nightly_rate * (0.94 + (h % 5) * 0.01), 2)
        recommendation = "buy_now"

    insights = {
        "rising":   f"Prices up {pct}% over the past 14 days — trend likely to continue.",
        "stable":   "Prices have been steady. Safe to book; no meaningful discount expected.",
        "volatile": "High volatility detected. Rate spikes are common — lock in now.",
        "falling":  f"Prices down {pct // 2}% recently. May fall further before levelling.",
    }
    return {
        "trend": trend,
        "recommendation": recommendation,
        "confidence": confidence,
        "predicted_low": predicted_low,
        "insight": insights[trend],
    }


@app.post("/v1/lodging/search", tags=["lodging"])
def search(req: SearchRequest, partner: dict = Depends(get_partner)):
    """
    HTS Connect lodging search + Ranking.

    Returns available properties for a destination with a lead rate each.
    `sort=recommended` uses a mock ranking score blending review score and the
    marketplace margin signal — a stand-in for the Ranking capability.
    """
    nights = (req.check_out - req.check_in).days
    if nights < 1:
        raise HTTPException(422, "check_out must be after check_in.")

    matches = [p for p in PROPERTIES if p["destination"].lower() == req.destination.lower()]
    if not matches:
        return {"results": [], "_marketplace": marketplace_block(partner, ["hts_connect"])}

    results = []
    for p in matches:
        lead = min(p["rates"], key=lambda r: r["supplier_net"])
        margin_signal = lead["supplier_net"] * partner["take_rate"]
        # mock ranking score: review weight + normalized margin signal
        rank_score = round(p["review_score"] * 10 + margin_signal * 0.15, 2)
        results.append({
            "property_id": p["property_id"],
            "name": p["name"],
            "star_rating": p["star_rating"],
            "review_score": p["review_score"],
            "lead_rate": {
                "rate_id": lead["rate_id"],
                "room_name": lead["room_name"],
                "board": lead["board"],
                "nightly_from": lead["supplier_net"],
                "currency": lead["currency"],
                "refundable": lead["refundable"],
            },
            "rank_score": rank_score,
            "_hopper_intelligence": _price_signal(p["property_id"], lead["supplier_net"]),
        })

    if req.sort == "price_asc":
        results.sort(key=lambda r: r["lead_rate"]["nightly_from"])
    elif req.sort == "rating_desc":
        results.sort(key=lambda r: r["review_score"], reverse=True)
    else:  # recommended
        results.sort(key=lambda r: r["rank_score"], reverse=True)

    return {
        "query": {"destination": req.destination, "nights": nights, "guests": req.guests, "sort": req.sort},
        "result_count": len(results),
        "results": results,
        "_marketplace": marketplace_block(partner, ["hts_connect", "ranking", "pricing"]),
    }


@app.get("/v1/lodging/properties", tags=["lodging"])
def list_properties(partner: dict = Depends(get_partner)):
    """List all available properties with their rates — used to populate partner UIs."""
    items = [
        {
            "property_id": p["property_id"],
            "name": p["name"],
            "destination": p["destination"],
            "star_rating": p["star_rating"],
            "rates": [
                {"rate_id": r["rate_id"], "room_name": r["room_name"],
                 "board": r["board"], "supplier_net": r["supplier_net"], "currency": r["currency"]}
                for r in p["rates"]
            ],
        }
        for p in PROPERTIES
    ]
    return {
        "properties": items,
        "_marketplace": marketplace_block(partner, ["content_property_mapping"]),
    }


@app.get("/v1/lodging/properties/{property_id}", tags=["lodging"])
def property_content(property_id: str, partner: dict = Depends(get_partner)):
    """Content & Property Mapping — full content payload for a single property."""
    p = next((x for x in PROPERTIES if x["property_id"] == property_id), None)
    if not p:
        raise HTTPException(404, f"Unknown property_id '{property_id}'.")
    return {
        "property_id": p["property_id"],
        "name": p["name"],
        "destination": p["destination"],
        "country": p["country"],
        "star_rating": p["star_rating"],
        "review_score": p["review_score"],
        "location": {"lat": p["lat"], "lng": p["lng"]},
        "content": p["content"],
        "rates": p["rates"],
        "_marketplace": marketplace_block(partner, ["content_property_mapping"]),
    }


@app.post("/v1/lodging/quote", tags=["lodging"])
def quote(req: QuoteRequest, partner: dict = Depends(get_partner)):
    """
    Pricing + Taxes + the marketplace take rate, fully itemized.

    This is where the commercial model becomes concrete: supplier net, taxes,
    the partner's take rate on GBV, and the resulting sell price.
    """
    p = next((x for x in PROPERTIES if x["property_id"] == req.property_id), None)
    if not p:
        raise HTTPException(404, f"Unknown property_id '{req.property_id}'.")
    rate = next((r for r in p["rates"] if r["rate_id"] == req.rate_id), None)
    if not rate:
        raise HTTPException(404, f"Unknown rate_id '{req.rate_id}' for this property.")

    nights = (req.check_out - req.check_in).days
    if nights < 1:
        raise HTTPException(422, "check_out must be after check_in.")

    invalid = [pid for pid in req.hopper_products if pid not in HOPPER_PRODUCTS]
    if invalid:
        raise HTTPException(400, f"Unknown Hopper product(s): {', '.join(invalid)}")

    tax = TAX_RULES.get(p["country"], {"vat_pct": 0.0, "city_tax_per_night": 0.0})
    net = round(rate["supplier_net"] * nights, 2)
    vat = round(net * tax["vat_pct"], 2)
    city_tax = round(tax["city_tax_per_night"] * nights, 2)
    take = round(net * partner["take_rate"], 2)

    # CFAR carries higher risk on non-refundable rates — premium bumped from 8% → 12%
    cfar_overrides = {}
    if "cfar" in req.hopper_products and not rate["refundable"]:
        cfar_overrides["cfar"] = 0.12

    hopper_items, hopper_total = _hopper_line_items(net, req.hopper_products, "lodging", cfar_overrides)
    sell_price = round(net + vat + city_tax + hopper_total, 2)

    return {
        "property_id": p["property_id"],
        "rate_id": rate["rate_id"],
        "room_name": rate["room_name"],
        "nights": nights,
        "currency": rate["currency"],
        "price_breakdown": {
            "supplier_net": net,
            "vat": vat,
            "city_tax": city_tax,
            "marketplace_take": take,
            "hopper_products": hopper_items,
            "hopper_total": hopper_total,
            "sell_price": sell_price,
        },
        "_marketplace": marketplace_block(partner, ["pricing", "taxes"], req.hopper_products),
    }


@app.get("/v1/cars", tags=["cars"])
def list_cars(partner: dict = Depends(get_partner)):
    """List all car rentals by destination with rates for both pickup locations."""
    return {
        "cars_by_destination": {
            destination: [
                {
                    "car_id": car["car_id"],
                    "supplier": car["supplier"],
                    "category": car["category"],
                    "model": car["model"],
                    "seats": car["seats"],
                    "bags": car["bags"],
                    "transmission": car["transmission"],
                    "rates": car["rates"],
                }
                for car in city_entry["cars"]
            ]
            for destination, city_entry in CAR_RENTALS.items()
        },
        "_marketplace": marketplace_block(partner, ["content_property_mapping"]),
    }


@app.post("/v1/cars/search", tags=["cars"])
def car_search(req: CarSearchRequest, partner: dict = Depends(get_partner)):
    """
    Search available car rentals for a destination.

    Returns all cars for the destination with the rate for the requested
    pickup_location (airport vs city centre).
    """
    days = (req.dropoff_date - req.pickup_date).days
    if days < 1:
        raise HTTPException(422, "dropoff_date must be after pickup_date.")

    city_entry = CAR_RENTALS.get(req.destination)
    if not city_entry:
        available = ", ".join(CAR_RENTALS)
        raise HTTPException(404, f"No cars for '{req.destination}'. Available: {available}")

    results = []
    for car in city_entry["cars"]:
        rate_info = car["rates"][req.pickup_location]
        results.append({
            "car_id": car["car_id"],
            "supplier": car["supplier"],
            "category": car["category"],
            "model": car["model"],
            "seats": car["seats"],
            "bags": car["bags"],
            "transmission": car["transmission"],
            "pickup_location": req.pickup_location,
            "location_name": rate_info["location_name"],
            "rate_per_day": rate_info["rate_per_day"],
            "total_for_days": round(rate_info["rate_per_day"] * days, 2),
            "currency": rate_info["currency"],
            "days": days,
        })

    results.sort(key=lambda c: c["rate_per_day"])

    return {
        "query": {
            "destination": req.destination,
            "pickup_location": req.pickup_location,
            "days": days,
        },
        "result_count": len(results),
        "results": results,
        "_marketplace": marketplace_block(partner, ["hts_connect", "pricing"]),
    }


@app.post("/v1/cars/quote", tags=["cars"])
def car_quote(req: CarQuoteRequest, partner: dict = Depends(get_partner)):
    """
    Fully itemized car rental quote — supplier net, taxes, marketplace take, and Hopper products.
    """
    city_entry, car = _find_car(req.car_id)
    if not car:
        raise HTTPException(404, f"Unknown car_id '{req.car_id}'.")

    days = (req.dropoff_date - req.pickup_date).days
    if days < 1:
        raise HTTPException(422, "dropoff_date must be after pickup_date.")

    invalid = [pid for pid in req.hopper_products if pid not in HOPPER_PRODUCTS]
    if invalid:
        raise HTTPException(400, f"Unknown Hopper product(s): {', '.join(invalid)}")
    not_applicable = [
        pid for pid in req.hopper_products
        if "cars" not in HOPPER_PRODUCTS[pid]["applies_to"]
    ]
    if not_applicable:
        names = ", ".join(HOPPER_PRODUCTS[p]["name"] for p in not_applicable)
        raise HTTPException(400, f"Product(s) not applicable to car rentals: {names}")

    rate_info = car["rates"][req.pickup_location]
    tax = TAX_RULES.get(city_entry["country"], {"vat_pct": 0.0, "city_tax_per_night": 0.0})
    net = round(rate_info["rate_per_day"] * days, 2)
    vat = round(net * tax["vat_pct"], 2)
    take = round(net * partner["take_rate"], 2)
    hopper_items, hopper_total = _hopper_line_items(net, req.hopper_products, "cars", days=days)
    sell_price = round(net + vat + hopper_total, 2)

    return {
        "car_id": car["car_id"],
        "supplier": car["supplier"],
        "model": car["model"],
        "category": car["category"],
        "pickup_location": req.pickup_location,
        "location_name": rate_info["location_name"],
        "days": days,
        "currency": rate_info["currency"],
        "price_breakdown": {
            "supplier_net": net,
            "vat": vat,
            "marketplace_take": take,
            "hopper_products": hopper_items,
            "hopper_total": hopper_total,
            "sell_price": sell_price,
        },
        "_marketplace": marketplace_block(partner, ["pricing", "taxes"], req.hopper_products),
    }


@app.post("/v1/bundle/quote", tags=["bundle"])
def bundle_quote(req: BundleQuoteRequest, partner: dict = Depends(get_partner)):
    """
    Hotel + Car bundle quote.

    The marketplace take rate is applied to the *combined* GBV (hotel net +
    car net), giving a single blended marketplace_take line item — the key
    commercial-model talking point for bundles.
    """
    # --- Resolve hotel ---
    prop = next((x for x in PROPERTIES if x["property_id"] == req.property_id), None)
    if not prop:
        raise HTTPException(404, f"Unknown property_id '{req.property_id}'.")
    rate = next((r for r in prop["rates"] if r["rate_id"] == req.rate_id), None)
    if not rate:
        raise HTTPException(404, f"Unknown rate_id '{req.rate_id}' for this property.")

    # --- Resolve car ---
    city_entry, car = _find_car(req.car_id)
    if not car:
        raise HTTPException(404, f"Unknown car_id '{req.car_id}'.")

    nights = (req.check_out - req.check_in).days
    if nights < 1:
        raise HTTPException(422, "check_out must be after check_in.")

    invalid = [pid for pid in req.hopper_products if pid not in HOPPER_PRODUCTS]
    if invalid:
        raise HTTPException(400, f"Unknown Hopper product(s): {', '.join(invalid)}")
    not_applicable = [
        pid for pid in req.hopper_products
        if "bundle" not in HOPPER_PRODUCTS[pid]["applies_to"]
    ]
    if not_applicable:
        names = ", ".join(HOPPER_PRODUCTS[p]["name"] for p in not_applicable)
        raise HTTPException(400, f"Product(s) not applicable to bundles: {names}")

    # --- Hotel pricing ---
    hotel_tax = TAX_RULES.get(prop["country"], {"vat_pct": 0.0, "city_tax_per_night": 0.0})
    hotel_net = round(rate["supplier_net"] * nights, 2)
    hotel_vat = round(hotel_net * hotel_tax["vat_pct"], 2)
    hotel_city_tax = round(hotel_tax["city_tax_per_night"] * nights, 2)

    # --- Car pricing ---
    car_rate_info = car["rates"][req.pickup_location]
    car_tax = TAX_RULES.get(city_entry["country"], {"vat_pct": 0.0, "city_tax_per_night": 0.0})
    car_net = round(car_rate_info["rate_per_day"] * nights, 2)
    car_vat = round(car_net * car_tax["vat_pct"], 2)

    # --- Bundle take on combined GBV ---
    combined_net = round(hotel_net + car_net, 2)
    bundle_take = round(combined_net * partner["take_rate"], 2)

    # --- Bundle loyalty discount: 4% off combined net for booking together ---
    BUNDLE_DISCOUNT_PCT = 0.04
    bundle_discount = round(combined_net * BUNDLE_DISCOUNT_PCT, 2)

    # --- Hopper products on combined net ---
    hopper_items, hopper_total = _hopper_line_items(
        combined_net, req.hopper_products, "bundle", days=nights
    )

    sell_price = round(
        hotel_net + hotel_vat + hotel_city_tax
        + car_net + car_vat
        + hopper_total
        - bundle_discount,
        2,
    )

    return {
        "hotel": {
            "property_id": prop["property_id"],
            "name": prop["name"],
            "rate_id": rate["rate_id"],
            "room_name": rate["room_name"],
            "nights": nights,
        },
        "car": {
            "car_id": car["car_id"],
            "supplier": car["supplier"],
            "model": car["model"],
            "category": car["category"],
            "pickup_location": req.pickup_location,
            "location_name": car_rate_info["location_name"],
            "days": nights,
        },
        "currency": "USD",
        "price_breakdown": {
            "hotel": {
                "supplier_net": hotel_net,
                "vat": hotel_vat,
                "city_tax": hotel_city_tax,
            },
            "car": {
                "supplier_net": car_net,
                "vat": car_vat,
            },
            "combined_net": combined_net,
            "bundle_discount": bundle_discount,
            "bundle_marketplace_take": bundle_take,
            "hopper_products": hopper_items,
            "hopper_total": hopper_total,
            "sell_price": sell_price,
        },
        "_marketplace": marketplace_block(partner, ["pricing", "taxes", "bundle"], req.hopper_products),
    }
