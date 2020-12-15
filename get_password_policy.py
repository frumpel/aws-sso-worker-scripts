from sso import SSO
from workers import OrgWorker, set_sso_access_token
import json

SSO_URL=None
SSO_REGION=None
# Change these to suit your account setup or set them as environment variables
# SSO_URL="https://ACCOUNT_NUMBER.awsapps.com/start"
# SSO_REGION="us-west-2"

# Configure these defaults to suit your needs. No override provided
SSO_WORKER_ROLE="AWSAdministratorAccess"
SSO_WORKER_REGIONS=["us-west-2", "us-east-1"]

sso = SSO(SSO_URL,SSO_REGION)
set_sso_access_token(sso.access_token, sso.region)

# do stuff
def my_func(session, logger):
    # logger.debug("Creationg IAM client for session")
    # logger.debug(str(session))
    iam = session.client("iam")
    # logger.debug("Got IAM response")
    # logger.debug(str(iam))
    result = iam.get_account_password_policy()
    # logger.debug("Got IAM policy result")
    # logger.debug(str(result))
    return result

account_ids = [a["accountId"] for a in sso.my_accounts()]
worker = OrgWorker(account_ids, SSO_WORKER_ROLE, "my-code-session", None, SSO_WORKER_REGIONS)
results = worker.exec_in_all_accounts(my_func)

# Brute force clean errors
for result in results:
    if 'error' in result:
        result.pop('error',None)
        result['result']={'PasswordPolicy':{}}

print(json.dumps(results,indent=2))
