# Backend

This folder now contains both the relational schema and the structured FastAPI backend app.

## App Structure

- `app/config.py` for settings and env loading
- `app/models.py` for Pydantic request models
- `app/service.py` for backend orchestration and domain rules
- `app/main.py` for FastAPI routes, startup lifecycle, and static serving integration

## Key Entities

- `buyers`
- `suppliers`
- `coffee_lots`
- `buyer_inquiries`
- `buyer_lot_interactions`
- `supplier_reviews`
- `buyer_reviews`
- `buyer_recommendation_surveys`
- `supplier_readiness` view

## Notes

- the current domain logic is being migrated into the structured app incrementally
- review writes are now gated by a completed buyer-supplier relationship signal
- the schema remains intentionally lightweight, but the server architecture is now production-friendlier than the original single-file prototype
