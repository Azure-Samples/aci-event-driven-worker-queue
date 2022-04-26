'use strict'

var { ClientSecretCredential } = require("@azure/identity");
var { ContainerInstanceManagementClient } = require("@azure/arm-containerinstance");

var clientId = process.env.client_id,
    secret = process.env.client_secret,
    domain = process.env.tenant,
    subscriptionId = process.env.subscription_id,
    resourceGroupName = process.env.resourceGroup;

module.exports = function(context, mySbMsg) {
    context.log('JavaScript ServiceBus queue trigger function processed message', mySbMsg);
    const credentials = new ClientSecretCredential(domain,clientId,secret);
    let client = new ContainerInstanceManagementClient(credentials,subscriptionId);
    let containerGroupName = mySbMsg;

    client.containerGroups.beginDeleteAndWait(resourceGroupName,containerGroupName)
        .then( (cgroup) => {
            context.log(cgroup)
        }).catch((err) => {
            context.log(err);
            return;
        });

    context.done();
};