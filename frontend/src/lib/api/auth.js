import { fetchParseHandler } from "./http";

const VITE_AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL;

export async function signup(user) {
    return fetchParseHandler("${VITE_AUTH_API_URL}/auth/signup", 
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(user)
        }

    )
}

export async function signin(credentials) {
    return fetchParseHandler("${VITE_AUTH_API_URL}/auth/signin",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(credentials)
        }

    )
}