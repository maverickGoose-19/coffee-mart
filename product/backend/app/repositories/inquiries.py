from __future__ import annotations

from ..db import execute, query_all, query_one
from ..utils import make_entity_id


class InquiryRepository:
    def get_lot_request_context(self, lot_id: str) -> dict | None:
        return query_one(
            """
            SELECT
              l.id,
              l.supplier_id,
              l.export_ready,
              l.sample_ready,
              l.compliance_ready,
              s.sample_size_grams,
              s.prior_notice_handler
            FROM coffee_lots l
            JOIN suppliers s ON s.id = l.supplier_id
            WHERE l.id = %s
            """,
            (lot_id,),
        )

    def create_inquiry(
        self,
        *,
        buyer_id: str,
        supplier_id: str,
        lot_id: str,
        destination_country: str,
        requested_sample_grams,
        prior_notice_required: bool,
        prior_notice_filed_by: str | None,
        buyer_message: str | None,
        source_surface: str,
    ) -> str:
        inquiry_id = make_entity_id("inq", lot_id)
        execute(
            """
            INSERT INTO buyer_inquiries (
              id, buyer_id, supplier_id, lot_id, destination_country, requested_sample_grams,
              shipment_status, prior_notice_required, prior_notice_filed, prior_notice_filed_by,
              buyer_message, source_surface
            ) VALUES (
              %s, %s, %s, %s, %s, %s,
              'new', %s, FALSE, %s,
              %s, %s
            )
            """,
            (
                inquiry_id,
                buyer_id,
                supplier_id,
                lot_id,
                destination_country,
                requested_sample_grams,
                prior_notice_required,
                prior_notice_filed_by,
                buyer_message,
                source_surface,
            ),
        )
        return inquiry_id

    def has_completed_relationship(self, buyer_id: str, supplier_id: str) -> bool:
        completed = query_one(
            """
            SELECT 1
            FROM buyer_inquiries
            WHERE buyer_id = %s
              AND supplier_id = %s
              AND shipment_status = 'closed'
            LIMIT 1
            """,
            (buyer_id, supplier_id),
        )
        if completed:
            return True
        completed = query_one(
            """
            SELECT 1
            FROM buyer_lot_interactions i
            JOIN coffee_lots l ON l.id = i.lot_id
            WHERE i.buyer_id = %s
              AND l.supplier_id = %s
              AND i.interaction_type = 'deal_closed'
            LIMIT 1
            """,
            (buyer_id, supplier_id),
        )
        return bool(completed)

    def get_admin_inquiries(self) -> list[dict]:
        return query_all(
            """
            SELECT
              i.id,
              i.shipment_status,
              i.tracking_number,
              i.courier,
              i.prior_notice_required,
              i.prior_notice_filed,
              i.prior_notice_filed_by,
              i.buyer_message,
              i.source_surface,
              i.buyer_id,
              i.supplier_id,
              b.company_name AS buyer_name,
              COALESCE(brs.average_rating, 0) AS buyer_average_rating,
              COALESCE(brs.review_count, 0) AS buyer_review_count,
              s.company_name AS supplier_name,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count,
              l.lot_name
            FROM buyer_inquiries i
            JOIN buyers b ON b.id = i.buyer_id
            JOIN suppliers s ON s.id = i.supplier_id
            JOIN coffee_lots l ON l.id = i.lot_id
            LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            ORDER BY i.created_at DESC
            """
        )

    def get_buyer_inquiries(self, buyer_id: str) -> list[dict]:
        return query_all(
            """
            SELECT
              i.id,
              i.shipment_status,
              i.tracking_number,
              i.courier,
              i.prior_notice_required,
              i.prior_notice_filed,
              i.prior_notice_filed_by,
              i.buyer_message,
              i.source_surface,
              i.buyer_id,
              i.supplier_id,
              b.company_name AS buyer_name,
              COALESCE(brs.average_rating, 0) AS buyer_average_rating,
              COALESCE(brs.review_count, 0) AS buyer_review_count,
              s.company_name AS supplier_name,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count,
              l.lot_name
            FROM buyer_inquiries i
            JOIN buyers b ON b.id = i.buyer_id
            JOIN suppliers s ON s.id = i.supplier_id
            JOIN coffee_lots l ON l.id = i.lot_id
            LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            WHERE i.buyer_id = %s
            ORDER BY i.created_at DESC
            """,
            (buyer_id,),
        )

    def get_inquiry_by_id(self, inquiry_id: str) -> dict | None:
        return query_one(
            """
            SELECT
              i.id,
              i.buyer_id,
              i.supplier_id,
              i.lot_id,
              i.destination_country,
              i.shipment_status,
              i.tracking_number,
              i.courier,
              i.prior_notice_required,
              i.prior_notice_filed,
              i.prior_notice_filed_by,
              i.buyer_message,
              i.source_surface,
              b.contact_email AS buyer_email,
              b.company_name AS buyer_company
            FROM buyer_inquiries i
            LEFT JOIN buyers b ON b.id = i.buyer_id
            WHERE i.id = %s
            """,
            (inquiry_id,),
        )

    def update_inquiry_shipment(
        self,
        inquiry_id: str,
        *,
        shipment_status: str,
        tracking_number: str | None = None,
        courier: str | None = None,
        prior_notice_filed: bool | None = None,
        prior_notice_filed_by: str | None = None,
    ) -> dict | None:
        # Build a dynamic SET clause for only the non-None fields
        fields: list[str] = ["shipment_status = %s"]
        values: list = [shipment_status]
        if tracking_number is not None:
            fields.append("tracking_number = %s")
            values.append(tracking_number)
        if courier is not None:
            fields.append("courier = %s")
            values.append(courier)
        if prior_notice_filed is not None:
            fields.append("prior_notice_filed = %s")
            values.append(prior_notice_filed)
        if prior_notice_filed_by is not None:
            fields.append("prior_notice_filed_by = %s")
            values.append(prior_notice_filed_by)
        values.append(inquiry_id)
        execute(
            f"UPDATE buyer_inquiries SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        return self.get_inquiry_by_id(inquiry_id)

    def get_supplier_inquiries(self, supplier_id: str) -> list[dict]:
        return query_all(
            """
            SELECT
              i.id,
              i.shipment_status,
              i.tracking_number,
              i.courier,
              i.prior_notice_required,
              i.prior_notice_filed,
              i.prior_notice_filed_by,
              i.buyer_message,
              i.source_surface,
              i.buyer_id,
              i.supplier_id,
              b.company_name AS buyer_name,
              COALESCE(brs.average_rating, 0) AS buyer_average_rating,
              COALESCE(brs.review_count, 0) AS buyer_review_count,
              s.company_name AS supplier_name,
              COALESCE(srs.average_rating, 0) AS supplier_average_rating,
              COALESCE(srs.review_count, 0) AS supplier_review_count,
              l.lot_name
            FROM buyer_inquiries i
            JOIN buyers b ON b.id = i.buyer_id
            JOIN suppliers s ON s.id = i.supplier_id
            JOIN coffee_lots l ON l.id = i.lot_id
            LEFT JOIN buyer_review_summary brs ON brs.buyer_id = b.id
            LEFT JOIN supplier_review_summary srs ON srs.supplier_id = s.id
            WHERE i.supplier_id = %s
            ORDER BY i.created_at DESC
            """,
            (supplier_id,),
        )
