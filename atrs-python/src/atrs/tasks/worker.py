"""arq worker configuration"""

from arq import cron
from arq.connections import RedisSettings

from ..config import settings


async def startup(ctx):
    """Worker startup - initialize database connection"""
    from ..config.database import get_database_manager

    db_manager = get_database_manager()
    await db_manager.connect()
    ctx["db"] = db_manager.database


async def shutdown(ctx):
    """Worker shutdown - cleanup"""
    from ..config.database import get_database_manager

    db_manager = get_database_manager()
    await db_manager.disconnect()


class WorkerSettings:
    """arq worker settings"""

    functions = [
        "atrs.tasks.report_generator.generate_reservation_history_report",
    ]

    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings.from_dsn(settings.redis_url)

    # Retry settings
    max_tries = 3
    job_timeout = 300  # 5 minutes
