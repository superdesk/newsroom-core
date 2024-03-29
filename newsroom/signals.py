from blinker import Namespace

signals = Namespace()

publish_item = signals.signal("publish-item")
publish_event = signals.signal("publish-event")
publish_planning = signals.signal("publish-planning")


#:
#: ..versionadded:: 2.4
#:
push = signals.signal("push")

#:
#: ..versionadded:: 2.4
#:
user_created = signals.signal("user-created")
user_updated = signals.signal("user-updated")
user_deleted = signals.signal("user-deleted")

#:
#: ..versionadded:: 2.5.0
#:
company_create = signals.signal("company-create")
