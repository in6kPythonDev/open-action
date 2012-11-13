from django import template
from django.conf import settings
from django.template import defaultfilters as filters


register = template.Library()

@register.simple_tag
def html_render_resource(resource):
    """Render an OpenAction resource"""

    html = """<a href="%(url)s" class="%(res_type)s">%(resource)s</a>""" % {
        'url' : resource.get_absolute_url(),
        'res_type' : resource.resource_type,
        'resource' : resource
    }
    return html

@register.simple_tag
def html_action_item(action):
    """Return html snippet for an action item."""

    html = """
<li class="action-item">
    <div class="action-author">%(author)s</div>
    <div class="action-title">%(action)s</div>
    <div class="action-geonames">%(geonames)s</div>
    <div class="action-categories">%(categories)s</div>
</li>
""" % {
        "author" : html_render_resource(action.author),
        "action" : html_render_resource(action),
        "geonames" : [html_render_resource(geoname) for geoname in action.geonames],
        "categories" :  [html_render_resource(category) for category in action.categories],
    }
    return html

@register.simple_tag
def html_action_tags(action):
    """ Return html for action category and locations """

    html = """
<i class="icon-map-marker"></i> %(locations)s
<br>
<i class="icon-tag"></i> %(categories)s
""" % {
        "locations" : ",".join([html_render_resource(geoname) for geoname in action.geonames]),
        "categories" : ",".join([html_render_resource(category) for category in action.categories])
    }
    return html

@register.inclusion_tag('tags/action_status.html')
def html_action_status(action):
    """ Return html for an action status """
    return {
        "voters": action.votes.count(),
        "answers": action.comments.count(),
        "target": action.threshold
    }

@register.inclusion_tag('tags/action_overview.html')
def html_action_overview(action):
    """Return html for an action item """
    d = {
        "action": html_render_resource(action),
        "tags" : html_action_tags(action),
    }
    d.update( html_action_status(action) )
    return d

@register.simple_tag
def html_blogpost_item(blogpost):
    """Return html snippet for a blog post item."""

    html = """
<li class="blogpost-item">
    <div class="blogpost-action">%(action_title)s</div>
    <div class="blogpost-title">%(blogpost_title)s</div>
    <div class="blogpost-subtitle">%(blogpost_date)s - %(blogpost_author)s - %(ncomments)s commenti</div>
    <div class="blogpost-excerpt">%(blogpost_excerpt)s</div>
</li>
""" % {
        "action_title" : blogpost.action,
        "blogpost_title" : blogpost.title,
        "blogpost_date" : blogpost.added_at,
        "blogpost_author" : blogpost.author,
        "ncomments" : blogpost.comments.count(),
        "blogpost_excerpt": filters.truncatewords(blogpost.html(), 300),
    }
    return html

@register.simple_tag
def html_activity_item(activity):
    """Return html snippet for an activity item."""

    extra_content = ""
    if activity.activity_type == askbot_extensions_consts.TYPE_ACTIVITY_ANSWER:
        extra_content = activity.content_object.title

    html = """
<div class="activity-item">
    <div class="activity-author">il %(activity_date)s %(activity_user)s</div>
    <div class="activity-type">ha %(activity_type)s</div>
    <div class="activity-action">%(action)s</div>
    <div class="activity-extra">%(extra_content)s</div>
</div>
""" % {
        "activity_user" : activity.user,
        "activity_date" : activity.active_at,
        "activity_type" : askbot_extensions_consts.ACTIVITY_TYPE_DISPLAY_D[activity.activity_type],
        "action" : activity.content_object.action,
        "extra_content" : extra_content,
    }
    return html


