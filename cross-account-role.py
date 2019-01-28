import boto3
from botocore.exceptions import ClientError


screts_client = boto3.client('secretsmanager',)


def get_temp_credentials_using_sts_through_ec2_iam_role(cross_account_role):
    """
    returns temporary credentials by caling STS.
    """
    sts_client = boto3.client('sts')
    temp_credentials = sts_client.assume_role(
        RoleArn=cross_account_role,
        DurationSeconds=3600,
        RoleSessionName="userOrAppName"
    )

    return temp_credentials

def get_credentials_from_secrets_manager_in_different_account_using_temp_credentials(temp_iam_credentials):
    """
    returns credentials stored in secrets manager.
    temp_iam_credentials: temporary credentials from STS
    """
    secrets_client = boto3.client('secretsmanager',
        aws_access_key_id = temp_iam_credentials["Credentials"]["AccessKeyId"],
        aws_secret_access_key = temp_iam_credentials["Credentials"]["SecretAccessKey"],
        aws_session_token = temp_iam_credentials["Credentials"]["SessionToken"],
        )
    
    db_credentials = secrets_client.get_secret_value(
            SecretId="sample-secret"
        )
    
    return db_credentials

def get_credentials_from_secrets_manager_in_current_account():
    """
    returns credentials stored in secrets manager.
    Credentials are automatically fetched from IAM role attached to EC2 instance
    """
    secrets_client = boto3.client('secretsmanager')
    
    db_credentials = secrets_client.get_secret_value(
            SecretId="mysql-rds-access"
        )
    
    return db_credentials

    
def main():
    
    print("\nDB credentials in secrets manager in current account\n")
    
    db_creds_in_same_account = get_credentials_from_secrets_manager_in_current_account()
    print(db_creds_in_same_account)

    print("\nDB credentials in secrets manager in different account\n")
    
    # This role must be defined in the other account and must trust the account from which 
    # this program is being run
    cross_account_role = 'arn:aws:iam::460424022147:role/org-master-account-role'

    temp_iam_credentials = get_temp_credentials_using_sts_through_ec2_iam_role(cross_account_role)

    db_creds_in_different_account = get_credentials_from_secrets_manager_in_different_account_using_temp_credentials(temp_iam_credentials)
    print(db_creds_in_different_account)

    


if __name__ == "__main__":
    main()