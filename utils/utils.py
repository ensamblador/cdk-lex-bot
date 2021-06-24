import json
import boto3
def load_config(conf_file):
    with open (conf_file, 'r') as f:
        cf = json.load(f)
    return cf

def get_params(param_path):
    ssm = boto3.client('ssm')
    params = ssm.get_parameters_by_path(
        Path=param_path,
        Recursive=True
    )['Parameters']
    return params

def get_param(param_name):
    ssm = boto3.client('ssm')
    param = ssm.get_parameter(
        Name=param_name
    )['Parameter']['Value']
    return param