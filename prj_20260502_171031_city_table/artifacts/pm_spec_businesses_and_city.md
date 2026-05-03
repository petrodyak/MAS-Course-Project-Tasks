# PM Spec: Businesses & Economy (Businesses)

## Entity: Businesses & Economy

### Fields
- `id` (INTEGER, PK, autoincrement)
- `name` (TEXT, NOT NULL)
- `type` (TEXT, NOT NULL; allowed values):
  - `Company`
  - `Store / Shop`
  - `Restaurant`
  - `Office`
- `city_id` (INTEGER, NOT NULL, FK → `city(id)`)
- `description` (TEXT, NULL)
- `established_year` (TEXT, NULL)

### Validation
- Business `type` is validated to allow only the four specified values.
- Invalid types are rejected at the service/repository layer.

## Relationship: City → Businesses
- Cardinality: **City (1) → (N) Businesses**
- `businesses.city_id` is a required FK with `NOT NULL`.
- Deleting a city cascades deletion of its businesses.

## API Scenarios (project convention)
- **POST** `/cities/{cityId}/businesses` creates a business scoped to that `city_id`.
- **GET** `/cities/{cityId}/businesses` returns only businesses for the given city.
- If a city has no businesses, GET returns an empty list.
