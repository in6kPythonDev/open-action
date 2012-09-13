from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import int_to_base36, base36_to_int
from django.utils.crypto import salted_hmac

from django.conf import settings

import base64

TOKEN_UID_PREFIX = ':&~0'
TOKEN_UID_POSTFIX = '|ab'

class ActionReferralTokenGenerator(PasswordResetTokenGenerator):
    """Strategy object used to generate tokens for referral of an action join.

    Django API user parameter is the couple (action, user) in OpenAction

    The final token would have <3 digit time>-<base64 of prefix+uid><separator><hash>.
    Just leave <3 digit time> at the start in order to make self.check_token compatible

    How to invalidate the token? Token should work just once?

    No. It should work more than once, so it is just invalidated by timeout days
    """

    def get_user_pk_from_token(self, token):
        ts_part, other_part = token.split('-')
        uid_part, real_token_part = other_part.split(TOKEN_UID_POSTFIX)
        decoded_uid_part = base64.decodestring(uid_part)
        return decoded_uid_part.replace(TOKEN_UID_PREFIX, '')

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.

        THIS METHOD is COPIED from django/contrib/auth/tokens.py
        The only difference is that is does not check against PASSWORD_RESET_TIMEOUT_DAYS,
        but against REFERRAL_TOKEN_RESET_TIMEOUT_DAYS

        """

        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > settings.REFERRAL_TOKEN_RESET_TIMEOUT_DAYS:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):

        # IMPORTANT: Django API user parameter = OpenAction (action, user)!
        # The user is the one that called for action
        action, user = user

        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)

        # NOT hashing the internal state of the action or the calling user,
        # because there is no invalidation method
        key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"
        value = unicode(user.id) + unicode(action.id) + \
            user.password + user.last_login.strftime('%Y-%m-%d %H:%M:%S') + \
            unicode(timestamp)
        hash = salted_hmac(key_salt, value).hexdigest()[::2]

        # UID PART to recognize user by token
        uid_part = base64.encodestring("%s%s" % (TOKEN_UID_PREFIX, user.id))

        return "%s-%s%s%s" % (ts_b36, uid_part, TOKEN_UID_POSTFIX, hash)


    def _make_token_with_timestamp_old(self, user, timestamp):
        raise PermissionDenied

