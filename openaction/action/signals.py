import django.dispatch

post_action_status_update = django.dispatch.Signal(providing_args=["old_status"])
#added declared vote
post_declared_vote_add = django.dispatch.Signal(providing_args=["vote_instance"])


