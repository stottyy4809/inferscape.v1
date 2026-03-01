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

# --- THE NEW PART: SAVING TO JSON ---
import json # Adding this just in case it isn't at the top of your file

# 1. The list of instances we want to track (mapped to GPU names)
target_instances = {
    "g5.xlarge": "A10",
    "g5.2xlarge": "A10 (Large)",
    "p4de.24xlarge": "A100",
    "p5.48xlarge": "H100"
}

# 2. Create an empty dictionary to hold our results
results_for_website = {}

print("Fetching prices from AWS...")

# 3. Loop through the list and get prices
for inst_id, gpu_name in target_instances.items():
    price = get_instance_price(inst_id)
    
    # Organize the data for the website
    results_for_website[inst_id] = {
        "gpu": gpu_name,
        "price": price
    }
    print(f"Got {inst_id}: {price}")

# 4. THE MAGIC STEP: Save this dictionary as a JSON file
with open('pricing.json', 'w') as f:
    json.dump(results_for_website, f, indent=4)

print("Success! pricing.json has been created.")
