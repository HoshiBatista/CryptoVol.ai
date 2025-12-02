import uvicorn
import subprocess
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, Request

from app.db.session import init_db_data
from app.core.logging_config import logger
from app.services.model_loader import reload_models_in_db
from app.api.endpoints import auth, users, health, dashboard


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

TEMPLATES_DIR = APP_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def run_migrations():
    """
    Запускает миграции Alembic синхронно.
    Это гарантирует, что таблицы существуют ДО того, как приложение начнет работу.
    """
    logger.info("🔄 Running Alembic migrations via subprocess...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("✅ Migrations applied successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Migration failed (Process Error): {e}")
    except FileNotFoundError:
        logger.error("❌ Alembic command not found. Make sure alembic is installed.")
    except Exception as e:
        logger.error(f"❌ Migration failed (Unknown): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    run_migrations()
    await init_db_data()
    await reload_models_in_db()
    yield
    logger.info("Application shutdown...")


app = FastAPI(
    title="CryptoVol.ai API [Minimal]",
    description="Базовый запуск для проверки БД и создания миграций.",
    version="0.0.1",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(health.router, prefix="/api", tags=["Health Check"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "CryptoVol.ai | Advanced Cryptocurrency Volatility Analysis",
            "api_base_url": "/api",
        },
    )


@app.get("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "signup.html", {"request": request, "title": "Sign Up | CryptoVol.ai"}
    )


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
