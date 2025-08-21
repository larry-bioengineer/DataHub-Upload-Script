import requests

from pymodbus.client import ModbusTcpClient
import dotenv
import os
import csv

dotenv.load_dotenv()

SERVER_URL = os.getenv("CLOUD_ENDPOINT")

"""
You will have to be in the same network as the gateway 
update the host based on Lora app 
"""

# Replace with your gateway's IP and port
client = ModbusTcpClient(host='192.168.1.130', port=502)  

if not client.connect():
    print("Failed to connect to Modbus TCP server.")
    exit(1)

# Modbus TCP usually uses the same register map as Modbus RTU
# unit_id = 1  # Device ID, check your gateway's settings
unit_id = 0
# register_address = 102
register_address = 1499  # temperature
# register_address = 1599  # humidity
# register_address = 1699  # battery 

def read_data(register_address):
    result = client.read_holding_registers(
        address=register_address,
        count=5,
        device_id=unit_id
    )

    if not result.isError():
        print(result)
        raw_temp = result.registers[1]
        if register_address == 1499:
            temperature = raw_temp / 100.0
            print(f"Current temperature: {temperature:.2f}°C")
            return temperature
        elif register_address == 1599:
            humidity = raw_temp / 10.0
            print(f"Current humidity: {humidity:.2f}%")
            return humidity
        elif register_address == 1699:
            battery = raw_temp / 1000.0
            print(f"Current battery: {battery:.2f}V")
            return battery
    else:
        print("Error reading register:", result)

client.close()

# send data to server


with open('upload_endpoints.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)

        resp = requests.post(
            url=f"{row['endpoint']}",
            json={
                row['field']: read_data(int(row['register_address'])),
            },
            headers = {
                "Authorization": f"Bearer {row['jwt']}"
            }
        )

        if resp.status_code == 200:
            print("Data sent successfully")
        else:
            print("Failed to send data")