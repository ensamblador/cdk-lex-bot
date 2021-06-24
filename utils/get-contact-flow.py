import argparse
import boto3
import json

parser = argparse.ArgumentParser(description='lee el contact flow ID y lo guarda en un archivo json')
parser.add_argument('instanceAlias', help='alias de la isntancia')
parser.add_argument('contactFlowName', help='Nombre del contact Flow')
parser.add_argument('region', default='us-east-1', nargs='?', help='Dynamo db region name (default=us-east-1')
parser.add_argument('profile', default='default', help='Profile a utilizar (default=default)')
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
client = session.client('connect', region_name=args.region)


instances = client.list_instances()['InstanceSummaryList']

for instance in instances:

    if instance['InstanceAlias'] == args.instanceAlias:
        instance_id = instance['Id']
        print ('Instance', args.instanceAlias, 'encontrada id:', instance_id)
        contact_flows = client.list_contact_flows(InstanceId=instance_id,
            ContactFlowTypes=['CONTACT_FLOW','CUSTOMER_QUEUE','CUSTOMER_HOLD',
            'CUSTOMER_WHISPER','AGENT_HOLD','AGENT_WHISPER','OUTBOUND_WHISPER',
            'AGENT_TRANSFER','QUEUE_TRANSFER'])['ContactFlowSummaryList']
        
        for contact_flow in contact_flows:
            cf_name = contact_flow['Name']
            if cf_name == args.contactFlowName:
                print('contact flow', cf_name, 'encontrado id:',contact_flow['Id'])
                cf = client.describe_contact_flow(InstanceId=instance['Id'],
                ContactFlowId=contact_flow['Id'])
                print ('escribiendo archivo {}.json'.format(cf_name))
                with open ('{}.json'.format(cf_name), 'w') as f:
                    json.dump(json.loads(cf['ContactFlow']['Content']), f)

                    print ('finalizado!')
                    exit(1)
        
        print('no se encontró contact flow {} en instance {}'.format(args.contactFlowName,args.instanceAlias))
    

print('no se encontró instancia ', args.instanceAlias)

