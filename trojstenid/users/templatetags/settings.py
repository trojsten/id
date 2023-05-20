from django import template

register = template.Library()


@register.inclusion_tag("_partials/navbar_items.html", takes_context=True)
def navbar_menu(context):
    items = [
        ("mdi:email", "E-mailové adresy", "account_email"),
        ("mdi:password", "Zmena hesla", "account_change_password"),
    ]

    context["items"] = items
    return context
