from concurrent.futures import ThreadPoolExecutor
import boto3
import logging

sts = boto3.client("sts")

sso_obj = {
  "access_token": None,
  "region": None
}

def set_sso_access_token(access_token, region):
  sso_obj["access_token"] = access_token
  sso_obj["region"] = region

class OrgWorker:
  def __init__(self, account_ids, role_name, role_session_name, ignore_regions=None, only_regions=None):
    self.account_ids = account_ids
    self.role_name = role_name
    self.role_session_name = role_session_name
    self.ignore_regions = ignore_regions
    self.only_regions = only_regions

  def exec_in_all_accounts(self, func, service_name="ec2", **kwargs):
    results = []
    futures = []
    for account_id in self.account_ids:
      worker = AccountWorker(account_id, self.role_name, self.role_session_name, self.ignore_regions, self.only_regions)
      futures.append(worker.exec_in_all_regions(func, service_name, **kwargs))
    for future in futures:
      results = results + future.result()
    return results
    
class AccountWorker:
  def __init__(self, account_id, role_name, role_session_name, ignore_regions=None, only_regions=None):
    self.account_id = account_id
    self.role_name = role_name
    self.role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    self.role_session_name = role_session_name
    self.executor = ThreadPoolExecutor(max_workers=30)
    self.ignore_regions = ignore_regions
    self.only_regions = only_regions

  def _create_session(self, region=None):
    if sso_obj["access_token"] is None:
      # get temp credentials
      creds = sts.assume_role(
        RoleArn=self.role_arn,
        RoleSessionName=self.role_session_name,
        DurationSeconds=900)
    else:
      # get temp credentials (via sso)
      sso = boto3.client("sso", region_name=sso_obj["region"])
      credsObj = sso.get_role_credentials(
        accessToken=sso_obj["access_token"], 
        accountId=self.account_id, 
        roleName=self.role_name)
      creds = credsObj["roleCredentials"]

    # create the session
    return boto3.session.Session(
        aws_access_key_id=creds["accessKeyId"],
        aws_secret_access_key=creds["secretAccessKey"],
        aws_session_token=creds["sessionToken"],
        region_name=region)

  def _execute(self, region, func, **kwargs):
    try:
      logger = logging.getLogger(f"aws:{self.account_id}:{region}")
      result = func(self._create_session(region), logger, **kwargs)
      return {
        "region": region,
        "account_id": self.account_id,
        "role_arn": self.role_arn,
        "result": result
      }
    except Exception as e:
      return {
        "region": region,
        "account_id": self.account_id,
        "role_arn": self.role_arn,
        "error": e
      }

  def _parallel_execute(self, func, service_name, **kwargs):
    results = []
    futures = []

    regions = self._get_service_regions(service_name)

    for region in regions:
      futures.append(self.executor.submit(self._execute, region, func, **kwargs))
    
    for future in futures:
      results.append(future.result())

    return results
      
  def _get_service_regions(self, service_name="ec2"):
    regions = self._create_session().get_available_regions(service_name=service_name, partition_name="aws")
    if not self.ignore_regions is None:
      regions = [r for r in regions if not r in self.ignore_regions]
    if not self.only_regions is None:
      regions = [r for r in regions if r in self.only_regions]
    return regions

  def exec_in_all_regions(self, func, service_name="ec2", **kwargs):
    return self.executor.submit(self._parallel_execute, func, service_name, **kwargs)
