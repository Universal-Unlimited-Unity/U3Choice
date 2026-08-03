import {fetchParseHandler, fetchParseHandlerForFiles} from "./http.js";
const API_URL = import.meta.env.VITE_API_URL;

export async function getProfile(token, profileUsername) {
    return await fetchParseHandler(`${API_URL}/${profileUsername}`, {
        headers: {
            "Authorization": `Bearer ${token}`
        } 
    });
}

let profilePhotoUrl = null;

async function getPhoto(username) {
    try {
        const blob = await fetchParseHandlerForFiles(`${API_URL}/${username}/photo`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (blob) {
            if (profilePhotoUrl) URL.revokeObjectURL(profilePhotoUrl);
            
            profilePhotoUrl = URL.createObjectURL(blob);
        }
    } catch (err) {
        console.error("Failed to load photo", err);
    }
}