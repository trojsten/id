from oauth2_provider.oauth2_validators import OAuth2Validator

from trojstenid.users.models import User


class OurOAuth2Validator(OAuth2Validator):
    oidc_claim_scope = OAuth2Validator.oidc_claim_scope
    oidc_claim_scope.update(
        {
            # field: required scope
            "groups": "groups",
            "school_info": "school_info",
            "emails": "email",
            "previously_known_as": "profile",
        }
    )

    def get_additional_claims(self, request):
        user: User = request.user
        school_info = None
        if record := user.get_current_school_record():
            school_info = record.to_dict()

        emails = set()
        emails.add(user.email)
        for e in user.emailaddress_set.filter(verified=True):
            emails.add(e.email)

        merged_users = user.previously_known_as.values_list("id", flat=True)

        return {
            "name": user.get_full_name(),
            "family_name": user.last_name,
            "given_name": user.first_name,
            "preferred_username": user.username,
            "email": user.email,
            "emails": list(emails),
            "groups": [g.name for g in user.groups.all()],
            "school_info": school_info,
            "previously_known_as": merged_users,
        }

    def validate_silent_login(self, request):  # pyright:ignore
        return True

    def validate_silent_authorization(self, request):  # pyright:ignore
        return True
