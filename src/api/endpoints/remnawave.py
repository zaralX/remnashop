from typing import cast

import orjson
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException, Request, Response, status
from loguru import logger
from remnawave.controllers import WebhookUtility
from remnawave.models.webhook import HwidUserDeviceDto as RemnaHwidUserDeviceDto
from remnawave.models.webhook import NodeDto as RemnaNodeDto
from remnawave.models.webhook import UserDto as RemnaUserDto

from src.core.config.app import AppConfig
from src.core.constants import API_V1, REMNAWAVE_WEBHOOK_PATH
from src.services.remnawave import RemnawaveService

router = APIRouter(prefix=API_V1)


@router.post(REMNAWAVE_WEBHOOK_PATH)
@inject
async def remnawave_webhook(
    request: Request,
    config: FromDishka[AppConfig],
    remnawave_service: FromDishka[RemnawaveService],
) -> Response:
    try:
        raw_body = await request.body()
        payload = WebhookUtility.parse_webhook(
            body=raw_body.decode("utf-8"),
            headers=dict(request.headers),
            webhook_secret=config.remnawave.webhook_secret.get_secret_value(),
            validate=True,
        )
    except orjson.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")
    except Exception as exc:
        logger.exception("Webhook validation failed")
        raise HTTPException(status_code=401, detail=str(exc))

    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if WebhookUtility.is_user_event(payload.event):
        user = cast(RemnaUserDto, WebhookUtility.get_typed_data(payload))
        await remnawave_service.handle_user_event(payload.event, user)

    elif WebhookUtility.is_user_hwid_devices_event(payload.event):
        device = cast(RemnaHwidUserDeviceDto, WebhookUtility.get_typed_data(payload))
        await remnawave_service.handle_device_event(payload.event, device)

    elif WebhookUtility.is_node_event(payload.event):
        node = cast(RemnaNodeDto, WebhookUtility.get_typed_data(payload))
        await remnawave_service.handle_node_event(payload.event, node)

    else:
        logger.warning(f"Unhandled Remnawave event type: {payload.event}")

    return Response(status_code=status.HTTP_200_OK)
