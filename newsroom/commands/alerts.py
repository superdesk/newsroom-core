from newsroom.company_expiry_alerts import CompanyExpiryAlerts
from newsroom.monitoring.email_alerts import MonitoringEmailAlerts
from newsroom.monitoring.email_delivery_monitor import EmailDeliveryMonitor
from .cli import newsroom_cli


@newsroom_cli.command("send_company_expiry_alerts")
async def send_company_expiry_alerts():
    """
    Send expiry alerts for companies which are close to be expired (now + 7 days)

    Example:
    ::

        $ python manage.py content_reset

    """
    await CompanyExpiryAlerts().send_alerts()


@newsroom_cli.command("send_monitoring_schedule_alerts")
async def send_monitoring_schedule_alerts():
    """
    Send monitoring schedule alerts.

    Example:
    ::

        $ python manage.py send_monitoring_schedule_alerts

    """
    await MonitoringEmailAlerts().run()


@newsroom_cli.command("send_monitoring_immediate_alerts")
async def send_monitoring_immediate_alerts():
    """
    Send monitoring immediate alerts.

    Example:
    ::

        $ python manage.py send_monitoring_immediate_alerts

    """
    await MonitoringEmailAlerts().run(True)


@newsroom_cli.command("send_email_delivery_monitor")
async def send_email_delivery_monitor():
    """
    Send the email delivery monitor message.

    Example:
    ::

        $ python manage.py send_email_delivery_monitor

    """
    await EmailDeliveryMonitor().run()
