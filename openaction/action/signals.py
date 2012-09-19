import django.dispatch

post_action_status_update = django.dispatch.Signal(providing_args=["old_status"])


