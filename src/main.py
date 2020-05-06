#!/usr/bin/env python3
#
# Simple RabbitMQ init container for creating users and setting up
# their vhost and topic permissions#.

import os
import requests
import json

from dotenv import load_dotenv
from urllib.parse import quote as url_encode


class RabbitApi:

    def __init__(self, host, port, username, password):
        self.__host = host
        self.__port = port
        self.__auth = username, password

    def url(self, resource, *args):
        acc = []
        for a in args:
            acc.append(url_encode(a, safe=''))
        tail = resource.format(*acc)
        return 'http://{}:{}/api/{}'.format(self.__host, self.__port, tail)

    def get_all_usernames(self):
        r = requests.get(self.url('users/'), auth=self.__auth)
        r.raise_for_status()
        users = r.json()
        return list(map(lambda u: u['name'], filter(lambda u: u['name'] != 'admin', users)))

    def create_admin_user(self, name, password):
        body = {'password': password, 'tags': 'administrator'}
        r = requests.put(self.url('users/{}', name), json=body, auth=self.__auth)
        r.raise_for_status()

    def update_admin_user(self, name, password):
        body = {'password': password, 'tags': 'administrator'}
        r = requests.put(self.url('users/{}', name), json=body, auth=self.__auth)
        r.raise_for_status()

    def get_user_vhost_permissions(self, name):
        r = requests.get(self.url('users/{}/permissions', name), auth=self.__auth)
        r.raise_for_status()
        return r.json()

    def set_user_vhost_permission(self, name, vhost, perms):
        r = requests.put(self.url('permissions/{}/{}', vhost, name), json=perms, auth=self.__auth)
        r.raise_for_status()

    def get_topic_permissions(self, name, vhost):
        r = requests.get(self.url('topic-permissions/{}/{}', vhost, name), auth=self.__auth)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return r.json()

    def set_topic_permissions(self, name, vhost, perms):
        r = requests.put(self.url('topic-permissions/{}/{}', vhost, name), json=perms, auth=self.__auth)
        r.raise_for_status()


def getenv(name):
    val = os.getenv(name)
    if val is None or val == '':
        raise ValueError('Expected environment variable {} to be present and non-empty'.format(name))
    return val


def del_lazy(dict_like, *keys):
    for k in keys:
        if k in dict_like:
            del dict_like[k]


def main():
    load_dotenv(verbose=True)

    rabbit = RabbitApi(getenv('RABBITMQ_HOST'),
                       getenv('RABBITMQ_PORT'),
                       getenv('RABBITMQ_USERNAME'),
                       getenv('RABBITMQ_PASSWORD'))

    user_passwd = {}
    vhost_permissions = {}
    topic_permissions = {}

    required_users = getenv('REQUIRED_USERS').split(':')
    print('Required users {}'.format(required_users))
    for u in required_users:
        user = u.upper()
        passwd = getenv('REQUIRED_USER_{}_PASSWORD'.format(user))
        user_passwd[u] = passwd
        vhost_permissions[u] = json.loads(getenv('REQUIRED_USER_{}_VHOST_PERMISSIONS'.format(user)))
        topic_permissions[u] = json.loads(getenv('REQUIRED_USER_{}_TOPIC_PERMISSIONS'.format(user)))

    print('Getting actual users')
    current_users = rabbit.get_all_usernames()
    print('Actual users {}'.format(current_users))

    print('Checking users')
    for u in required_users:
        if u not in current_users:
            print('Creating missing user {}'.format(u))
            rabbit.create_admin_user(u, user_passwd[u])
        else:
            print('Updating user {} password'.format(u))
            rabbit.update_admin_user(u, user_passwd[u])

    print('Checking user vhost permissions')
    for u in required_users:
        expected_perms = vhost_permissions[u]

        # RabbitMQ returns list(dict) where the dict contains
        # additionally the 'user' and 'vhost' key
        actual_perms = rabbit.get_user_vhost_permissions(u)
        if len(actual_perms) == 1:
            ap = actual_perms[0]  # list head
            del_lazy(ap, 'user', 'vhost')
            actual_perms = ap  # flatten

        if actual_perms != expected_perms:
            print('User {} vhost permission {} are not as expected {}'.format(u, actual_perms, expected_perms))
            print('Setting user {} vhost permissions {} on vhost /'.format(u, expected_perms))
            rabbit.set_user_vhost_permission(u, '/', expected_perms)

    print('Checking user topic permissions')
    for u in required_users:
        expected_perms = topic_permissions[u]

        # RabbitMQ returns list(dict) where the dict contains
        # additionally the 'user' and 'vhost' key
        actual_perms = rabbit.get_topic_permissions(u, '/')
        if len(actual_perms) == 1:
            ap = actual_perms[0]  # list head
            del_lazy(ap, 'user', 'vhost')
            actual_perms = ap  # flatten

        if actual_perms != expected_perms:
            print('User {} topic permission {} are not as expected {}'.format(u, actual_perms, expected_perms))
            print('Setting user {} topic permissions {} on vhost /'.format(u, expected_perms))
            rabbit.set_topic_permissions(u, '/', expected_perms)


if __name__ == '__main__':
    main()
