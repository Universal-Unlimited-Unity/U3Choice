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

export async function getPhoto(token, username) {
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

export async function getPhotoUrl(token, username) {
    try {
        const blob = await fetchParseHandlerForFiles(`${API_URL}/${username}/photo`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (blob) {
            return URL.createObjectURL(blob);
        }
    } catch (err) {
        console.error("Failed to load photo for", username, err);
    }
    return null;
}

export async function getfriends(token, username) {
    return await fetchParseHandler(`${API_URL}/${username}/friends`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
}

export async function updateProfile(token, username, updateData) {
    return await fetchParseHandler(`${API_URL}/${username}/update`, {
        method: "PATCH",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(updateData)
    });
}

export async function updateProfilePhoto(token, username, photoFile) {
    const formData = new FormData();
    formData.append("photo", photoFile);
    return await fetchParseHandler(`${API_URL}/${username}/update/photo`, {
        method: "PATCH",
        headers: {
            "Authorization": `Bearer ${token}`
        },
        body: formData
    });
}

export async function changePassword(token, oldPassword, newPassword) {
    return await fetchParseHandler(`${API_URL}/settings/password`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            old_pwd: { old_pwd: oldPassword },
            new_pwd: { new_pwd: newPassword }
        })
    });
}

export async function changeEmail(token, currentPassword, newEmail) {
    return await fetchParseHandler(`${API_URL}/settings/email`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            pwd: { old_pwd: currentPassword },
            new_email: { new_email: newEmail }
        })
    });
}

export async function changePhone(token, currentPassword, newPhone) {
    return await fetchParseHandler(`${API_URL}/settings/phone`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            pwd: { old_pwd: currentPassword },
            new_phone: { new_phone: newPhone }
        })
    });
}


