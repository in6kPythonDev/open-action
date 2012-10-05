"""

Request types
-------------

* MODERATION: a request of moderation of the Action from its owner to an Action follower
* MESSAGE: a private message between user related to the same Action
*SET_VICTORY: a referrer ask to set the Action state to VICTORY
*SET_CLOSURE: a referrer ask to set the Action state to CLOSED

"""

REQUEST_TYPE_MODERATION = 'moderation'
REQUEST_TYPE_MESSAGE = 'message'
REQUEST_TYPE_SET_VICTORY = 'set_victory'
REQUEST_TYPE_SET_CLOSURE = 'set_closure'

REQUEST_TYPE = {
    'mod' : REQUEST_TYPE_MODERATION,
    'msg' : REQUEST_TYPE_MODERATION,
    'vict' : REQUEST_TYPE_SET_VICTORY,
    'clos' : REQUEST_TYPE_SET_CLOSURE,
}
