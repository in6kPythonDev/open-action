from django import template

register = template.Library()

@register.inclusion_tag('tags/form_field_text.html')
def form_field_text(formField):
    return {
        'field': formField
    }

@register.inclusion_tag('tags/form_field_checkbox.html')
def form_field_checkbox(formField):
    return {
        'field': formField
    }

@register.inclusion_tag('tags/form_field_text.html')
def form_field_password(formField):
    return {
        'field': formField,
        'type': 'password',
        'empty_value': True,
    }

@register.inclusion_tag('tags/form_field_textarea.html')
def form_field_textarea(formField, klass='', rows=None, cols=None):
    return {
        'field': formField,
        'class': klass,
        'rows' : rows,
        'cols' : cols,
    }