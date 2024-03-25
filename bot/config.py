from moon_db import MoonUser
import services
from datetime import time


def set_time_after_restart(updater, tzone) -> None:
    for user_time in MoonUser().get_all_users():
        hours, minutes = map(int, user_time.notify_time.split(':'))
        updater.job_queue.run_daily(
            services.send_a_moon_info,
            time(hour=hours, minute=minutes, tzinfo=tzone),
            name=str(user_time.user_id),
            context=user_time.user_id
        )
