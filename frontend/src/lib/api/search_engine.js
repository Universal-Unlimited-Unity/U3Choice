import {fetchParseHandler} from "./http.js";

const API_URL = import.meta.env.VITE_API_URL;

export async function searchUsers(token, keyword, limit = 10) {
    const url = new URL(`${API_URL}/search/users`);
    url.searchParams.append("keyword", keyword);
    url.searchParams.append("limit", limit);
    return (await fetchParseHandler(url, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })).results;
}
