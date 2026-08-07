import {fetchParseHandler} from "./fetch.js";
const API_URL = import.meta.env.VITE_API_URL;

export async function sendFriendRequest(token, friendshipData) {
    return await fetchParseHandler(`${API_URL}/friendships/send_request`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(friendshipData)
    });
}

export async function acceptFriendRequest(token, friendshipData) {
    return await fetchParseHandler(`${API_URL}/friendships/accept_request`, {
        method: "POST",
        headers: {"Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(friendshipData)
    });
}

export async function rejectFriendRequest(token, friendshipData) {
    return await fetchParseHandler(`${API_URL}/friendships/reject_request`, {
        method: "POST",
        headers: {"Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(friendshipData)
    });
}

export async function BlockFriend(token, blockfriendshipData) {
    return await fetchParseHandler(`${API_URL}/friendships/block`, { 
        method: "POST",
        headers: {"Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(blockfriendshipData)
    });
}

export async function UnblockFriend(token, blockfriendshipData) {
    return await fetchParseHandler(`${API_URL}/friendships/unblock`, { 
        method: "POST",
        headers: {"Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(unblockfriendshipData)
    });
}

export async function removeFriendship(token, friendshipData) {
    return await fetchParseHandler(`${API_URL}/friendships/remove_friendship`, {
        method: "DELETE",
        headers: {"Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(friendshipData)
    });
}
