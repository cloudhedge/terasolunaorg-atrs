"""Report service for requesting and managing reports"""

from arq import create_pool
from arq.connections import RedisSettings

from ...config import settings


class ReportService:
    """Service for managing report generation requests"""

    def __init__(self):
        self._redis_settings = RedisSettings.from_dsn(settings.redis_url)

    async def request_history_report(self, membership_number: str) -> str:
        """
        Request async generation of reservation history report.

        Returns job ID that can be used to check status.
        """
        redis = await create_pool(self._redis_settings)

        job = await redis.enqueue_job(
            "generate_reservation_history_report",
            membership_number=membership_number,
        )

        await redis.close()
        return job.job_id

    async def get_job_status(self, job_id: str) -> dict:
        """Get status of a report generation job"""
        redis = await create_pool(self._redis_settings)

        job = await redis.job(job_id)
        if not job:
            return {"status": "not_found"}

        status = await job.status()
        result = await job.result(timeout=0)

        await redis.close()

        return {
            "status": status.value,
            "result": result if result else None,
        }
