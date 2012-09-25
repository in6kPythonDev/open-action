from django.dispatch import receiver
from django.conf import settings

import logging

log = logging.getLogger(settings.PROJECT_NAME)

#handle the moderation requests from the action owner
