"""
Mock data for the HTS API Marketplace prototype.

Two things are modeled here that matter for the *marketplace* (not just the
lodging) story:

1. PARTNERS — each partner key maps to a commercial tier and a take rate.
   This is how we make the platform-vs-variable commercial model tangible in
   the API surface itself, rather than burying it in a pricing deck.

2. PROPERTIES — the underlying lodging supply that HTS Connect orchestrates,
   plus the content (Content & Property Mapping) and rates (Pricing) layered
   on top.

All properties are real hotels. Review scores are approximate Booking.com
averages; supplier_net rates reflect indicative wholesale pricing (c.65–70%
of published rack) for demo purposes only.

Pricing is in USD. EUR amounts converted at ~1.08 (approximate mid-2025 rate).
"""

# --- Partner registry (mock auth + commercial model) --------------------------
# In production this is the Extranet / partner onboarding layer. Here the API key
# both authenticates the partner AND determines their take-rate tier.
PARTNERS = {
    "hts_demo_sbx_000": {
        "partner_name": "Sandbox",
        "tier": "sandbox",
        "take_rate": 0.000,
        "model": "free_sandbox",
        "description": "Mock data only · Rate limited · No production access",
    },
    "hts_demo_slf_003": {
        "partner_name": "Starter",
        "tier": "self_serve",
        "take_rate": 0.085,
        "model": "variable",
        "description": "Pay-as-you-go · Production access · Community docs support",
    },
    "hts_demo_std_002": {
        "partner_name": "Standard",
        "tier": "standard",
        "take_rate": 0.070,
        "model": "variable",
        "description": "Production SLA · Core capabilities · Email support",
    },
    "hts_demo_grw_004": {
        "partner_name": "Growth",
        "tier": "growth",
        "take_rate": 0.055,
        "model": "variable_with_commitment",
        "description": "$???K/mo min GBV · Bundles &amp; Financial Products",
    },
    "hts_demo_ent_001": {
        "partner_name": "Enterprise",
        "tier": "enterprise",
        "take_rate": 0.035,
        "model": "platform_plus_variable",
        "description": "Annual committed GBV · Custom packaging · Dedicated AM",
    },
}

# --- Lodging supply -----------------------------------------------------------
# Each property carries content (Content & Property Mapping capability) and a set
# of rates (Pricing capability). `supplier_net` is what the supplier charges us;
# the marketplace take rate is applied on top at quote time.
PROPERTIES = [
    # ── Lisbon ────────────────────────────────────────────────────────────────
    {
        "property_id": "hts_lis_4412",
        "name": "Bairro Alto Hotel",
        "destination": "Lisbon",
        "country": "PT",
        "star_rating": 5,
        "review_score": 9.4,
        "lat": 38.7103,
        "lng": -9.1433,
        "content": {
            "description": (
                "Member of The Leading Hotels of the World, occupying a "
                "restored 18th-century building at the heart of Chiado. "
                "The rooftop bar offers sweeping views over the Tagus."
            ),
            "amenities": ["wifi", "restaurant", "bar", "spa", "rooftop_terrace",
                          "wellness", "concierge", "air_conditioning"],
            "images": ["https://cdn.example/hts/lis_4412/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_4412_a", "room_name": "Deluxe Room", "board": "breakfast",
             "supplier_net": 308.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_4412_b", "room_name": "Classic Room", "board": "room_only",
             "supplier_net": 243.00, "currency": "USD", "refundable": False},
        ],
    },
    {
        "property_id": "hts_lis_7781",
        "name": "Memmo Alfama",
        "destination": "Lisbon",
        "country": "PT",
        "star_rating": 4,
        "review_score": 9.2,
        "lat": 38.7102,
        "lng": -9.1306,
        "content": {
            "description": (
                "Adults-only design boutique hotel — the first of its kind in "
                "Alfama — with a terrace pool and panoramic views over the "
                "Tagus rooftops, a five-minute walk from the Cathedral."
            ),
            "amenities": ["wifi", "pool", "wine_bar", "terrace", "air_conditioning"],
            "images": ["https://cdn.example/hts/lis_7781/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_7781_a", "room_name": "Superior Room", "board": "breakfast",
             "supplier_net": 211.00, "currency": "USD", "refundable": True},
        ],
    },
    {
        "property_id": "hts_lis_9032",
        "name": "Hotel Marquês de Pombal",
        "destination": "Lisbon",
        "country": "PT",
        "star_rating": 4,
        "review_score": 8.9,
        "lat": 38.7192,
        "lng": -9.1451,
        "content": {
            "description": (
                "Contemporary four-star hotel on Avenida da Liberdade, steps "
                "from Marquês de Pombal square and Parque Eduardo VII, with "
                "individually decorated rooms and a spa."
            ),
            "amenities": ["wifi", "restaurant", "gym", "sauna", "hammam",
                          "air_conditioning"],
            "images": ["https://cdn.example/hts/lis_9032/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_9032_a", "room_name": "Superior Room", "board": "room_only",
             "supplier_net": 127.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_9032_b", "room_name": "Superior Room", "board": "breakfast",
             "supplier_net": 146.00, "currency": "USD", "refundable": True},
        ],
    },
    {
        "property_id": "hts_lis_2210",
        "name": "Hotel Metropole",
        "destination": "Lisbon",
        "country": "PT",
        "star_rating": 3,
        "review_score": 8.1,
        "lat": 38.7137,
        "lng": -9.1424,
        "content": {
            "description": (
                "Classic Art Nouveau hotel directly on Praça do Rossio, "
                "Lisbon's historic main square, with original 1917 décor "
                "and views across to the Carmo ruins."
            ),
            "amenities": ["wifi", "bar", "breakfast", "air_conditioning"],
            "images": ["https://cdn.example/hts/lis_2210/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_2210_a", "room_name": "Classic Double", "board": "breakfast",
             "supplier_net": 103.00, "currency": "USD", "refundable": False},
            {"rate_id": "r_2210_b", "room_name": "Classic Double", "board": "room_only",
             "supplier_net": 85.00, "currency": "USD", "refundable": True},
        ],
    },
    # ── Madrid ────────────────────────────────────────────────────────────────
    {
        "property_id": "hts_mad_1101",
        "name": "The Palace, a Luxury Collection Hotel, Madrid",
        "destination": "Madrid",
        "country": "ES",
        "star_rating": 5,
        "review_score": 8.8,
        "lat": 40.4148,
        "lng": -3.6945,
        "content": {
            "description": (
                "Grand palace hotel on the Paseo del Prado since 1912 — "
                "commissioned by King Alfonso XIII — famed for its "
                "stained-glass dome and its position at the centre of "
                "Madrid's art museum triangle."
            ),
            "amenities": ["wifi", "restaurant", "bar", "spa", "fitness",
                          "concierge", "room_service", "air_conditioning"],
            "images": ["https://cdn.example/hts/mad_1101/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_1101_a", "room_name": "Deluxe Room", "board": "breakfast",
             "supplier_net": 335.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_1101_b", "room_name": "Classic Room", "board": "room_only",
             "supplier_net": 265.00, "currency": "USD", "refundable": False},
        ],
    },
    {
        "property_id": "hts_mad_2034",
        "name": "Hyatt Centric Gran Vía Madrid",
        "destination": "Madrid",
        "country": "ES",
        "star_rating": 4,
        "review_score": 8.7,
        "lat": 40.4167,
        "lng": -3.7033,
        "content": {
            "description": (
                "Lifestyle hotel on the Gran Vía featuring locally commissioned "
                "artwork throughout its 136 rooms, a rooftop bar, and a "
                "front-row seat to Madrid's best shopping and nightlife."
            ),
            "amenities": ["wifi", "restaurant", "bar", "rooftop_bar",
                          "fitness", "air_conditioning"],
            "images": ["https://cdn.example/hts/mad_2034/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_2034_a", "room_name": "King Room", "board": "breakfast",
             "supplier_net": 192.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_2034_b", "room_name": "King Room", "board": "room_only",
             "supplier_net": 167.00, "currency": "USD", "refundable": True},
        ],
    },
    {
        "property_id": "hts_mad_3178",
        "name": "AC Hotel Recoletos by Marriott",
        "destination": "Madrid",
        "country": "ES",
        "star_rating": 4,
        "review_score": 8.2,
        "lat": 40.4186,
        "lng": -3.6876,
        "content": {
            "description": (
                "Contemporary Marriott property in the upscale Recoletos "
                "district, known for its live jazz sessions, a short stroll "
                "from El Retiro park and the Prado."
            ),
            "amenities": ["wifi", "restaurant", "bar", "gym", "air_conditioning"],
            "images": ["https://cdn.example/hts/mad_3178/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_3178_a", "room_name": "Superior Room", "board": "room_only",
             "supplier_net": 157.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_3178_b", "room_name": "Superior Room", "board": "breakfast",
             "supplier_net": 175.00, "currency": "USD", "refundable": True},
        ],
    },
    # ── New York ──────────────────────────────────────────────────────────────
    {
        "property_id": "hts_nyc_0101",
        "name": "The Plaza, A Fairmont Managed Hotel",
        "destination": "New York",
        "country": "US",
        "star_rating": 5,
        "review_score": 8.5,
        "lat": 40.7645,
        "lng": -73.9746,
        "content": {
            "description": (
                "Iconic 1907 French Renaissance château at Fifth Avenue and "
                "Central Park South, home to the legendary Palm Court "
                "afternoon tea and 282 rooms and suites."
            ),
            "amenities": ["wifi", "restaurant", "bar", "spa", "fitness",
                          "concierge", "room_service", "air_conditioning"],
            "images": ["https://cdn.example/hts/nyc_0101/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_0101_a", "room_name": "Deluxe Room", "board": "room_only",
             "supplier_net": 749.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_0101_b", "room_name": "Classic Room", "board": "room_only",
             "supplier_net": 589.00, "currency": "USD", "refundable": False},
        ],
    },
    {
        "property_id": "hts_nyc_0234",
        "name": "The Standard, High Line",
        "destination": "New York",
        "country": "US",
        "star_rating": 4,
        "review_score": 7.9,
        "lat": 40.7409,
        "lng": -74.0081,
        "content": {
            "description": (
                "Eighteen-story hotel elevated on concrete stilts above the "
                "High Line, with floor-to-ceiling windows offering "
                "unobstructed Hudson River and skyline views from every room."
            ),
            "amenities": ["wifi", "restaurant", "bar", "rooftop_bar",
                          "fitness", "air_conditioning"],
            "images": ["https://cdn.example/hts/nyc_0234/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_0234_a", "room_name": "King Room", "board": "room_only",
             "supplier_net": 249.00, "currency": "USD", "refundable": True},
            {"rate_id": "r_0234_b", "room_name": "Queen Room", "board": "room_only",
             "supplier_net": 215.00, "currency": "USD", "refundable": True},
        ],
    },
    {
        "property_id": "hts_nyc_0389",
        "name": "The Knickerbocker Hotel",
        "destination": "New York",
        "country": "US",
        "star_rating": 4,
        "review_score": 8.4,
        "lat": 40.7552,
        "lng": -73.9860,
        "content": {
            "description": (
                "Restored 1906 Beaux-Arts landmark at the crossroads of "
                "Times Square, where legend holds the martini was invented, "
                "and home to a Maxfield Parrish mural and a rooftop bar."
            ),
            "amenities": ["wifi", "restaurant", "bar", "rooftop_bar",
                          "fitness", "concierge", "air_conditioning"],
            "images": ["https://cdn.example/hts/nyc_0389/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_0389_a", "room_name": "Deluxe King", "board": "room_only",
             "supplier_net": 209.00, "currency": "USD", "refundable": False},
            {"rate_id": "r_0389_b", "room_name": "Deluxe King", "board": "breakfast",
             "supplier_net": 245.00, "currency": "USD", "refundable": True},
        ],
    },
    {
        "property_id": "hts_nyc_0412",
        "name": "citizenM New York Times Square",
        "destination": "New York",
        "country": "US",
        "star_rating": 3,
        "review_score": 8.8,
        "lat": 40.7616,
        "lng": -73.9850,
        "content": {
            "description": (
                "Tech-forward hotel on West 50th Street with iPad-controlled "
                "rooms, three rooftop terraces, a 24-hour canteen, and "
                "consistently among the highest-rated hotels in Midtown."
            ),
            "amenities": ["wifi", "bar", "rooftop_terrace", "fitness",
                          "canteen_24hr", "air_conditioning"],
            "images": ["https://cdn.example/hts/nyc_0412/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_0412_a", "room_name": "Standard King", "board": "room_only",
             "supplier_net": 149.00, "currency": "USD", "refundable": False},
            {"rate_id": "r_0412_b", "room_name": "Standard King", "board": "room_only",
             "supplier_net": 169.00, "currency": "USD", "refundable": True},
        ],
    },
    {
        "property_id": "hts_mad_4892",
        "name": "Hotel Mediodía",
        "destination": "Madrid",
        "country": "ES",
        "star_rating": 3,
        "review_score": 7.8,
        "lat": 40.4076,
        "lng": -3.6922,
        "content": {
            "description": (
                "Historic 1914 French Neoclassical building opposite Atocha "
                "station, at the gateway to the art museum triangle, with "
                "original stained-glass windows and a grand staircase."
            ),
            "amenities": ["wifi", "breakfast", "air_conditioning"],
            "images": ["https://cdn.example/hts/mad_4892/1.jpg"],
        },
        "rates": [
            {"rate_id": "r_4892_a", "room_name": "Double Room", "board": "breakfast",
             "supplier_net": 78.00, "currency": "USD", "refundable": False},
            {"rate_id": "r_4892_b", "room_name": "Double Room", "board": "room_only",
             "supplier_net": 63.00, "currency": "USD", "refundable": True},
        ],
    },
]

# --- Hopper financial products ------------------------------------------------
# Hopper Cloud fintech products available as add-ons at quote time.
# fee_type is one of:
#   "pct_of_net"  — percentage of (supplier_net × nights)
#   "flat"        — fixed fee per booking, regardless of duration
HOPPER_PRODUCTS = {
    "cfar": {
        "name": "Cancel for Any Reason",
        "tagline": "Cancel up to check-in for a full refund, no questions asked.",
        "description": (
            "Cancel your booking at any point up to check-in and receive a "
            "100% refund of the hotel cost. Hopper covers any supplier "
            "cancellation fees. Available on all rates, including "
            "non-refundable."
        ),
        "fee_type": "pct_of_net",
        "fee_value": 0.08,   # 8% of supplier net total
        "applies_to": ["lodging", "bundle"],
    },
    "lfar": {
        "name": "Leave for Any Reason",
        "tagline": "Check out early and Hopper covers the cost to rebook.",
        "description": (
            "Leave at or after check-in for any reason and Hopper will cover "
            "100% of the cost to rebook a same-star-rated hotel for your "
            "remaining nights. Hotels-specific product."
        ),
        "fee_type": "pct_of_net",
        "fee_value": 0.07,   # 7% of supplier net total
        "applies_to": ["lodging"],
    },
    "price_freeze": {
        "name": "Price Freeze",
        "tagline": "Lock in today's hotel rate for up to 14 days while you decide.",
        "description": (
            "Pay a one-time fee to freeze the current rate. If the price "
            "rises before you confirm, you still pay today's rate. If it "
            "falls, you pay the lower price. The freeze fee is credited "
            "toward your final booking."
        ),
        "fee_type": "flat",
        "fee_value": 35.00,  # flat fee per booking (converted from €32 at 1.08)
        "applies_to": ["lodging", "bundle"],
    },
    "price_drop": {
        "name": "Price Drop Protection",
        "tagline": "Book now. If the hotel price drops before check-in, we credit you the difference.",
        "description": (
            "After booking, Hopper's price engine monitors the rate daily. "
            "If the price falls, you automatically receive a Hopper travel "
            "credit for the full difference — no forms, no chasing."
        ),
        "fee_type": "pct_of_net",
        "fee_value": 0.03,   # 3% of supplier net total
        "applies_to": ["lodging", "bundle"],
    },
    "price_freeze_cars": {
        "name": "Price Freeze for Cars",
        "tagline": "Lock in today's car rate for up to 7 days while you decide.",
        "description": (
            "Pay a one-time fee to freeze the current rental rate. If the "
            "price rises before you confirm, you still pay today's rate. "
            "If it falls, you pay the lower price."
        ),
        "fee_type": "flat",
        "fee_value": 19.00,  # flat fee per booking
        "applies_to": ["cars", "bundle"],
    },
}

# --- Car rental supply --------------------------------------------------------
# Airport locations carry a ~15-20% premium vs city centre (airport surcharges,
# shuttle costs, higher demand). Rates are per-day supplier net in USD, reflecting
# indicative wholesale pricing for demo purposes.
CAR_RENTALS = {
    "Lisbon": {
        "country": "PT",
        "cars": [
            {
                "car_id": "car_lis_001",
                "supplier": "Hertz",
                "category": "economy",
                "model": "VW Polo or similar",
                "seats": 5,
                "bags": 2,
                "transmission": "manual",
                "rates": {
                    "airport": {
                        "location_name": "Lisbon Airport (LIS)",
                        "rate_per_day": 38.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Lisbon City Centre",
                        "rate_per_day": 32.00,
                        "currency": "USD",
                    },
                },
            },
            {
                "car_id": "car_lis_002",
                "supplier": "Enterprise",
                "category": "midsize",
                "model": "Toyota Corolla or similar",
                "seats": 5,
                "bags": 3,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "Lisbon Airport (LIS)",
                        "rate_per_day": 52.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Lisbon City Centre",
                        "rate_per_day": 44.00,
                        "currency": "USD",
                    },
                },
            },
            {
                "car_id": "car_lis_003",
                "supplier": "Avis",
                "category": "suv",
                "model": "Ford Kuga or similar",
                "seats": 5,
                "bags": 4,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "Lisbon Airport (LIS)",
                        "rate_per_day": 78.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Lisbon City Centre",
                        "rate_per_day": 66.00,
                        "currency": "USD",
                    },
                },
            },
        ],
    },
    "Madrid": {
        "country": "ES",
        "cars": [
            {
                "car_id": "car_mad_001",
                "supplier": "Enterprise",
                "category": "economy",
                "model": "Seat Ibiza or similar",
                "seats": 5,
                "bags": 2,
                "transmission": "manual",
                "rates": {
                    "airport": {
                        "location_name": "Madrid Barajas Airport (MAD)",
                        "rate_per_day": 36.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Madrid City Centre",
                        "rate_per_day": 30.00,
                        "currency": "USD",
                    },
                },
            },
            {
                "car_id": "car_mad_002",
                "supplier": "National",
                "category": "midsize",
                "model": "Toyota Camry or similar",
                "seats": 5,
                "bags": 3,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "Madrid Barajas Airport (MAD)",
                        "rate_per_day": 54.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Madrid City Centre",
                        "rate_per_day": 46.00,
                        "currency": "USD",
                    },
                },
            },
            {
                "car_id": "car_mad_003",
                "supplier": "Hertz",
                "category": "suv",
                "model": "BMW X1 or similar",
                "seats": 5,
                "bags": 4,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "Madrid Barajas Airport (MAD)",
                        "rate_per_day": 82.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Madrid City Centre",
                        "rate_per_day": 69.00,
                        "currency": "USD",
                    },
                },
            },
        ],
    },
    "New York": {
        "country": "US",
        "cars": [
            {
                "car_id": "car_nyc_001",
                "supplier": "Budget",
                "category": "economy",
                "model": "Chevrolet Spark or similar",
                "seats": 4,
                "bags": 2,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "JFK International Airport",
                        "rate_per_day": 79.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Midtown Manhattan",
                        "rate_per_day": 65.00,
                        "currency": "USD",
                    },
                },
            },
            {
                "car_id": "car_nyc_002",
                "supplier": "Avis",
                "category": "midsize",
                "model": "Toyota Camry or similar",
                "seats": 5,
                "bags": 3,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "JFK International Airport",
                        "rate_per_day": 115.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Midtown Manhattan",
                        "rate_per_day": 95.00,
                        "currency": "USD",
                    },
                },
            },
            {
                "car_id": "car_nyc_003",
                "supplier": "Enterprise",
                "category": "suv",
                "model": "Jeep Grand Cherokee or similar",
                "seats": 5,
                "bags": 4,
                "transmission": "automatic",
                "rates": {
                    "airport": {
                        "location_name": "JFK International Airport",
                        "rate_per_day": 165.00,
                        "currency": "USD",
                    },
                    "city": {
                        "location_name": "Midtown Manhattan",
                        "rate_per_day": 139.00,
                        "currency": "USD",
                    },
                },
            },
        ],
    },
}

# --- Tax rules ----------------------------------------------------------------
# Tax model per destination (Taxes capability). Mock: a percentage VAT plus a
# fixed per-night city tax. City tax amounts converted from EUR at ~1.08.
TAX_RULES = {
    "PT": {"vat_pct": 0.06,   "city_tax_per_night": 4.32, "currency": "USD"},
    "ES": {"vat_pct": 0.10,   "city_tax_per_night": 2.43, "currency": "USD"},
    # US: combined NY State + NYC sales tax (8.875%) + hotel occupancy tax (5.875%)
    # city_tax_per_night covers the state unit fee ($1.50) + city per-night fee ($2.00)
    "US": {"vat_pct": 0.1475, "city_tax_per_night": 3.50, "currency": "USD"},
}
