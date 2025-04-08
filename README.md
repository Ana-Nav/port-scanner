# port-scanner
Simple port scanner that implements multithreading for faster scanning. Connects to ports in IPv4 addresses using TCP. The script will output open port numbers and their corresponding service. You can choose to save the output to a file.

## Installation
1. Clone this project:
```bash
git clone https://github.com/Ana-Nav/port-scanner
```
2. Ensure you have Python 3 installed on your system.
3. Run the script:
```bash
python3 port_scanner.py
```
## Usage
The script will prompt you to enter target IP addresses and ports to scan.

**Addresses:**
* Single address: `192.168.1.x`
* Multiple addresses: `192.168.1.x,192.168.1.x,192.168.1.x`
* Subnet: `192.168.1.0/24`

**Ports:**
* Single port: `80`
* Multiple ports: `22,80,443`
* Port range: `0-1023`

## Configuration
Each thread handles the scan of a different IP address. You can adjust the `workers` variable at the top of the script to control the maximum number of threads, along with the `timeout` value, which controls how long the script will wait for a response from a port before moving on to the next port.

Choosing a short timeout will make the script faster but may move on from ports that are open but slow to respond. Maximum thread amount will also impact performance: a value too high may use too many resources and make the script slower. The ideal amount of threads will depend on your system.

## Disclaimer
This project is intended for educational purposes. Do not use this tool to scan networks or systems without permission.