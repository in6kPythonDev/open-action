"""

Request types
-------------

* MODERATION: a request of moderation of the Action from its owner to an Action follower
* MESSAGE: a private message between user related to the same Action

"""

REQUEST_TYPE_MODERATION = 'moderation'
REQUEST_TYPE_MESSAGE = 'message'
REQUEST_TYPE_SET_VICTORY = 'set_victory'

REQUEST_TYPE = {
    'mod' : REQUEST_TYPE_MODERATION,
    'msg' : REQUEST_TYPE_MODERATION,
    'vict' : REQUEST_TYPE_SET_VICTORY,
}
