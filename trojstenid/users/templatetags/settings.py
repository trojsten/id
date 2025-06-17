from django import template

register = template.Library()


@register.inclusion_tag("_partials/navbar_items.html", takes_context=True)
def navbar_menu(context):
    items = [
        ("mdi:user", "Osobné údaje", "account_profile"),
        ("mdi:school", "Školy", "account_school"),
        ("mdi:email", "E-mailové adresy", "account_email"),
        ("mdi:password", "Zmena hesla", "account_change_password"),
        ("mdi:account-key", "Externé účty", "socialaccount_connections"),
    ]

    context["items"] = items
    return context
