import os
import sys
import json
from time import sleep
import botocore


from lex_bot.lex import create_or_update_bot, wait_for_build, delete_bot, wait_for_delete
from crhelper import CfnResource

from shared.logger import get_logger
from shared.client import get_client


logger = get_logger(__name__)
helper = CfnResource(json_logging=True, log_level="INFO")
client = get_client("lex-models")


@helper.create
def create_resource(event, _):
    logger.info ('Creando Resource')
    bot_json_file              = os.environ.get('BOT_JSON_FILE')
    bot_name                   = os.environ.get('BOT_NAME')
    bot_fulfillment_lambda_arn = os.environ.get('BOT_FULFILLMENT_LAMBDA_ARN')

    bot_definition             = json.load(open(bot_json_file))['resource']
    bot_definition['name']     = bot_name

    if "intents" in bot_definition:
        for intent in bot_definition['intents']:
            if intent['fulfillmentActivity']['type'] == 'CodeHook':
                intent['fulfillmentActivity']['codeHook']['uri'] = bot_fulfillment_lambda_arn

    response_create = create_or_update_bot(bot_definition)
    logger.info (response_create)

    bot_version = response_create['version']

    wait_for_build(bot_name, bot_version)

    # Send response to Cloudformation
    helper.Data.update(BotName=bot_name, BotVersion=bot_version)
    return bot_name


@helper.delete
def delete_resource(event, _):
    bot_name = os.environ.get('BOT_NAME')
    try:
        logger.info(event)
        response  = delete_bot(bot_name)
        wait_for_delete(bot_name)
        logger.info(response)
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Failed to delete Bot.")

@helper.update
def update_resource(event, _):
    #delete_resource(event, _)
    #bot_name = os.environ.get('BOT_NAME')
    #wait_for_delete(bot_name)
    create_resource(event, _)

def lambda_handler(event, context):
    helper(event, context)
