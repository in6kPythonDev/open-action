from django import template
from django.conf import settings


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
<div class="action-item">
    <div class="action-author">%(author)s</div>
    <div class="action-title">%(action)s</div>
    <div class="action-geonames">%(geonames)s</div>
    <div class="action-categories">%(categories)s</div>
</div>
""" % {
        'author' : html_render_resource(action.author),
        'action' : html_render_resource(action),
        'geonames' : [html_render_resource(geoname) for geoname in action.geonames],
        'categories' :  [html_render_resource(category) for category in action.categories],
    }
    return html

@register.simple_tag
def html_blogpost_item(blogpost):
    """Return html snippet for a blog post item."""

    html = """
<div class="blogpost-item">
    <div class="blogpost-author">%(blogpost_author)s</div>
    <div class="blogpost-title">%(blogpost)s</div>
    <div class="blogpost-action">%(action)s</div>
    <div class="blogpost-ncomments">ha ricevuto %(ncomments)s commenti</div>
</div>
""" % {
        'blogpost_author' : html_render_resource(blogpost.author),
        'blogpost' : html_render_resource(blogpost),
        'action' : html_render_resource(blogpost.action),
        'ncomments' : blogpost.comments.count(),
    }
    return html

@register.simple_tag
def html_activity_item(blogpost):
    """Return html snippet for an activity item."""

    html = """
<div class="activity-item">
    <div class="activity-author">%(activity_user)s il %(activity_date)s</div>
    <div class="activity-type">ha %(activity_type)s</div>
    <div class="activity-action">%(action)s</div>
</div>
""" % {
        'activity_user' : activity.user,
        'activity_date' : activity.active_at,
        'activity_type' : const.ACTIVITY_TYPE_DISPLAY_D[activity.activity_type],
        'action' : activity.content_object.action,
    }
    return html


