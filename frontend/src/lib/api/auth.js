import {fetchParseHandler} from "./http.js";
const API_URL = import.meta.env.VITE_API_URL;

export async function signup(user) {
    return await fetchParseHandler(`${API_URL}/auth/signup`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(user)
    });

}

export async function signin(user) {
    
    return await fetchParseHandler(`${API_URL}/auth/signin`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(user)
    });


}

