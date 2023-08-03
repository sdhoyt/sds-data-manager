"""Module with helper functions for creating standard sets of stacks"""
# Installed
from aws_cdk import App, Environment

# Local
from sds_data_manager.stacks import (
    api_gateway_stack,
    backup_bucket_stack,
    domain_stack,
    dynamodb_stack,
    opensearch_stack,
    s3_data_buckets_stack,
    sds_data_manager_stack,
)


def build_sds(
    scope: App, env: Environment, sds_id: str, use_custom_domain: bool = False
):
    """Builds the entire SDS

    Parameters
    ----------
    scope : App
    env : Environment
        Account and region
    sds_id : str
        Name suffix for stack
    use_custom_domain : bool, Optional
        Build API Gateway using custom domain
    """
    open_search = opensearch_stack.OpenSearch(
        scope, f"OpenSearch-{sds_id}", sds_id, env=env
    )

    dynamodb = dynamodb_stack.DynamoDB(
        scope,
        construct_id=f"DynamoDB-{sds_id}",
        sds_id=sds_id,
        table_name=f"imap-data-watcher-{sds_id}",
        partition_key="instrument",
        sort_key="filename",
        env=env,
    )

    s3 = s3_data_buckets_stack.S3DataBuckets(
        scope,
        construct_id=f"S3-Data-Bucket-{sds_id}",
        sds_id=sds_id,
        env=env,
    )

    data_manager = sds_data_manager_stack.SdsDataManager(
        scope, f"SdsDataManager-{sds_id}", sds_id, open_search, dynamodb, s3, env=env
    )

    domain = domain_stack.Domain(
        scope,
        f"DomainStack-{sds_id}",
        sds_id,
        env=env,
        use_custom_domain=use_custom_domain,
    )

    api_gateway_stack.ApiGateway(
        scope,
        f"ApiGateway-{sds_id}",
        sds_id,
        data_manager.lambda_functions,
        env=env,
        hosted_zone=domain.hosted_zone,
        certificate=domain.certificate,
        use_custom_domain=use_custom_domain,
    )


def build_backup(scope: App, env: Environment, sds_id: str, source_account: str):
    """Builds backup bucket with permissions for replication from source_account.

    Parameters
    ----------
    scope : App
    env : Environment
        Account and region
    sds_id : str
        Name suffix for stack
    source_account : str
        Account number for source bucket for replication
    """
    # This is the S3 bucket used by upload_api_lambda
    backup_bucket_stack.BackupBucket(
        scope, f"BackupBucket-{sds_id}", sds_id, env=env, source_account=source_account
    )


def build_s3_data_buckets(scope: App, env: Environment, sds_id: str):
    s3_data_buckets_stack.S3DataBuckets(
        scope,
        construct_id=f"S3-Data-Bucket-{sds_id}",
        sds_id=sds_id,
        env=env,
    )
