import os
import multiprocessing
from blockchain import Blockchain, add_node_to_file, register_nodes_automatically
from time import sleep
import requests

def read_existing_ports():
    """Lê as portas dos nós registrados no arquivo nodes.txt"""
    if not os.path.exists('nodes.txt'):
        return []
    with open('nodes.txt', 'r') as file:
        nodes = file.readlines()
    return [node.strip().split(":")[-1] for node in nodes]  

def start_server(port=5000):
    """Função que inicializa o servidor na porta fornecida."""
    node_url = f"http://127.0.0.1:{port}"
    
    if not os.path.exists('nodes.txt'):
        with open('nodes.txt', 'w') as file:
            file.write(f"{node_url}\n")
    else:

        add_node_to_file(node_url) 
        register_nodes_automatically(node_url) 

    # Inicia o servidor
    from blockchain import app
    app.run(host='127.0.0.1', port=port)

def all_servers_ready(ports):
    """Verifica se todos os servidores estão prontos (respondendo a uma requisição GET)."""
    for port in ports:
        node_url = f"http://127.0.0.1:{port}/chain"
        while True:
            try:
                response = requests.get(node_url)
                if response.status_code == 200:
                    print(f"Servidor na porta {port} está pronto.")
                    break
            except requests.exceptions.RequestException:
                print(f"Aguardando o servidor na porta {port}...")
            sleep(1)

def register_all_nodes(ports):
    """Registra todos os nós entre si após estarem prontos."""
    for i, port in enumerate(ports):
        node_url = f"http://127.0.0.1:{port}"
        for other_port in ports:
            if other_port != port:
                other_node_url = f"http://127.0.0.1:{other_port}"
                print(f"Registrando nó {node_url} em {other_node_url}")
                try:
                    response = requests.post(f"{other_node_url}/nodes/register", json={"nodes": [node_url]})
                    if response.status_code == 201:
                        print(f"Registro do nó {node_url} em {other_node_url} bem-sucedido.")
                    else:
                        print(f"Erro ao tentar registrar nó {node_url} em {other_node_url}.")
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao tentar registrar nó {node_url} em {other_node_url}: {e}")

def start_multiple_servers():
    """Função para iniciar múltiplos servidores e garantir que todos estejam prontos antes de registrar entre si."""
    registered_ports = read_existing_ports()
    
    default_ports = [5000, 5001, 5002, 5003, 5004,5005,5006,5007]
    
    ports = set(registered_ports).union(default_ports)
    
    processes = []
    for port in ports:
        process = multiprocessing.Process(target=start_server, args=(port,))
        processes.append(process)
        process.start()
        sleep(1)  
        
    all_servers_ready(list(ports))

    register_all_nodes(list(ports))

    for process in processes:
        process.join()

if __name__ == '__main__':
    start_multiple_servers()