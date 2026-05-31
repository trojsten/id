from django import template

register = template.Library()

VEDUCI_GROUP = "veduci@iam.trojsten.sk"


@register.inclusion_tag("_partials/navbar_items.html", takes_context=True)
def navbar_menu(context):
    items = [
        ("mdi:user", "Osobné údaje", "account_profile"),
        ("mdi:school", "Školy", "account_school"),
        ("mdi:email", "E-mailové adresy", "account_email"),
        ("mdi:password", "Zmena hesla", "account_change_password"),
        ("mdi:account-key", "Externé účty", "socialaccount_connections"),
    ]

    user = context.get("user")
    if (
        user
        and user.is_authenticated
        and user.groups.filter(name=VEDUCI_GROUP).exists()
    ):
        items.append(("mdi:account-group", "Skupiny", "group_list"))

    context["items"] = items
    return context
