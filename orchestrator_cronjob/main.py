import logging
import os

from twilio.rest import Client

from db import meeting_requests_dao
from db import phones_dao

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

logger = logging.getLogger(__name__)


def call_orchestrator():
    logger.info("Calling orchestrator")
    for pending_meeting_request in meeting_requests_dao.get_pending_meeting_requests():
        logger.info(f"Pending meeting request: {pending_meeting_request}")
        available_phone = phones_dao.get_available_phone()
        if not available_phone:
            logger.info(f"No available phone for {pending_meeting_request}")
            return

        phones_dao.update_phone_usage(available_phone.number, True)

        try:
            outbound_twiml = (
                f'<?xml version="1.0" encoding="UTF-8"?>'
                f'<Response><Connect><Stream url="wss://bountiful-cat-production.up.railway.app/media-stream"><Parameter name="meetingRequestId" value="{pending_meeting_request.meeting_request_id}" /><Parameter name="phoneNumber" value="{available_phone.number}" /></Stream></Connect></Response>'
            )

            call = client.calls.create(
                from_=available_phone.number,
                to=pending_meeting_request.client_phone,
                twiml=outbound_twiml
            )
            logger.info(f"Call started with SID: {call.sid}")
        except Exception as error:
            logger.error(f"Call failed with: {error}")
            phones_dao.update_phone_usage(available_phone.number, False)


if __name__ == "__main__":
    call_orchestrator()
