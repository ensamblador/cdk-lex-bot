import json
def valida_instancia(client, instance_id):
    response = client.list_instances()
    instances = response['InstanceSummaryList']
    found = False
    for inst in instances:
        if inst['Id'].split('/')[-1] == instance_id:
            
            found = True

    return found

def valida_telefono(client, instance_id, telefono):
    response = client.list_phone_numbers(InstanceId=instance_id)
    numeros = response['PhoneNumberSummaryList']
    found = False
    for num in numeros:
        if num['PhoneNumber'] == telefono:
            
            found = True
    return found

def create_contact_flow(client, file_name, instance_id):
    name = file_name.split('/')[-1].split('.')[0]
    with open (file_name, 'r') as f:
        cf = json.load(f)
        
    response = client.list_contact_flows(InstanceId=instance_id,ContactFlowTypes=['CONTACT_FLOW'])
    contact_flows = response['ContactFlowSummaryList']
    found = False

    for contact_flow in contact_flows:
        if contact_flow['Name']== name:
            found = True
            print ('Ya existe contact flow {}. Actualizando contenido.'.format(name))
            update = client.update_contact_flow_content(
                InstanceId=instance_id,
                ContactFlowId=contact_flow['Id'],
                Content=json.dumps(cf))

    if not found:
        print ('No existe contact flow {}. Creando.'.format(name))
        try:
            create_response = client.create_contact_flow(
                InstanceId=instance_id,
                Name=name,
                Type='CONTACT_FLOW',
                Description='Flujo para smart contact',
                Content=json.dumps(cf),
                Tags={
                    'APP': 'SMART-CONTACT'
                }
            )
        except Exception as e:
            print(e)

def get_connect_bucket(client, instance_id):
    CONNECT_BUCKET = None

    cl_attr =client.describe_instance_attribute(
        InstanceId=instance_id,
        AttributeType='CONTACT_LENS'
    )
    if cl_attr['Attribute']['Value'] == 'true':
        storage_config = client.list_instance_storage_configs(
        InstanceId=instance_id,
        ResourceType='CALL_RECORDINGS'
        )
        s3_config = storage_config['StorageConfigs'][0]['S3Config']

        CONNECT_BUCKET = {
            'BUCKET_NAME': s3_config['BucketName'],
            'BUCKET_PREFIX': s3_config['BucketPrefix']
        }
    print ('Connect Bucket:', CONNECT_BUCKET)
    return CONNECT_BUCKET

def super_title(text):
    largo=len(text)
    print('='*(10+largo))
    print('====={}====='.format(text))
    print('='*(10+largo))

def find_instance_id(client, instance_alias):
    instance_id = None
    instances = client.list_instances()['InstanceSummaryList']
    for instance in instances:
        if instance['InstanceAlias'] == instance_alias:
            instance_id = instance['Id']
            print ('  {}:{} encontrado ;)'.format(instance_alias,instance_id))
            break
    return instance_id

def find_source_phone(client, instance_id):
    response = client.list_phone_numbers(
        InstanceId=instance_id
    )
    numeros = response['PhoneNumberSummaryList']
    for num in numeros:
        print ('  Country:{} Número:{} ({})'.format(num['PhoneNumberCountryCode'], num['PhoneNumber'], num['PhoneNumberType']))
    
    return numeros


def find_prompt_arn(client, instance_id, prompt_name):
    prompts= client.list_prompts(InstanceId = instance_id)['PromptSummaryList']

    for prompt in prompts:
        if prompt['Name'] == prompt_name:
            print('  Prompt {}=>{}'.format(prompt_name, prompt['Arn']))
            return prompt['Arn']
    return None


def find_agent_arn(client, instance_id, agent_name):
    usuarios_connect = client.list_users(InstanceId=instance_id)['UserSummaryList']
    for u in usuarios_connect:
        if u['Username'] == agent_name:
            print('  Usuario por defecto {}=>{}'.format(agent_name, u['Arn']))
            return u['Arn']
    
    return None


def get_agent_data(client, instance_id, agent_id):
    return client.describe_user(UserId=agent_id, InstanceId=instance_id)['User']


