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
        'resource' : getattr(resource, 'bare_title', resource)
    }
    return html

@register.simple_tag
def html_render_action(action):
    """Render an OpenAction resource"""

    html = """<a href="%(url)s" class="%(res_type)s">%(resource)s</a>""" % {
        'url' : action.get_absolute_url(),
        'res_type' : action.resource_type,
        'resource' : action.bare_title,
    }
    return html

@register.inclusion_tag('tags/action_item.html')
def html_action_item(action):
    """Return html snippet for an action item."""
    d = {
        "action": html_render_resource(action),
        "tags" : html_action_tags(action),
        "action_url": action.get_absolute_url(),
        'organization': html_render_resource(action.in_nomine_org) if action.in_nomine_org else None,
    }
    return d

@register.simple_tag
def html_action_tags(action):
    """ Return html for action category and locations """

    html = []
    if action.geonames:
        html.append( '<i class="icon-map-marker"></i> %s' % ", ".join([html_render_resource(geoname) for geoname in action.geonames]) )
    if action.categories:
        html.append( '<i class="icon-tag"></i> %s' % ", ".join([html_render_resource(category) for category in action.categories]) )

    return "<br>".join(html)


@register.inclusion_tag('tags/action_status.html')
def html_action_status(action):
    """ Return html for an action status """
    vote_count = action.votes.count()
    threshold = action.threshold if action.threshold else 0
    return {
        "votes": vote_count,
        "answers": action.comments.count(),
        "target": threshold,
        "progress": ((vote_count * 100.0) / threshold) if threshold else 0.0,
    }

@register.inclusion_tag('tags/action_item.html')
def html_action_overview(action):
    """Return html for an action item """
    d = {
        "action": html_render_resource(action),
        "tags" : html_action_tags(action),
        "action_url": action.get_absolute_url(),
        'organization': html_render_resource(action.in_nomine_org) if action.in_nomine_org else None,
        "status": True
    }
    d.update( html_action_status(action) )
    return d

@register.simple_tag
def html_blogpost_item(blogpost):
    """Return html snippet for a blog post item."""

    html = u"""
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
        "blogpost_excerpt": filters.truncatewords(blogpost.html, 300),
    }
    return html

@register.inclusion_tag('tags/action_activity.html')
def html_activity_item(activity):
    """Return html snippet for an activity item."""
    from askbot_extensions import consts
    activities = dict(consts.TYPE_ACTIVITY_CHOICES)

    extra_content = ""
    if activity.activity_type == consts.TYPE_ACTIVITY_ANSWER:
        extra_content = activity.content_object.title

    return {
        "activity_user" : activity.user,
        "activity_date" : activity.active_at,
        "activity_type" : activities[activity.activity_type],
        "action" : activity.content_object,
        "extra_content" : extra_content,
        }


@register.inclusion_tag('tags/action_list.html', takes_context=True)
def html_action_list(context, action_list):

    from django.http import QueryDict
#    base_url = context['request'].get_full_path().split()
#    if '?' not in base_url: base_url += '?'
    base_url = context['request'].path
    q = context['request'].GET.copy()
    try:
        del q['__sort']
    except KeyError:
        pass
    return {
        'base_url': base_url + '?' + q.urlencode(),
        'action_list': action_list,
        'sorting': context['request'].GET.get('__sort',False)
    }

@register.inclusion_tag('tags/action_comment.html')
def html_action_comment(comment):
    return { 'comment': comment }

@register.inclusion_tag('tags/blogpost_list.html')
def html_blogpost_list(blog_post_list):
    return { 'blog_post_list': blog_post_list }

@register.inclusion_tag('tags/voter_list.html')
def html_voter_list(voters, latest=None, reversed=False):
    voters = voters[::-1] if reversed else voters
    return { 'voters': voters[:latest] if latest else voters, 'reversed': reversed }