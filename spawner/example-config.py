from azure.identity import DefaultAzureCredential

class AzureContext(object):
   """Azure Security Context. 

      remarks:
      This is a helper to combine service principal credentials with the subscription id.
      See README for information on how to obtain a service principal attributes client id, secret, etc. for Azure
   """
   
   def __init__(self, subscription_id):
      self.credentials = DefaultAzureCredential()
      self.subscription_id = subscription_id


azure_context = AzureContext(
      subscription_id = '<subId>'
   )

#ACI Specific configurations
ACI_CONFIG = {
    "subscriptionId": "",
    "resourceGroup": "",
    "location": ""
}

#CosmosMongoDb without the ssl
DATABASE_URI = ""

queueConf = {
      'queue_name': '',
      'connstr': ''
}
