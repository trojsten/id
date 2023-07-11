from oauth2_provider.oauth2_validators import OAuth2Validator

from trojstenid.users.models import User


class OurOAuth2Validator(OAuth2Validator):
    oidc_claim_scope = OAuth2Validator.oidc_claim_scope
    oidc_claim_scope.update({"groups": "groups"})

    def get_additional_claims(self, request):
        user: User = request.user
        return {
            "name": user.get_full_name(),
            "family_name": user.last_name,
            "given_name": user.first_name,
            "preferred_username": user.username,
            "email": user.email,
            "groups": [g.name for g in user.groups.all()],
        }

    def validate_silent_login(self, request):
        return request.user and request.user.is_authenticated

    def validate_silent_authorization(self, request):
        return request.user and request.user.is_authenticated
