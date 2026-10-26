import hashlib
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_dotenv(path: Path) -> None:
    """Читает .env для локального запуска. На Render переменные задаются в панели."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or 0)

# Render сам задаёт RENDER_EXTERNAL_URL. Если он есть — работаем через вебхук, иначе через polling
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE") or os.getenv("RENDER_EXTERNAL_URL", "")
WEBHOOK_PATH = "/webhook"
PORT = int(os.getenv("PORT", "8080"))

# Telegram принимает в секрете только буквы, цифры, _ и -. Хэшируем, чтобы подошла любая строка
WEBHOOK_SECRET = hashlib.sha256(os.getenv("WEBHOOK_SECRET", BOT_TOKEN).encode()).hexdigest()

if not BOT_TOKEN:
    raise SystemExit("Не задан BOT_TOKEN. Скопируй .env.example в .env и впиши токен.")
