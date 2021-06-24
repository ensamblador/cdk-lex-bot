

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.

import uuid
import json
import boto3

from aws_cdk import (
    core as cdk, 
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    custom_resources as cr
)

from utils.utils import get_param

from aws_cdk.core import CustomResource

STACK_NAME = 'dev'

class CdkLexBotStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        fulfillment_lambda_arn = get_param(f'/ct-manager/{STACK_NAME}/lawyer-bot/abogados-fulfillment-arn')


        on_event_es = _lambda.Function(
            self, "event_es", runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lex_bot/lambda_function.lambda_handler", timeout=cdk.Duration.seconds(300),
            memory_size=1024, code=_lambda.Code.asset("./lambdas"),
            description='[LEX BOT] Custom Resource Provider',
            environment={
                'BOT_FULFILLMENT_LAMBDA_ARN': fulfillment_lambda_arn, 
                'BOT_NAME': 'CT_GET_LAWYER_ES',
                'BOT_JSON_FILE': 'bot_definitions/get-lawyer-es.json'}
            )

        on_event_en = _lambda.Function(
            self, "event_en", runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lex_bot/lambda_function.lambda_handler", timeout=cdk.Duration.seconds(300),
            memory_size=1024, code=_lambda.Code.asset("./lambdas"),
            description='[LEX BOT] Custom Resource Provider',
            environment={
                'BOT_FULFILLMENT_LAMBDA_ARN': fulfillment_lambda_arn, 
                'BOT_NAME': 'CT_GET_LAWYER_EN',
                'BOT_JSON_FILE': 'bot_definitions/get-lawyer-en.json'}
            )

        on_event_es.add_to_role_policy(iam.PolicyStatement(actions=["lex:*"],resources=['*']))
        on_event_en.add_to_role_policy(iam.PolicyStatement(actions=["lex:*"],resources=['*']))

        my_provider_es = cr.Provider(self, "lex_provider_es",on_event_handler=on_event_es, log_retention=logs.RetentionDays.ONE_DAY)
        my_provider_en = cr.Provider(self, "lex_provider_en",on_event_handler=on_event_en, log_retention=logs.RetentionDays.ONE_DAY)

        CustomResource(self, "lexbot_es", service_token=my_provider_es.service_token)
        CustomResource(self, "lexbot_en", service_token=my_provider_en.service_token)