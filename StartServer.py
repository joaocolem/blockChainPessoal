import os
import multiprocessing
from blockchain import Blockchain, add_node_to_file, register_nodes_automatically
from time import sleep
import requests

def get_registered_ports(file_path='nodes.txt'):
    """Obtém as portas dos nós já registrados no arquivo nodes.txt."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip().split(":")[-1] for line in file.readlines()]
    return []

def register_node(port, file_path='nodes.txt'):
    """Registra um nó no arquivo e configura automaticamente."""
    node_url = f"http://127.0.0.1:{port}"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(f"{node_url}\n")
    else:
        add_node_to_file(node_url)
        register_nodes_automatically(node_url)

def launch_server(port):
    """Inicializa o servidor na porta especificada."""
    from blockchain import app
    app.run(host='127.0.0.1', port=port)

def monitor_server(port):
    """Espera o servidor na porta especificada ficar pronto."""
    node_url = f"http://127.0.0.1:{port}/chain"
    while True:
        try:
            response = requests.get(node_url)
            if response.status_code == 200:
                print(f"Servidor na porta {port} está pronto.")
                return
        except requests.exceptions.RequestException:
            print(f"Aguardando o servidor na porta {port}...")
        sleep(1)

def connect_nodes(ports):
    """Interconecta todos os nós fornecidos."""
    for port in ports:
        node_url = f"http://127.0.0.1:{port}"
        
        target_urls = [f"http://127.0.0.1:{target_port}" for target_port in ports if target_port != port]
        
        try:
            response = requests.post(f"{node_url}/nodes/register", json={"nodes": target_urls})
            if response.status_code == 201:
                print(f"Todos os nós registrados com sucesso em {node_url}.")
            else:
                print(f"Erro ao registrar nós em {node_url}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar com {node_url}: {e}")

def initialize_servers(ports):
    """Inicia e monitora múltiplos servidores."""
    processes = []

    for port in ports:
        register_node(port)
        process = multiprocessing.Process(target=launch_server, args=(port,))
        processes.append(process)
        process.start()
        sleep(1)

    for port in ports:
        monitor_server(port)

    connect_nodes(ports)

    for process in processes:
        process.join()

def main():
    """Controla o fluxo principal de inicialização e registro de servidores."""
    default_ports = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007]
    registered_ports = get_registered_ports()
    all_ports = sorted(set(map(int, registered_ports + default_ports)))

    initialize_servers(all_ports)

if __name__ == '__main__':
    main()
