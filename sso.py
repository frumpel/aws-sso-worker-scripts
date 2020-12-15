import boto3
import webbrowser
import time
import os
import iters
import logging

logger = logging.getLogger("aws:sso")

class SSO:
    def __init__(self, start_url=None, sso_region=None):
        self.region=sso_region
        if sso_region is None:
            if not "SSO_REGION" in os.environ:
                raise Exception("SSO_REGION environment variable not found")
            self.region = os.environ["SSO_REGION"]
        self.start_url = start_url
        if start_url is None:
            if not "SSO_START_URL" in os.environ:
                raise Exception("SSO_START_URL environment variable not found")
            self.start_url = os.environ["SSO_START_URL"]
        self._login()

    def my_accounts(self):
        sso = boto3.client("sso", region_name=self.region)
        return iters.boto(sso.list_accounts, "accountList", accessToken=self.access_token)

    def _login(self):
        logger.info(f"Starting SSO login in {self.region} at {self.start_url}")

        sso_oidc = boto3.client("sso-oidc", region_name=self.region)

        sso_client = sso_oidc.register_client(
            clientName="python-sso-client",
            clientType="public")

        logger.info(f"SSO client registered ({sso_client['clientId']})")

        auth = sso_oidc.start_device_authorization(
            clientId=sso_client["clientId"],
            clientSecret=sso_client["clientSecret"],
            startUrl=self.start_url)

        logger.info(
            f"Device authorization started ({auth['verificationUriComplete']})")

        webbrowser.open(auth["verificationUriComplete"])

        # Wait for SSO to complete
        sso_timeout = 60
        while True:
            try:
                # this will throw errors until the SSO process is complete
                sso_token = sso_oidc.create_token(
                    clientId=sso_client["clientId"],
                    clientSecret=sso_client["clientSecret"],
                    grantType="urn:ietf:params:oauth:grant-type:device_code",
                    deviceCode=auth["deviceCode"])
                self.access_token = sso_token["accessToken"]
                logger.info("SSO login complete")
                break
            except:
                logger.info("Waiting for SSO authentication to complete...")
                sso_timeout -= 1
                time.sleep(1)
                if sso_timeout == 0:
                    raise Exception(
                        "Timed out waiting for SSO to complete, please try again.")
