import { fetchParseHandler } from "./http.js";

const API_URL = import.meta.env.VITE_API_URL;

export async function sendVerificationEmail(token, email = "") {
    const params = new URLSearchParams();
    if (email?.trim()) {
        params.set("email", email.trim());
    }

    const query = params.toString();
    const url = `${API_URL}/security/send_verification_email${query ? `?${query}` : ""}`;

    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    return await fetchParseHandler(url, {
        method: "POST",
        headers
    });
}

export async function sendForgotPasswordVerificationEmail(email) {
    const params = new URLSearchParams({ email: email.trim() });

    return await fetchParseHandler(`${API_URL}/security/send_verification_email_forgot_password?${params.toString()}`, {
        method: "POST"
    });
}

export async function verifyEmailCode(token, code) {
    const params = new URLSearchParams({ code: String(code).trim() });

    return await fetchParseHandler(`${API_URL}/security/verify_email_code?${params.toString()}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
}

export async function resetForgottenPassword(email, code, newPassword) {
    const params = new URLSearchParams({
        email: email.trim(),
        code: String(code).trim(),
        new_password: newPassword
    });

    return await fetchParseHandler(`${API_URL}/security/forgot_password?${params.toString()}`, {
        method: "GET"
    });
}