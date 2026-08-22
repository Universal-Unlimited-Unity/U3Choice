import { fetchParseHandler } from "./http.js";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getMessagesBetweenUsers(token, user1Id, user2Id) {
    if (!token || !user1Id || !user2Id) {
        return [];
    }

    const response = await fetchParseHandler(`${API_URL}/messages/between/${user1Id}/${user2Id}`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    return Array.isArray(response?.messages) ? response.messages : [];
}

export async function sendMessage(token, payload) {
    if (!token || !payload) {
        throw new Error("Missing message payload");
    }

    return await fetchParseHandler(`${API_URL}/messages/send`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });
}
