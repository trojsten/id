from django import template

register = template.Library()


@register.inclusion_tag("forms/input.html")
def input(field):  # noqa: A001
    return {"field": field}


@register.inclusion_tag("forms/form.html")
def form(form):
    return {"form": form}
