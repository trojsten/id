from oauth2_provider.oauth2_validators import OAuth2Validator

from trojstenid.users.models import User


class OurOAuth2Validator(OAuth2Validator):
    def get_additional_claims(self, request):
        user: User = request.user
        return {
            "name": user.get_full_name(),
            "family_name": user.last_name,
            "given_name": user.first_name,
            "preferred_username": user.username,
            "email": user.email,
        }
