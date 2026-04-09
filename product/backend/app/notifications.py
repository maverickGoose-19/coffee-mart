from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import settings


class EmailNotifier:
    def _send_with_resend(self, subject: str, body: str) -> bool:
        if not settings.alert_email_to or not settings.resend_api_key or not settings.resend_from_email:
            return False
        payload = {
            "from": settings.resend_from_email,
            "to": [settings.alert_email_to],
            "subject": subject,
            "text": body,
        }
        if settings.resend_reply_to:
            payload["reply_to"] = settings.resend_reply_to
        request = Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "coffee-platform/0.1",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=15) as response:
                return 200 <= response.status < 300
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            print(f"[alert-email resend failed] {subject}\nstatus={exc.code}\n{details}")
            return False
        except URLError as exc:
            print(f"[alert-email resend failed] {subject}\n{exc}")
            return False

    def _send_with_smtp(self, subject: str, body: str) -> bool:
        if not settings.alert_email_to or not settings.smtp_host or not settings.smtp_from_email:
            return False
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.smtp_from_email
        message["To"] = settings.alert_email_to
        message.set_content(body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True

    def _send(self, subject: str, body: str) -> bool:
        if self._send_with_resend(subject, body):
            return True
        if self._send_with_smtp(subject, body):
            return True
        if not settings.alert_email_to:
            print(f"[alert-email skipped] {subject}\n{body}")
            return False
        print(f"[alert-email skipped] {subject}\n{body}")
        return False

    def notify_new_supplier(self, supplier: dict) -> None:
        subject = f"New supplier submitted: {supplier['companyName']}"
        body = (
            f"A new supplier was created.\n\n"
            f"Supplier: {supplier['companyName']}\n"
            f"ID: {supplier['id']}\n"
            f"Export ready: {supplier['exportReady']}\n"
            f"Sample ready: {supplier['sampleReady']}\n"
            f"Compliance ready: {supplier['complianceReady']}\n"
            f"Approval status: {supplier['approvalStatus']}\n"
        )
        self._send(subject, body)

    def notify_new_inquiry(self, inquiry: dict, buyer: dict, lot: dict) -> None:
        subject = f"New inquiry: {buyer.get('buyer_name') or buyer.get('email')} -> {lot['id']}"
        body = (
            f"A new inquiry was created.\n\n"
            f"Inquiry ID: {inquiry['id']}\n"
            f"Buyer ID: {buyer.get('buyer_id')}\n"
            f"Buyer: {buyer.get('buyer_name') or buyer.get('email')}\n"
            f"Lot ID: {lot['id']}\n"
            f"Supplier ID: {lot['supplier_id']}\n"
            f"Shipment status: {inquiry['shipmentStatus']}\n"
            f"Prior notice required: {inquiry['priorNoticeRequired']}\n"
        )
        self._send(subject, body)

    def notify_profile_change_request(self, request: dict) -> None:
        subject = f"Profile change request: {request['entityType']} {request['entityId']}"
        body = (
            f"A profile change request was submitted.\n\n"
            f"Request ID: {request['id']}\n"
            f"Entity type: {request['entityType']}\n"
            f"Entity ID: {request['entityId']}\n"
            f"Changed fields: {', '.join(request.get('changedFields', []))}\n"
            f"Status: {request['status']}\n"
        )
        self._send(subject, body)

    def notify_profile_change_decision(self, request: dict, decision: str) -> None:
        """Notify supplier/buyer that their profile change request was approved or rejected."""
        entity_type = request.get("entity_type") or request.get("entityType", "entity")
        entity_id = request.get("entity_id") or request.get("entityId", "")
        changed = request.get("changed_fields") or request.get("changedFields") or []
        verb = "approved" if decision == "approved" else "rejected"
        subject = f"Profile update {verb}: {entity_type} {entity_id}"
        body = (
            f"Your profile change request has been {verb} by an admin.\n\n"
            f"Request ID: {request['id']}\n"
            f"Entity: {entity_type} {entity_id}\n"
            f"Changed fields: {', '.join(changed)}\n\n"
        )
        body += (
            "Your profile has been updated with the requested changes.\n"
            if decision == "approved"
            else "Your current profile has not been changed. Contact support if you have questions.\n"
        )
        self._send(subject, body)

    def notify_inquiry_accepted(self, inquiry: dict) -> None:
        """Notify buyer that their sample request was accepted."""
        inquiry_id = inquiry.get("id", "")
        lot_id = inquiry.get("lot_id", "")
        buyer_email = inquiry.get("buyer_email")
        subject = f"Sample request accepted — Inquiry {inquiry_id}"
        body = (
            f"Great news! The supplier has accepted your sample request.\n\n"
            f"Inquiry ID: {inquiry_id}\n"
            f"Lot: {lot_id}\n"
            f"Next step: The supplier will begin preparing your sample.\n\n"
            f"Track progress in your Inquiries dashboard.\n"
        )
        self._send_to_buyer(buyer_email, subject, body)

    def notify_inquiry_rejected(self, inquiry: dict) -> None:
        """Notify buyer that their sample request was rejected."""
        inquiry_id = inquiry.get("id", "")
        lot_id = inquiry.get("lot_id", "")
        buyer_email = inquiry.get("buyer_email")
        subject = f"Sample request not accepted — Inquiry {inquiry_id}"
        body = (
            f"The supplier was unable to accept your sample request at this time.\n\n"
            f"Inquiry ID: {inquiry_id}\n"
            f"Lot: {lot_id}\n"
            f"Status: Closed\n\n"
            f"Browse other available lots in the catalog and submit a new request.\n"
        )
        self._send_to_buyer(buyer_email, subject, body)

    def _send_to_buyer(self, buyer_email: str | None, subject: str, body: str) -> bool:
        """Send to a buyer's email directly, falling back to the platform alert address."""
        if not buyer_email:
            return self._send(subject, body)
        if settings.resend_api_key and settings.resend_from_email:
            payload = {
                "from": settings.resend_from_email,
                "to": [buyer_email],
                "subject": subject,
                "text": body,
            }
            if settings.resend_reply_to:
                payload["reply_to"] = settings.resend_reply_to
            request = Request(
                "https://api.resend.com/emails",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "coffee-platform/0.1",
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=15) as response:
                    if 200 <= response.status < 300:
                        return True
            except (HTTPError, URLError):
                pass
        return self._send(subject, body)
