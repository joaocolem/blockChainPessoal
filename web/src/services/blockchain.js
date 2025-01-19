import axios from 'axios';

export const registerNode = async (nodes, port) => {
    try {
        const response = await axios.post(`http://localhost:${port}/nodes/register`, {
            nodes: nodes,
        });
        return response.data;
    } catch (error) {
        console.error("Error registering node:", error);
        return error.response ? error.response.data : error.message;
    }
};

export const newTransaction = async (sender, recipient, amount, port) => {
    try {
        const response = await axios.post(`http://localhost:${port}/transactions/new`, {
            sender,
            recipient,
            amount,
        });
        return response.data;
    } catch (error) {
        console.error("Error creating transaction:", error);
        return error.response ? error.response.data : error.message;
    }
};

export const mineBlock = async (port) => {
    try {
        const response = await axios.get(`http://localhost:${port}/mine`);
        return response.data;
    } catch (error) {
        console.error("Error mining block:", error);
        return error.response ? error.response.data : error.message;
    }
};

export const resolveConflicts = async (port) => {
    try {
        const response = await axios.get(`http://localhost:${port}/nodes/resolve`);
        return response.data;
    } catch (error) {
        console.error("Error resolving conflicts:", error);
        return error.response ? error.response.data : error.message;
    }
};

export const getChain = async (port) => {
    try {
        const response = await axios.get(`http://localhost:${port}/chain`);
        return response.data;
    } catch (error) {
        console.error("Error getting chain:", error);
        return error.response ? error.response.data : error.message;
    }
};
