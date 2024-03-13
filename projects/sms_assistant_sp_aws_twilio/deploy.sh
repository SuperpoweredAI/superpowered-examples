#!/bin/bash
set -e

# NOTE: THIS SCRIPT ASSUMES YOU HAVE THE AWS CLI AND SAM CLI INSTALLED AND CONFIGURED
#       ADDITIONALLY, IT WILL USE THE DEFAULT 

export AWS_DEFAULT_REGION=us-east-1

###############################
# PARSE COMMAND LINE ARGUMENTS
###############################
while (( "$#" )); do
  case "$1" in
    --twilio-phone-number)
        TWILIO_PHONE_NUMBER="$2"
        shift 2
        ;;
    --twilio-account-sid)
        twilio_account_sid="$2"
        shift 2
        ;;
    --twilio-auth-token)
        twilio_auth_token="$2"
        shift 2
        ;;
    --sp-api-key-id)
        sp_api_key_id="$2"
        shift 2
        ;;
    --sp-api-key-secret)
        sp_api_key_secret="$2"
        shift 2
        ;;
    -*|--*=) # unsupported flags
        echo "Error: Unsupported flag $1" >&2
        exit 1
        ;;
    *) # preserve positional arguments
        PARAMS="$PARAMS $1"
        shift
        ;;
  esac
done
# set positional arguments in their proper place
eval set -- "$PARAMS"


# set parameter names
TwilioAccountSidParamName=twilio-account-sid
TwilioAuthTokenParamName=twilio-auth-token
SpApiKeyIdParamName=sp-api-key-id
SpApiKeySecretParamName=sp-api-key-secret


# if twilio_phone_number is not set, then exit
if [ -z "$TWILIO_PHONE_NUMBER" ]; then
    echo "Error: Twilio phone number is required" >&2
    exit 1
fi

###############################
# SET SSM PARAMETERS IF THEY WERE PASSED IN
###############################
# if the other parameters are set, create ssm parameters individually
if [ -n "$twilio_account_sid" ]; then
    aws ssm put-parameter --name "$TwilioAccountSidParamName" --value "$twilio_account_sid" --type SecureString --overwrite
fi
if [ -n "$twilio_auth_token" ]; then
    aws ssm put-parameter --name "$TwilioAuthTokenParamName" --value "$twilio_auth_token" --type SecureString --overwrite
fi
if [ -n "$sp_api_key_id" ]; then
    aws ssm put-parameter --name "$SpApiKeyIdParamName" --value "$sp_api_key_id" --type SecureString --overwrite
fi
if [ -n "$sp_api_key_secret" ]; then
    aws ssm put-parameter --name "$SpApiKeySecretParamName" --value "$sp_api_key_secret" --type SecureString --overwrite
fi


###############################
# DEPLOY AWS RESOURCES
###############################
sam build -t resources.yaml --use-container


sam deploy \
    --stack-name sms-assistant \
    --no-confirm-changeset \
    --resolve-s3 \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
        ParameterKey=TwilioAccountSidParamName,ParameterValue=$TwilioAccountSidParamName \
        ParameterKey=TwilioAuthTokenParamName,ParameterValue=$TwilioAuthTokenParamName \
        ParameterKey=SpApiKeyIdParamName,ParameterValue=$SpApiKeyIdParamName \
        ParameterKey=SpApiKeySecretParamName,ParameterValue=$SpApiKeySecretParamName \


###############################
# SET UP TWILIO WEBHOOK
###############################
# first get the output of the stack: RespondToSmsLambdaUrl
respond_to_sms_lambda_url=$(aws cloudformation describe-stacks --stack-name sms-assistant --query "Stacks[0].Outputs[?OutputKey=='RespondToSmsLambdaUrl'].OutputValue" --output text)

# get twilio credentials from ssm with decryption
TWILIO_ACCOUNT_SID=$(aws ssm get-parameter --name "$TwilioAccountSidParamName" --with-decryption --query "Parameter.Value" --output text)
TWILIO_AUTH_TOKEN=$(aws ssm get-parameter --name "$TwilioAuthTokenParamName" --with-decryption --query "Parameter.Value" --output text)

# find the twilio phone number sid
resp=$(curl -s -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/IncomingPhoneNumbers.json" -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN)

sid=$(echo $resp | jq -r '.incoming_phone_numbers[0].sid')

# update the sms webhook url
update_resp=$(curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/IncomingPhoneNumbers/$sid.json" \
 -d "SmsUrl=$respond_to_sms_lambda_url" -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN)

echo "Successfully set the webhooks for $TWILIO_PHONE_NUMBER to $respond_to_sms_lambda_url"