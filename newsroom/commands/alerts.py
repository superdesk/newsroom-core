from quart.cli import with_appcontext

from newsroom.company_expiry_alerts import CompanyExpiryAlerts
from newsroom.monitoring.email_alerts import MonitoringEmailAlerts
from .cli import newsroom_cli


@newsroom_cli.register_async_command("send_company_expiry_alerts", with_appcontext=True)
async def send_company_expiry_alerts():
    """
    Send expiry alerts for companies which are close to be expired (now + 7 days)

    Example:
    ::

        $ python manage.py content_reset

    """
    await CompanyExpiryAlerts().send_alerts()


@newsroom_cli.command("send_monitoring_schedule_alerts")
@with_appcontext
def send_monitoring_schedule_alerts():
    """
    Send monitoring schedule alerts.

    Example:
    ::

        $ python manage.py send_monitoring_schedule_alerts

    """
    MonitoringEmailAlerts().run()


@newsroom_cli.command("send_monitoring_immediate_alerts")
@with_appcontext
def send_monitoring_immediate_alerts():
    """
    Send monitoring immediate alerts.

    Example:
    ::

        $ python manage.py send_monitoring_immediate_alerts

    """
    MonitoringEmailAlerts().run(True)
