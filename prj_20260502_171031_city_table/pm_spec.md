# PM spec: District table

This project adds a new table `district` linked to `city`.

## Required columns
- `district_id` (PK, INTEGER AUTOINCREMENT)
- `city_id` (FK -> city)
- `name` (non-empty TEXT)
- `code` (optional official administrative code)
- `type` (TEXT, allowed: `urban`, `suburban`, `industrial`, `other`)
- `status` (TEXT, allowed: `active`, `merged`, `deprecated`)

## Constraints
- Foreign key integrity: inserting a district referencing a non-existing `city.id` must fail.
- CHECK: `length(trim(name)) > 0`
- CHECK: `type IN ('urban','suburban','industrial','other')`
- CHECK: `status IN ('active','merged','deprecated')`

## Indexes
- `idx_district_city_id`
- `idx_district_status`
- `idx_district_type`
