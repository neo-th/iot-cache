#!/usr/bin/env python3

import os
import redis
import glob
import argparse
import json

def redisPush(store_name, host='localhost', port=6379, password=None, ssl=False, overwrite=False):

    r = redis.Redis(host=host, port=port, password=password, ssl=ssl)

    if not os.path.exists(store_name):
        print(f"Store file {store_name} does not exist")
        return
    
    if not is_key_store_file(store_name):
        print("Invalid key store file!")
    else:
        with open(store_name, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(f"Error: {store_name} is not a valid JSON file.")
                return
          
        all_pushed = True
        for key, value in data["data"].items():
            if not r.exists(key) or overwrite:
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

    if "data" not in data:
        data["data"] = {}

    if is_key_store_file(store_name):
        data["data"][key] = value

        with open(store_name, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Pair add to {store_name}")
    else:
        print("Invalid key store file!")

def delete_keyValue(key, store_name):

    if not os.path.exists(store_name):
        print(f"Store file {store_name} does not exist.")
        return

    if is_key_store_file(store_name):
        try:
            with open(store_name, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {store_name} is not valid JSON file.")
            return

        if key in data:
            del data["data"][key]
            with open(store_name, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Key deleted from {store_name}!")
        else:
            print(f"Key not found in {store_name}.")
    else:
        print(f"{store_name} is not a valid key store file.")

def list_key_stores():
    
    only_json = glob.glob("*.json")

    if not only_json:
        print("No JSON files found in current directory.")
        return

    valid_files = [i for i in only_json if is_key_store_file(i)]

    if valid_files:
        print("Valid key store files:")
        for i in sorted(valid_files):
            print(f"- {i}")
    else:
        print("No valid key store files found.")

def is_key_store_file(store_name):

    try:
        with open(store_name, "r") as f:
            data = json.load(f)
            return data.get("__tag__") == "--key-store--"
    except json.JSONDecodeError:
        return False

def view_keyValue(key, store_name):

    if not os.path.exists(store_name):
        print(f"Store file {store_name} does not exist.")
        return

    if is_key_store_file(store_name):
        try:
            with open(store_name, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {store_name} is not a valid JSON file.")

        print(data["data"].get(key, "Key not found!"))
    else:
        print("Invalid key store file!")

def delete_keyStore(store_name):

    if is_key_store_file(store_name):
        if os.path.exists(store_name):
            os.remove(store_name)
            print("Key store deleted!")
        else:
            print("Key store does not exist!")
    else:
        if not os.path.exists(store_name):
            print("Key store does not exists")
        else:
            print("Invalid key store file!")

def new_keyStore(store_name):
    
    if os.path.exists(store_name):
        print("File exists!")
    else:
        open(store_name, "x")

        data = {}
        data["__tag__"] = "--key-store--"

        data["data"] = {}

        with open(store_name, "w") as file:
            json.dump(data, file, indent=4)
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
    
    redis_sync_parser.add_argument('--host', type=str, default='localhost', help='Redis server hostname (default: localhost)')
    redis_sync_parser.add_argument('--port', type=int, default=6379, help='Redis server port (default: 6379)')
    redis_sync_parser.add_argument('--password', type=str, default=None, help='Password for Redis server (default: None)')
    redis_sync_parser.add_argument('--ssl', action='store_true', help='Enable SSL connection to Redis')
    redis_sync_parser.add_argument('--overwrite', action='store_true', help='If keys are changed and need to be overwritten ')

    store_list_parser = subparsers.add_parser('store-list', help='This will list all key stores.')

    args = parser.parse_args()

    commands = {
        'create-key': lambda args: create_keyValue(args.key, args.value, args.store_name),
        'view-key': lambda args: view_keyValue(args.key, args.store_name),
        'delete-key': lambda args: delete_keyValue(args.key, args.store_name),
        'delete-store': lambda args: delete_keyStore(args.store_name),
        'create-store': lambda args: new_keyStore(args.store_name),
        'redis-sync': lambda args: redisPush(
            args.store_name, 
            host=args.host, 
            port=args.port, 
            password=args.password, 
            ssl=args.ssl, 
            overwrite=args.overwrite
        ),
        'store-list': lambda args: list_key_stores()
    }

    command = commands.get(args.command, lambda _: parser.print_help())
    command(args)

if __name__ == '__main__':
    main()