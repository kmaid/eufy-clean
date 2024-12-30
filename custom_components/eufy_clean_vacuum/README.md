# eufy-clean

Python library for controlling Eufy robot vacuums. This is a port of the TypeScript library.

## Installation

```bash
# Using poetry (recommended)
poetry add eufy-clean

# Using pip
pip install eufy-clean
```

## Usage

```python
import asyncio
from .eufy_clean import EufyClean

async def main():
    # Initialize with your Eufy account credentials
    eufy = EufyClean(
        username="your.email@example.com",
        password="your-password"
    )

    # Initialize connection
    await eufy.init()

    # Get list of devices
    devices = await eufy.get_mqtt_devices()
    print("Found devices:", devices)

    # Initialize a specific device
    device = await eufy.init_device({
        "device_id": "your-device-id",
        "auto_update": True,  # Optional: automatically update device state
        "debug": True  # Optional: enable debug logging
    })

    if device:
        # Start auto cleaning
        await device.auto_clean()

        # Get battery level
        battery = await device.get_battery_level()
        print(f"Battery level: {battery}%")

        # Set cleaning speed
        await device.set_clean_speed("STANDARD")  # Options: QUIET, STANDARD, TURBO, MAX

        # Send robot home
        await device.go_home()

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Control Eufy robot vacuums via cloud and MQTT connections
- Support for all major Eufy RoboVac models
- Comprehensive control over cleaning operations:
  - Auto cleaning
  - Room cleaning
  - Spot cleaning
  - Manual control
  - Setting cleaning parameters
- Monitor device status:
  - Battery level
  - Cleaning state
  - Error codes
  - Work mode

## Supported Models

The library supports a wide range of Eufy RoboVac models, including:

- RoboVac X Series (X8, X8 Hybrid, X8 Pro, X9 Pro, X10 Pro Omni)
- RoboVac G Series (G20, G30, G40, etc.)
- RoboVac L Series (L60, L70 Hybrid)
- RoboVac C Series (30C, 35C, etc.)
- RoboVac S Series (11S)

For a complete list of supported models, see the `constants/devices.py` file.

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/eufy-clean.git
cd eufy-clean

# Install dependencies
poetry install

# Run tests
poetry run pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
