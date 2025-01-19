import { useState } from 'react';
import { newTransaction, mineBlock, resolveConflicts, getChain } from './services/blockchain';

function App() {
  const [sender, setSender] = useState('');
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  const [blockchain, setBlockchain] = useState([]);
  const [message, setMessage] = useState('');

  const [port, setPort] = useState(5000);

  const updateBaseUrl = (selectedPort) => {
    setPort(selectedPort);
  };



  const handleNewTransaction = async () => {
    const result = await newTransaction(sender, recipient, amount, port);
    setMessage(result.message || 'Transaction added successfully!');
  };

  const handleMineBlock = async () => {
    const result = await mineBlock(port);
    setMessage(result.message || 'Block mined successfully!');
  };

  const handleResolveConflicts = async () => {
    const result = await resolveConflicts(port);
    setMessage(result.message || 'Conflicts resolved successfully!');
  };

  const handleGetChain = async () => {
    const result = await getChain(port);
    setBlockchain(result.chain);
  };

  const renderTransactions = (transactions) => {
    return transactions.length ? (
      <div className="transactions">
        {transactions.map((transaction, index) => (
          <div key={index} className="transaction">
            <p>Sender: {transaction.sender}</p>
            <p>Recipient: {transaction.recipient}</p>
            <p>Amount: {transaction.amount}</p>
          </div>
        ))}
      </div>
    ) : (
      <p>No transactions</p>
    );
  };

  const truncateHash = (hash) => {
    if (hash && typeof hash === 'string') {
      return hash.length > 10 ? `${hash.substring(0, 10)}...` : hash;
    }
    return "N/A";
  };




  return (
    <div className="App">
      <h1>Blockchain Frontend</h1>

      {/* Selecionar Porta */}
      <div>

        <div>
          <h2>Select Port</h2>
          <select value={port} onChange={(e) => updateBaseUrl(Number(e.target.value))}>
            {Array.from({ length: 8 }, (_, i) => 5000 + i).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <p>Current API URL: {port}</p>
        </div>

      </div>

      {/* Criar transação */}
      <div>
        <h2>New Transaction</h2>
        <input
          type="text"
          placeholder="Sender"
          onChange={(e) => setSender(e.target.value)}
          value={sender}
        />
        <input
          type="text"
          placeholder="Recipient"
          onChange={(e) => setRecipient(e.target.value)}
          value={recipient}
        />
        <input
          type="number"
          placeholder="Amount"
          onChange={(e) => setAmount(e.target.value)}
          value={amount}
        />
        <button onClick={handleNewTransaction}>Create Transaction</button>
      </div>

      {/* Minerar bloco */}
      <div>
        <h2>Mine Block</h2>
        <button onClick={handleMineBlock}>Mine</button>
      </div>

      {/* Resolver conflitos */}
      <div>
        <h2>Resolve Conflicts</h2>
        <button onClick={handleResolveConflicts}>Resolve</button>
      </div>

      {/* Ver cadeia de blocos */}
      <div>
        <h2>Blockchain</h2>
        <button onClick={handleGetChain}>Get Blockchain</button>
        <div className="blockchain-container">
          {blockchain.map((block) => (
            <div key={block.index} className="block">
              <div className="block-header">
                <h3>Block #{block.index}</h3>
                <p><strong>Previous Hash:</strong> {truncateHash(block.previous_hash)}</p>
                <p><strong>Proof:</strong> {block.proof}</p>
              </div>

              {/* Renderizando as transações */}
              {renderTransactions(block.transactions)}
            </div>
          ))}
        </div>
      </div>

      {/* Mensagem de status */}
      <div>
        <h2>Status</h2>
        <p>{message}</p>
      </div>
    </div>
  );
}

export default App;
