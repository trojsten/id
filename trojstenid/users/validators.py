from oauth2_provider.oauth2_validators import OAuth2Validator

from trojstenid.users.models import User


class OurOAuth2Validator(OAuth2Validator):
    oidc_claim_scope = OAuth2Validator.oidc_claim_scope
    oidc_claim_scope.update({"groups": "groups", "school_info": "school_info"})

    def get_additional_claims(self, request):
        user: User = request.user
        school_info = None
        if record := user.get_current_school_record():
            school_info = record.to_dict()

        return {
            "name": user.get_full_name(),
            "family_name": user.last_name,
            "given_name": user.first_name,
            "preferred_username": user.username,
            "email": user.email,
            "groups": [g.name for g in user.groups.all()],
            "school_info": school_info,
        }

    def validate_silent_login(self, request):
        return True

    def validate_silent_authorization(self, request):
        return True
