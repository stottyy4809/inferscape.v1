import os
import boto3
import json

# This tells Python to go look in the secure GitHub environment for these values
ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

def get_instance_price(instance_name):
    """
    This is our 'Worker' function. It takes one instance name 
    and returns just the price as a string.
    """
    client = boto3.client(
        'pricing', 
        region_name='us-east-1',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    filters = [
        {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_name},
        {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'EU (Frankfurt)'},
        {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
        {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
        {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'}
    ]

    try:
        response = client.get_products(ServiceCode='AmazonEC2', Filters=filters)
        if not response['PriceList']:
            return "N/A"

        price_item = json.loads(response['PriceList'][0])
        on_demand = price_item['terms']['OnDemand']
        id1 = list(on_demand.keys())[0]
        id2 = list(on_demand[id1]['priceDimensions'].keys())[0]
        price = on_demand[id1]['priceDimensions'][id2]['pricePerUnit']['USD']
        
        return f"${float(price):.2f}"
    except Exception:
        return "Error"

# --- THE NEW PART: THE LIST & THE LOOP ---

# 1. Create a list of all instances you want to check
target_instances = ["g5.xlarge", "g5.2xlarge", "p4de.24xlarge", "p5.48xlarge"]

print(f"{'Instance':<15} | {'Price/hr (Frankfurt)':<20}")
print("-" * 40)

# 2. Loop through the list and call our function for each one
for instance in target_instances:
    price = get_instance_price(instance)
    print(f"{instance:<15} | {price:<20}")