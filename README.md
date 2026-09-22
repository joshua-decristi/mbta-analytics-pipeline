## Environment:

- Python 3.14.7
- PDM 2.29.2 (in-project venv enabled)

---

## Vehicle Normalization

```py
MBTA_URL = "https://api-v3.mbta.com/vehicles?page%5Blimit%5D=1"
MBTA_URL_RESPONSE_FIXTURES_FILE = "data/fixtures/raw/vehicles-response.json"
```

| Raw MBTA field                     | Normalized field |
| ---------------------------------- | ---------------- |
| data[].id                          | vehicle_id       |
| data[].relationships.route.data.id | route_id         |
| data[].attributes.updated_at       | observed_at      |
| data[].attributes.latitude         | latitude         |
| data[].attributes.longitude        | longitude        |
