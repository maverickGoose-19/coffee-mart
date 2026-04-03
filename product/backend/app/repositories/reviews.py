from __future__ import annotations

from ..db import execute, query_all
from ..utils import make_entity_id


class ReviewRepository:
    def get_supplier_reviews(self, supplier_id: str) -> list[dict]:
        return query_all(
            """
            SELECT
              id,
              reviewer_name,
              reviewer_role,
              reviewer_company,
              rating,
              review_text,
              created_at
            FROM supplier_reviews
            WHERE supplier_id = %s
            ORDER BY created_at DESC
            LIMIT 8
            """,
            (supplier_id,),
        )

    def get_buyer_reviews(self, buyer_id: str) -> list[dict]:
        return query_all(
            """
            SELECT
              id,
              reviewer_name,
              reviewer_role,
              reviewer_company,
              rating,
              review_text,
              created_at
            FROM buyer_reviews
            WHERE buyer_id = %s
            ORDER BY created_at DESC
            LIMIT 8
            """,
            (buyer_id,),
        )

    def create_supplier_review(
        self,
        *,
        supplier_id: str,
        reviewer_name: str,
        reviewer_role: str,
        reviewer_company: str | None,
        rating: int,
        review_text: str | None,
    ) -> dict:
        review_id = make_entity_id("suprev", supplier_id)
        execute(
            """
            INSERT INTO supplier_reviews (
              id, supplier_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (review_id, supplier_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text),
        )
        return {"id": review_id, "supplierId": supplier_id, "rating": rating}

    def create_buyer_review(
        self,
        *,
        buyer_id: str,
        reviewer_name: str,
        reviewer_role: str,
        reviewer_company: str | None,
        rating: int,
        review_text: str | None,
    ) -> dict:
        review_id = make_entity_id("buyrev", buyer_id)
        execute(
            """
            INSERT INTO buyer_reviews (
              id, buyer_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (review_id, buyer_id, reviewer_name, reviewer_role, reviewer_company, rating, review_text),
        )
        return {"id": review_id, "buyerId": buyer_id, "rating": rating}
