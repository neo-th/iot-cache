#!/usr/bin/env python3

import os
import redis
import glob
import argparse
import json

def redisPush(store_name, host='localhost', port=6379, password=None, ssl=False):

    r = redis.Redis(host=host, port=port, password=password, ssl=ssl)

    if not os.path.exists(store_name):
        print(f"Store file {store_name} does not exist")
        return
    
    with open(store_name, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print(f"Error: {store_name} is not a valid JSON file.")
            return
        
    all_pushed = True
    for key, value in data.items():
        if not r.exists(key):
            result = r.set(key, value)
            if not result:
                all_pushed = False
    
    if all_pushed:
        print(f"{store_name} pushed successfully!")
    else:
        print(f"Failed to push {store_name}")

def create_keyValue(key, value, store_name):

    if os.path.exists(store_name):
        with open(store_name, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    
    data[key] = value

    with open(store_name, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Pair add to {store_name}")

def delete_keyValue(key, store_name):
    if not os.path.exists(store_name):
        print(f"Store file {store_name} does not exist.")
        return

    try:
        with open(store_name, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {store_name} is not valid JSON file.")
        return

    if key in data:
        del data[key]
        with open(store_name, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Key deleted from {store_name}!")
    else:
        print(f"Key not found in {store_name}.")

def list_key_stores():

    only_json = glob.glob("*.json")
    print(only_json)

def view_keyValue(key, store_name):

    found = False

    with open(f"{store_name}", "r") as file:
        for line_number, line in enumerate(file, start=1):
            if line.startswith(f"{key}"):
                print(f"{line.split()}")
                found = True
                break
    if not found:
        print("no <Key:Value> found!")

def delete_keyStore(store_name):
    if os.path.exists(store_name):
        os.remove(store_name)
        print("Key store deleted!")
    else:
        print("Key store does not exist!")

def new_keyStore(store_name):
    f = open(f"{store_name}", "x")
    print("Key store created!")

def main():

    parser = argparse.ArgumentParser(description="Local key store cache for IoT devices")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    create_key_parser = subparsers.add_parser('create-key', help='Create <key:value> pair')
    create_key_parser.add_argument('key', type=str, help='Add a key')
    create_key_parser.add_argument('value', type=str, help='Add a value')
    create_key_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    view_key_parser = subparsers.add_parser('view-key', help='View <key:value> pair')
    view_key_parser.add_argument('key', type=str, help='Add a key')
    view_key_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    delete_key_parser = subparsers.add_parser('delete-key', help='Delete <key:value> pair')
    delete_key_parser.add_argument('key', type=str, help='Add a key')
    delete_key_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    key_store_delete_parser = subparsers.add_parser('delete-store', help='Delete key store')
    key_store_delete_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    new_store_parser = subparsers.add_parser('create-store', help='Create key store')
    new_store_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    redis_sync_parser = subparsers.add_parser('redis-sync', help='Sync data from the store file to Redis')
    redis_sync_parser.add_argument('store_name', type=str, help='The store name is a .json file.')
    
    # optional connection parameters
    redis_sync_parser.add_argument('--host', type=str, default='localhost', help='Redis server hostname (default: localhost)')
    redis_sync_parser.add_argument('--port', type=int, default=6379, help='Redis server port (default: 6379)')
    redis_sync_parser.add_argument('--password', type=str, default=None, help='Password for Redis server (default: None)')
    redis_sync_parser.add_argument('--ssl', action='store_true', help='Enable SSL connection to Redis')


    store_list_parser = subparsers.add_parser('store-list', help='This will list all key stores.')

    args = parser.parse_args()

    if args.command == 'create-key':
        create_keyValue(args.key, args.value, args.store_name)
    elif args.command == 'view-key':
        view_keyValue(args.key, args.store_name)
    elif args.command == "delete-key":
        delete_keyValue(args.key, args.store_name)
    elif args.command == 'delete-store':
        delete_keyStore(args.store_name)
    elif args.command == 'create-store':
        new_keyStore(args.store_name)
    elif args.command == 'redis-sync':
        redisPush(args.store_name, host=args.host, port=args.port, password=args.password, ssl=args.ssl)
    elif args.command == 'store-list':
        list_key_stores()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()