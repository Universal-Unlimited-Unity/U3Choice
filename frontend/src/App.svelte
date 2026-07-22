const API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8000';

export async function signup(user) {
    console.log("Posting to:", `${API_URL}/signup`, user);

    const response = await fetch(`${API_URL}/signup`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(user),
    });

    const data = await response.json();

    if (!response.ok) {
        throw data;
    }

    return data;
}

export async function signin(credentials) {
    console.log("Posting to:", `${API_URL}/signin`, credentials);

    const response = await fetch(`${API_URL}/signin`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
    });

    const data = await response.json();

    if (!response.ok) {
        throw data;
    }

    return data;
}