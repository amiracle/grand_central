import sys
import os
import csv
import json
directory = sys.argv[1]
all_creds = [
    {
        'credentials': []
    }
]
credential_csv_mapping = {'User name': 'name', 'Access key ID': 'key_id', 'Secret access key': 'secret_key'}
for subdir, dirs, files in os.walk(directory):
    for file in files:
        f = open(os.path.join(subdir, file), 'r')
        data = f.readlines()
        f.close()
        credential_json = {
            'name': '', 
            'key_id': '', 
            'secret_key': '', 
            'category': '1'
        }
        if len(data) > 1:
            keys = data[0].split(',')
            values = data[1].split(',')
            for i, key in enumerate(keys):
                key = key.rstrip()
                if key in credential_csv_mapping:
                    json_key = credential_csv_mapping[key].rstrip()
                    credential_json[json_key] = values[i].rstrip()
            all_creds[0]['credentials'].append(credential_json)
f = open('all_account_credentials.json', 'w')
f.write(json.dumps(all_creds))
f.close()
