import asyncio
import os
from dotenv import load_dotenv
from eufy_clean import EufyClean
import json
# Load environment variables from .env file
load_dotenv()

if not os.getenv('EUFY_EMAIL') or not os.getenv('EUFY_PASSWORD'):
    raise ValueError("EUFY_EMAIL and EUFY_PASSWORD must be set in .env file")

async def main():
    eufy_clean = EufyClean(
        username=os.getenv('EUFY_EMAIL'),
        password=os.getenv('EUFY_PASSWORD')
    )

    await eufy_clean.init()

    # Get all devices
    devices = await eufy_clean.get_mqtt_devices()
    print("Found devices:", json.dumps(devices, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
