import logging

from typing import TYPE_CHECKING

from django.core.exceptions import BadRequest
from django.http import Http404, HttpResponse

from laces.components import ServableComponentNotFound, get_servable


if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


def serve(request: "HttpRequest", component_slug: str) -> HttpResponse:
    logger.error(component_slug)

    try:
        Component = get_servable(component_slug)
    except ServableComponentNotFound:
        raise Http404

    kwargs = request.GET.dict()

    try:
        component = Component(**kwargs)
    except TypeError as e:
        raise BadRequest(e)

    return HttpResponse(content=component.render_html())
