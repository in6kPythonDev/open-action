"""
Constants specific to OpenAction application

Action statuses
---------------

* DRAFT: an action has been created but parameters are not all defined.
  Users cannot vote the action
* READY: parameters are all defined, users can vote the action, but the action is
  still not reachable by search engines, nor by site search. Just only with the url
* ACTIVE: threshold reached
* CLOSED: timeout exceeded or failed
* VICTORY: leads to victory
* CANCELED DRAFT: not valid and erased

"""

ACTION_STATUS_DRAFT = 'draft'
ACTION_STATUS_READY = 'ready'
ACTION_STATUS_ACTIVE = 'active'
ACTION_STATUS_DELETED = 'deleted'
ACTION_STATUS_CLOSED = 'closed'
ACTION_STATUS_VICTORY = 'victory'

ACTION_STATUS = {
    ACTION_STATUS_DRAFT: 'DRAFT',
    ACTION_STATUS_READY: 'READY',
    ACTION_STATUS_DELETED : 'CANCELED DRAFT',
    ACTION_STATUS_ACTIVE : 'ACTIVE',
    ACTION_STATUS_CLOSED : 'CLOSED',
    ACTION_STATUS_VICTORY : 'VICTORY',
}
