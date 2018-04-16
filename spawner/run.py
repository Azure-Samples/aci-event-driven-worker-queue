#!/usr/bin/env python

import random
import string
import sys
from collections import deque
from config.config import queueConf, azure_context, DATABASE_URI, ACI_CONFIG
from azure.servicebus import ServiceBusService, Message, Queue
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup, Container, ContainerPort, Port, IpAddress, EnvironmentVariable,
                                                 ResourceRequirements, ResourceRequests, ContainerGroupNetworkProtocol, OperatingSystemTypes)

resource_client = ResourceManagementClient(azure_context.credentials, azure_context.subscription_id)
client = ContainerInstanceManagementClient(azure_context.credentials, azure_context.subscription_id)


bus_service = ServiceBusService(
    service_namespace = queueConf['service_namespace'],
    shared_access_key_name = queueConf['saskey_name'],
    shared_access_key_value = queueConf['saskey_value'])



BASE_NAMES = deque(["anders", "wenjun", "robbie", "robin", "allen", "tony", "xiaofeng", "tingting", "harry", "chen"])
NAMES_COUNTER = 0
IMAGE = "pskreter/worker-container:latest"


def main():
    sys.stdout.write("Starting Work Cycle...\n")  # same as print
    sys.stdout.flush()
    while True:
        try:
            msg = bus_service.receive_queue_message(queueConf['queue_name'], peek_lock=False)
            if msg.body is not None:
                work = msg.body.decode("utf-8")

                container_name = get_container_name()
                env_vars = create_env_vars(work, DATABASE_URI, container_name)
                sys.stdout.write("Creating container: " + container_name + " with work: " + work + '\n')  # same as print
                sys.stdout.flush()
                create_container_group(ACI_CONFIG['resourceGroup'], container_name, ACI_CONFIG['location'], IMAGE, env_vars)
                
        except KeyboardInterrupt:
            pass


def create_env_vars(msg, database_uri, container_name):
    msg_var = EnvironmentVariable(name = "MESSAGE", value = msg)
    database_var = EnvironmentVariable(name = "DATABASE_URI", value = database_uri)
    container_name_var = EnvironmentVariable(name = "CONTAINER_NAME", value = container_name)

    return [msg_var, database_var, container_name_var]


def get_container_name():
    random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(7))
    name = BASE_NAMES.popleft()
    BASE_NAMES.append(name)
    return name + "-" + random_string


def create_container_group(resource_group_name, name, location, image, env_vars):

    # setup default values
    port = 80
    container_resource_requirements = None
    command = None

    # set memory and cpu
    container_resource_requests = ResourceRequests(memory_in_gb = 3.5, cpu = 2)
    container_resource_requirements = ResourceRequirements(requests = container_resource_requests)

    container = Container(name = name,
                        image = image,
                        resources = container_resource_requirements,
                        command = command,
                        ports = [ContainerPort(port=port)],
                        environment_variables = env_vars)

    # defaults for container group
    cgroup_os_type = OperatingSystemTypes.linux
    cgroup_ip_address = IpAddress(ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port = port)])
    image_registry_credentials = None

    cgroup = ContainerGroup(location = location,
                        containers = [container],
                        os_type = cgroup_os_type,
                        ip_address = cgroup_ip_address,
                        image_registry_credentials = image_registry_credentials)

    client.container_groups.create_or_update(resource_group_name, name, cgroup)


if __name__ == '__main__':
    main()
