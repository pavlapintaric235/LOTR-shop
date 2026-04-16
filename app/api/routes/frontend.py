from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["frontend"])

templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def frontend_home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )