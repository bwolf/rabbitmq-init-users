# rabbitmq-init-users

[`rabbitmq-init-users`](https://github.com/bwolf/rabbitmq-init-users) is a simple init container for [RabbitMQ](https://www.rabbitmq.com) that creates users and their permissions for virtual hosts and topics.

## Container Images
Please find container images on [docker hub](https://hub.docker.com/r/bwolf/rabbitmq-init-users).

## Usage

Define the required environment variables to connect to RabbitMQ:

       RABBITMQ_HOST=localhost
       RABBITMQ_PORT=15672
       RABBITMQ_USERNAME=admin
       RABBITMQ_PASSWORD=ha!

Define which users to be created, separated by `:`:

       REQUIRED_USERS=user1:user2

For each user to be created or updated, define its password, virtual host and topic permissions:

       REQUIRED_USER_USER1_PASSWORD=secret
       REQUIRED_USER_USER1_VHOST_PERMISSIONS='{"configure": ".*", "write": ".*", "read": ".*"}'
       REQUIRED_USER_USER1_TOPIC_PERMISSIONS='{"exchange": "", "write": ".*", "read": ".*"}'

Repeat this for each user. As one can imagine, permissions must be valid JSON.
