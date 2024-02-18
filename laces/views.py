import logging

from typing import TYPE_CHECKING

from django.http import HttpResponse


if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


def serve(request: "HttpRequest", component_slug: str) -> HttpResponse:
    logger.error(component_slug)
    return HttpResponse()
