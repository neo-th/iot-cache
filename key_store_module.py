import os
import redis
import glob
import json
import encrypt_value

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
        data["data"][key] = encrypt_value.call_encrypt(value) + encrypt_value.get_hostname()

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

        if "data" in data and key in data["data"]:
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
            return

        encrypted_value = data["data"].get(key, None).split(":")[0]
        
        if encrypted_value is None:
            print("Key not found!")
        try:
            decrypted_value = encrypt_value.call_decrypt(encrypted_value)
            print(decrypted_value)
        except Exception as e:
            print("Decryption failed:", str(e))
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