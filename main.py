#!/usr/bin/env python3

import argparse
import key_store_module

def main():

    parser = argparse.ArgumentParser(description="Local key store cache for IoT devices")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    create_key_parser = subparsers.add_parser('create-key', help='Create <key:value> pair', description="This command will create a key pair.")
    create_key_parser.add_argument('key', type=str, help='Add a key')
    create_key_parser.add_argument('value', type=str, help='Add a value')
    create_key_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    view_key_parser = subparsers.add_parser('view-key', help='View <key:value> pair', description="This command lets you view the value of the key pair.")
    view_key_parser.add_argument('key', type=str, help='Add a key')
    view_key_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    delete_key_parser = subparsers.add_parser('delete-key', help='Delete <key:value> pair', description="This command will delete a key pair.")
    delete_key_parser.add_argument('key', type=str, help='Add a key')
    delete_key_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    key_store_delete_parser = subparsers.add_parser('delete-store', help='Delete key store', description="This command will delete any valid key store file.")
    key_store_delete_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    new_store_parser = subparsers.add_parser('create-store', help='Create key store', description="This command will create a new key store file.")
    new_store_parser.add_argument('store_name', type=str, help='The store name is a .json file.')

    redis_sync_parser = subparsers.add_parser('redis-sync', help='Sync data from the store file to Redis', description="This command will sync any valid key store file with a redis database.")
    redis_sync_parser.add_argument('store_name', type=str, help='The store name is a .json file.')
    
    redis_sync_parser.add_argument('--host', type=str, default='localhost', help='Redis server hostname (default: localhost)')
    redis_sync_parser.add_argument('--port', type=int, default=6379, help='Redis server port (default: 6379)')
    redis_sync_parser.add_argument('--password', type=str, default=None, help='Password for Redis server (default: None)')
    redis_sync_parser.add_argument('--ssl', action='store_true', help='Enable SSL connection to Redis')
    redis_sync_parser.add_argument('--overwrite', action='store_true', help='If keys are changed and need to be overwritten ')

    store_list_parser = subparsers.add_parser('store-list', help='This will list all key stores.', description='This command lists all valid key store files in the current directory.')

    args = parser.parse_args()

    commands = {
        'create-key': lambda args: key_store_module.create_keyValue(args.key, args.value, args.store_name),
        'view-key': lambda args: key_store_module.view_keyValue(args.key, args.store_name),
        'delete-key': lambda args: key_store_module.delete_keyValue(args.key, args.store_name),
        'delete-store': lambda args: key_store_module.delete_keyStore(args.store_name),
        'create-store': lambda args: key_store_module.new_keyStore(args.store_name),
        'redis-sync': lambda args: key_store_module.redisPush(
            args.store_name, 
            host=args.host, 
            port=args.port, 
            password=args.password, 
            ssl=args.ssl, 
            overwrite=args.overwrite
        ),
        'store-list': lambda args: key_store_module.list_key_stores()
    }

    command = commands.get(args.command, lambda _: parser.print_help())
    command(args)

if __name__ == '__main__':
    main()