from newsroom.email_delivery_monitor import EmailDeliveryMonitor


def test_email_delivery_monitor_imports_from_top_level_module():
    assert EmailDeliveryMonitor.__name__ == "EmailDeliveryMonitor"
