import sys 
from time import sleep
import botocore

sys.path.append("..")


from shared.client import get_client
from shared.logger import get_logger


client = get_client("lex-models")
logger = get_logger(__name__)


def wait_for_build(bot_name, bot_version):
    response = client.get_bot(name=bot_name,versionOrAlias=bot_version)
    bot_status = response['status']
    
    while bot_status == "BUILDING":
        sleep(1)
        response = client.get_bot(name=bot_name,versionOrAlias=bot_version)
        bot_status = response["status"]

    if "READY" not in bot_status:
        logger.error(response)
        raise RuntimeError("Failed to create Lex bot.")

def bot_exist(bot_list, bot_name):
    for bot in bot_list:
        if bot['name'] == bot_name:
            return True
    return False


def wait_for_delete(bot_name):
    response = client.get_bots(nameContains=bot_name)
    exist = bot_exist(response['bots'], bot_name)
    while exist:
        sleep(1)
        response = client.get_bots(nameContains=bot_name)
        exist = bot_exist(response['bots'], bot_name)


def get_slot_type_version(slot_name):
    response = client.get_slot_types(nameContains=slot_name)
    for slot_type in response['slotTypes']:
        if slot_type['name'] == slot_name:
            return slot_type['version']
    return None

def get_slot_type(slot_name):
    slot_version = get_slot_type_version(slot_name)
    if slot_version:
        return client.get_slot_type(name=slot_name,version=slot_version)
    
    return None    


def get_intent_version(intent_name):
    response = client.get_intent_versions(name=intent_name)
    for intent in response['intents']:
        if intent['name'] == intent_name:
            return intent['version']
    return None

def get_intent(intent_name):
    intent_version = get_intent_version(intent_name)
    if intent_version:
        return client.get_intent(name=intent_name,version=intent_version)
    
    return None    


def get_bot_version(bot_name):
    response = client.get_bot_versions(name=bot_name)
    for bot in response['bots']:
        if bot['name'] == bot_name:
            return bot['version']
    return None

def get_bot(bot_name):
    bot_version = get_bot_version(bot_name)
    if bot_version:
        return client.get_bot(name=bot_name,versionOrAlias=bot_version)
    
    return None    

def create_or_update_slot_type(slot_name, slot_description, slot_values):

    params = dict (
        name=slot_name,
        description=slot_description,
        enumerationValues=slot_values,
        valueSelectionStrategy='ORIGINAL_VALUE'
    )
    existing_slot = get_slot_type(slot_name)

    if existing_slot:
        params['checksum'] = existing_slot['checksum']
    create_slot_type_response = client.put_slot_type(**params)
    return create_slot_type_response


def create_or_update_intent(
    intent_name, intent_description, 
    intent_slots, sample_utterances, 
    confirmation_prompt, rejection_statement, conclusion_statement, fulfillment_activity ):

    params = dict (
        name = intent_name,
        description = intent_description,
        slots = intent_slots,
        sampleUtterances = sample_utterances,
        fulfillmentActivity= fulfillment_activity
    )

    existing_intent = get_intent(intent_name)
    #print(existing_intent)

    if existing_intent:
        params['checksum'] = existing_intent['checksum']

    if confirmation_prompt:
        params['confirmationPrompt'] =  confirmation_prompt

    if rejection_statement:
        params['rejectionStatement'] =  rejection_statement


    if conclusion_statement:
        params['conclusionStatement'] =  conclusion_statement

    #print(params)
    create_intent_response = client.put_intent(**params)

    return create_intent_response

def delete_bot(bot_name):
    logger = get_logger(__name__)
    logger.info (f'borrando bot: {bot_name}')
    response = client.delete_bot(name=bot_name)
    logger.info(response)
    return response


def create_or_update_bot(bot_json):
    logger = get_logger(__name__)

    if "slotTypes" in bot_json:
        for slot_type in bot_json['slotTypes']:
            logger.info ('Creando Slot Type')
            res = create_or_update_slot_type(slot_type['name'],slot_type['description'], slot_type['enumerationValues'])
            logger.info(res)

    intents = []

    if "intents" in bot_json:
        for intent in bot_json['intents']:
            logger.info ('Creando Intent')
            intent_description = intent['description'] if 'description' in intent else 'Intent description'
            confirmation_prompt =  intent['confirmationPrompt'] if 'confirmationPrompt' in intent else None
            rejection_statement =  intent['rejectionStatement'] if 'rejectionStatement' in intent else None
            conclusion_statement = intent['conclusionStatement'] if 'conclusionStatement' in intent else None

            res =  create_or_update_intent(
                intent['name'], intent_description, 
                intent['slots'], intent['sampleUtterances'],
                confirmation_prompt, rejection_statement,conclusion_statement, 
                intent['fulfillmentActivity']
            )
            logger.info(res)
            intents.append({'intentName': res['name'], 'intentVersion':  res['version']})
    
    
    bot_description = bot_json['description'] if 'description' in bot_json else 'Bot description'

    existing_bot = get_bot(bot_json['name'])

    params = dict (
        name=bot_json['name'],
        description=bot_description,
        intents=intents,
        enableModelImprovements=bot_json['enableModelImprovements'],
        clarificationPrompt = bot_json['clarificationPrompt'],
        abortStatement=bot_json['abortStatement'],
        idleSessionTTLInSeconds=bot_json['idleSessionTTLInSeconds'],
        voiceId=bot_json['voiceId'],
        locale=bot_json['locale'],
        childDirected=bot_json['childDirected'],
        detectSentiment=bot_json['detectSentiment']
    )

    if existing_bot:
        params['checksum'] = existing_bot['checksum']

    put_bot_response = client.put_bot(**params)

    return put_bot_response

        