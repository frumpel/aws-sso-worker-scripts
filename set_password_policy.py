from sso import SSO
from workers import OrgWorker, set_sso_access_token
import json

SSO_URL=None
SSO_REGION=None
# Change these to suit your account setup or set them as environment variables
# SSO_URL="https://ACCOUNT_NUMBER.awsapps.com/start"
# SSO_REGION="us-west-2"

SSO_WORKER_ROLE="AWSAdministratorAccess"
SSO_WORKER_REGIONS=["us-west-2", "us-east-1"]
SSO_WORKER_SET_POLICY={
        "MinimumPasswordLength": 10,
        "RequireSymbols": True,
        "RequireNumbers": True,
        "RequireUppercaseCharacters": True,
        "RequireLowercaseCharacters": True,
        "AllowUsersToChangePassword": True,
        # Note: even though 0 is the default for "off" it can't be SET to 0
        # uncomment if you want to set a number > 0
        # "MaxPasswordAge": 0,
        # "PasswordReusePrevention": 0, 
        # "HardExpiry": 0
    }

sso = SSO(SSO_URL,SSO_REGION)
set_sso_access_token(sso.access_token, sso.region)

# do stuff
def my_func(session, logger):
    # logger.debug("Creationg IAM client for session")
    # logger.debug(str(session))
    iam = session.client("iam")
    # logger.debug("Got IAM response")
    # logger.debug(str(iam))
    result = iam.update_account_password_policy(**SSO_WORKER_SET_POLICY)
    # logger.debug("Got IAM policy result")
    # logger.debug(str(result))
    return result

account_ids = [a["accountId"] for a in sso.my_accounts()]
worker = OrgWorker(account_ids, SSO_WORKER_ROLE, "my-code-session", None, SSO_WORKER_REGIONS)
results = worker.exec_in_all_accounts(my_func)

print(results)
# # Brute force clean errors
# for result in results:
#     if 'error' in result:
#         result.pop('error',None)
#         result['result']={'PasswordPolicy':{}}

# print(json.dumps(results,indent=2))
