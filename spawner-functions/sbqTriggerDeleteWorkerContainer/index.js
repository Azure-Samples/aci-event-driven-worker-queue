'use strict'

var msRestAzure = require("ms-rest-azure");
var resourceManagement = require('azure-arm-resource');
var containerInstance = require('azure-arm-containerinstance');

var clientId = process.env.client_id,
    secret = process.env.client_secret,
    domain = process.env.tenant,
    subscriptionId = process.env.subscription_id,
    resourceGroupName = process.env.resourceGroup;

module.exports = function(context, mySbMsg) {
    context.log('JavaScript ServiceBus queue trigger function processed message', mySbMsg);
    
    msRestAzure.loginWithServicePrincipalSecret(clientId, secret, domain, function(err, credentials) {
        let client = new containerInstance.ContainerInstanceManagementClient(credentials,subscriptionId);
        let containerGroupName = mySbMsg;

        client.containerGroups.deleteMethod(resourceGroupName, containerGroupName)
            .then( (cgroup) => {
                context.log(cgroup)
            }).catch((err) => {
                context.log(err);
                return;
            });
    });

    context.done();
};