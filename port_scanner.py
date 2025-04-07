import socket
import ipaddress
from os import path
import re
from concurrent.futures import ThreadPoolExecutor

# time the socket will wait for a response from a port before moving on to the next port
timeout: float = 0.5

# maximum amount of threads
workers: int = 120

# check if user input for target address is valid
while True:
    input_addresses: str = input("""
Enter IP addresses to scan in one of the following formats:
    Single address: 192.168.1.x
    Multiple addresses: 192.168.1.x,192.168.1.x,192.168.1.x
    Subnet: 192.168.1.0/24
""").replace(" ","")
    
    # check if user input for subnet is valid
    if "/" in input_addresses:
        try:
            ipaddress.ip_network(input_addresses)
            break
        except:
            print("[ Invalid subnet ]")

    # check if user input for list of addresses is valid
    elif "," in input_addresses:
        addr_list = input_addresses.split(",")
        try:
            for addr in addr_list:
                ipaddress.ip_address(addr)
            break
        except:
            print("[ Invalid address list ]")
    
    # check if user input for single address is valid
    else:
        try:
            ipaddress.ip_address(input_addresses)
            break
        except:
            print("[ Invalid address ]")

# check if user input for target ports is valid
while True:
    input_ports: str = input("""
Enter ports to scan in one of the following formats:
    Single port: 80
    Multiple ports: 22,80,443
    Port range: 0-1023
""").replace(" ","")
    
    if "," in input_ports:
        list_pattern = "([0-9]+,[0-9]*)+"
        port_list = re.fullmatch(list_pattern, input_ports)

        if port_list:
            break
        else:
            print("[ Invalid port list ]")

    elif "-" in input_ports:
        range_pattern = "[0-9]+-[0-9]+"
        port_range = re.fullmatch(range_pattern, input_ports)

        if port_range:
            break
        else:
            print("[ Invalid port range ]")

    else:
        int_pattern = "[0-9]+"
        port_int = re.fullmatch(int_pattern, input_ports)

        if port_int:
            break
        else:
            print("[ Invalid port ]")

output: str = input("Save output to file? (y/n): ").lower()

if output == "y" or output == "yes":
    file: str = input("Enter file name without extension: ")
    filename: str = file + ".txt"

# generate a list containing target ip addresses
def retrieve_input_addresses(target: str) -> list: 
    address_list = []

    if "/" in target:
        for addr in ipaddress.IPv4Network(target):
            address_list.append(str(addr))

    else:
        address_list = target.split(",")

    return address_list

# generate list containing target ports
def retrieve_input_ports(target: str) -> list:

    # turn input into range and generate a list from the range
    if "-" in target:
        num_range = target.split("-")
        ports_int = list(map(int, num_range))
        port_range = range(ports_int[0], ports_int[1] + 1)

        port_list = list(port_range)
    
    else:
        port_list = target.split(",")

        # if user input for ports ends with a comma, an empty list element is created
        # the following line erases that element
        if port_list[-1] == "":
            del port_list[-1]

        # turn list elements into integers
        port_list = list(map(int, port_list))
    
    return port_list

target_addresses: list = retrieve_input_addresses(input_addresses)
target_ports: list = retrieve_input_ports(input_ports)

# scan a single address for ports in the list
def scan_ports(address: str, ports: list) -> list:
    open_ports = []

    for port in ports:

        # create socket object that can connect with IPv4 addresses using TCP
        scanner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (address, port)

        # if a connection is established, the port is open
        try:
            scanner.settimeout(timeout)
            scanner.connect(addr)
            
            # add port details to list of open ports
            service = socket.getservbyport(port, "tcp")
            open_ports.append(f"{address} \t{port} \t{service}")
           
            # close connection before using socket on another connection
            scanner.close()
        
        # handle errors caused by closed ports
        except ConnectionRefusedError:
            pass

        except TimeoutError:
            pass

        except OSError:
            pass

    return open_ports

def start_scan(addresses: list) -> list:
    scan_results = []

    # create a pool of threads that will handle different scans
    with ThreadPoolExecutor(max_workers=workers) as executor:

        # each thread handles the scan of a different address
        for address in addresses:
            future = executor.submit(scan_ports, address, target_ports)
            scan_results.append(future)
    
    # the list contains future objects returned by the threads
    return scan_results

def main():
    print(f"\nScanning {input_addresses} for port(s) {input_ports}...\n")

    scan_result = start_scan(target_addresses)
    result_list = []

    # get the result of each future object
    for addr in scan_result:
        result = addr.result()

        # only append if there were any open ports on address
        if addr:
            result_list.append(result)

    if output == "y" or output == "yes":

        # create .txt file in the same directory as this script
        dir_path = path.dirname(__file__)
        file_path = path.join(dir_path, filename)

        def write(line: str):
            with open(file_path, "a") as file:
                file.write(line)

        write(f"Scan results for {input_addresses} and port(s) {input_ports}:\nADDRESS \tPORT \tSERVICE\n")
        for r in result_list:

            # each result is a list of open ports in each address
            for line in r:
                write(line + "\n")
    
    else:
        print(f"Open Ports in {input_addresses} for ports {input_ports}:\nADDRESS \tPORT \tSERVICE")
        for r in result_list:
            for line in r:
                print(line)

main()