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

#Service Principle Creds for ACI
azure_context = AzureContext(
      subscription_id = ''
   )

#ACI Specific configurations
ACI_CONFIG = {
    "subscriptionId": "",
    "resourceGroup": "",
    "location": ""
}

#Cosmosdb mongodb api connection string
DATABASE_URI = "" 

#Service Bus Queue Config
queueConf = {
      'queue_name': '',
      'connstr': ''
}
