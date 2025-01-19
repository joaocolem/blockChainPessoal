import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Caminho do arquivo de nós
NODES_FILE = 'nodes.txt'

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Cria o bloco gênese
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Adiciona um novo nó à lista de nós
        :param address: Endereço do nó. Exemplo: 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Aceita um URL sem esquema como '192.168.0.5:5000'
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('URL inválido')

    def valid_chain(self, chain):
        """
        Determina se uma blockchain é válida
        :param chain: Uma blockchain
        :return: True se for válida, False se não for
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Verifica se o hash do bloco está correto
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Verifica se o Proof of Work está correto
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True


    def resolve_conflicts(self):
        neighbours = self.nodes 
        new_chain = None
        chains = {}

        chains['local'] = self.chain
        print(f"Cadeia local: {self.chain}")

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    chain = response.json()['chain']
                    chains[node] = chain
            except requests.exceptions.RequestException as e:
                print(f"Erro ao conectar com o nó {node}: {e}")

        if not chains:
            print("Não foi possível obter cadeias dos vizinhos.")
            return False

        block_index = 0
        while chains:
            block_hashes = {}

            for node, chain in chains.items():
                if block_index < len(chain): 
                    block = chain[block_index]
                    block_hash = block.get('previous_hash') 
                    if block_hash:
                        block_hashes[block_hash] = block_hashes.get(block_hash, 0) + 1

            if block_hashes:
                print("-----------------------------------------------")
                most_common_hash = max(block_hashes, key=block_hashes.get)
                print(f"Bloco {block_index + 1}: Hash mais comum é {most_common_hash}")

                chains = {node: chain for node, chain in chains.items() if block_index < len(chain) and chain[block_index].get('previous_hash') == most_common_hash}

                print(len(chains))
                if len(chains) == 1 or all(block_index >= len(chain) for chain in chains.values()):
                    new_chain = next(iter(chains.values()))
                    print(f"Cadeia escolhida: {new_chain}")
                    break
            else:
                break

            block_index += 1

        
        
        if len(chains) > 1:
            new_chain = next(iter(chains.values()))
        local_chain_in_chains = any(chain == self.chain for chain in chains.values())
        
        if new_chain and not local_chain_in_chains:
            self.chain = new_chain
            print("Cadeia substituída com sucesso!")
            return True

        print("Não houve necessidade de substituir a cadeia.")
        return False




    def new_block(self, proof, previous_hash):
        """
        Cria um novo bloco na blockchain
        :param proof: O proof dado pelo algoritmo Proof of Work
        :param previous_hash: O hash do bloco anterior
        :return: Novo bloco
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reseta a lista de transações
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Cria uma nova transação para ser adicionada ao próximo bloco
        :param sender: Endereço do remetente
        :param recipient: Endereço do destinatário
        :param amount: Quantidade
        :return: O índice do bloco que conterá essa transação
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 de um bloco
        :param block: Bloco
        :return: Hash do bloco
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Algoritmo simples de Proof of Work:
         - Encontrar um número p' tal que hash(pp') contenha 4 zeros à frente
         - Onde p é o proof anterior, e p' é o novo proof
        :param last_block: O último bloco
        :return: Novo proof
        """
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Valida o proof
        :param last_proof: Proof anterior
        :param proof: Proof atual
        :param last_hash: Hash do último bloco
        :return: True se válido, False caso contrário
        """
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


def read_nodes_from_file():
    if not os.path.exists(NODES_FILE):
        return []

    with open(NODES_FILE, 'r') as file:
        return [line.strip() for line in file.readlines()]

def add_node_to_file(node_url):
    with open(NODES_FILE, 'a') as file:
        file.write(f"{node_url}\n")


def register_nodes_automatically(new_node_url):
    nodes = read_nodes_from_file()  
    for node in nodes:
        if node != new_node_url:  
            url = f"{new_node_url}/nodes/register"
            payload = {"nodes": [node]}
            try:
                response = requests.post(url, json=payload)
                print(f"Node {node} registrado com sucesso no {new_node_url}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao registrar o nó {node} no {new_node_url}: {e}")

app = Flask(__name__)
CORS(app)
node_identifier = str(uuid4()).replace('-', '')  # Identificador único para o nó
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    
    proof = blockchain.proof_of_work(last_block)
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    print(f"Bloco minerado: {block}")

    response = {
        'message': "Novo bloco minerado",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Valores ausentes', 400

    print(f"Transação recebida: {values}")

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transação será adicionada ao bloco {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Erro: Por favor forneça uma lista válida de nós", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Novos nós foram adicionados',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Nossa cadeia foi substituída',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Nossa cadeia é autoritativa',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


def add_node_to_file(node_url):
    """
    Adiciona o nó à lista de nós no arquivo `nodes.txt`.
    """
    with open('nodes.txt', 'a') as file:
        file.write(f"{node_url}\n")
    print(f"Nó {node_url} registrado no arquivo de nós.")


def register_nodes_automatically(node_url):
    """
    Registra este nó automaticamente nos outros nós existentes.
    """
    # Lê os nós do arquivo
    try:
        with open('nodes.txt', 'r') as file:
            nodes = file.readlines()
        
        for node in nodes:
            node = node.strip()  # Remover possíveis espaços extras ou quebras de linha
            if node != node_url:  # Não tentar registrar o nó atual em si mesmo
                try:
                    # Garantir que a URL está corretamente formatada com "http://"
                    if not node.startswith('http://'):
                        node = 'http://' + node
                    
                    response = requests.post(f'{node}/nodes/register', json={"nodes": [node_url]})
                    if response.status_code == 201:
                        print(f"Registro do nó {node_url} em {node} bem-sucedido.")
                    else:
                        print(f"Erro ao registrar nó {node_url} em {node}: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao tentar registrar nó {node_url} em {node}: {str(e)}")
    except FileNotFoundError:
        print("Arquivo de nós não encontrado. Certifique-se de que o arquivo 'nodes.txt' existe.")

# novas


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='Porta para escutar')
    args = parser.parse_args()
    port = args.port

    # Registra os nós automaticamente ao iniciar o servidor
    register_nodes_automatically(f'http://127.0.0.1:{port}')

    app.run(host='127.0.0.1', port=port)