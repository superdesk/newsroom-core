from blinker import Namespace

signals = Namespace()

publish_item = signals.signal("publish-item")

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
