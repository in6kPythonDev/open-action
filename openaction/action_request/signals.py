import django.dispatch

action_moderation_request_submitted = django.dispatch.Signal()
action_moderation_request_processed = django.dispatch.Signal()
action_message_sent = django.dispatch.Signal()
action_message_replied = django.dispatch.Signal(providing_args=['replier'])
