from newsroom.company_expiry_alerts import CompanyExpiryAlerts
from newsroom.monitoring.email_alerts import MonitoringEmailAlerts

from .manager import manager


@manager.command
def send_company_expiry_alerts():
    """
    Send expiry alerts for companies which are close to be expired (now + 7 days)

    Example:
    ::

        $ python manage.py content_reset

    """
    CompanyExpiryAlerts().send_alerts()


@manager.command
def send_monitoring_schedule_alerts():
    """
    Send monitoring schedule alerts.

    Example:
    ::

        $ python manage.py send_monitoring_schedule_alerts

    """
    MonitoringEmailAlerts().run()


@manager.command
def send_monitoring_immediate_alerts():
    """
    Send monitoring immediate alerts.

    Example:
    ::

        $ python manage.py send_monitoring_immediate_alerts

    """
    MonitoringEmailAlerts().run(True)
