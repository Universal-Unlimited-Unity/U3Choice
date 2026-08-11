export async function fetchParseHandler(url, options) {
    let response;
    try {
    response = await fetch(url, options);
    } catch (error) {
        console.error(`Network error: ${error.message}`);
        throw new Error(`Network error: ${error.message}`);
    }
    let data = null;

    try {
        data = await response.json();
    } catch {}

    if (!response.ok) {
        // If unauthorized, clear token and notify app to logout
        if (response.status === 401) {
            try {
                localStorage.removeItem("token");
            } catch (e) {}
            const reason = data?.detail || 'Unauthorized';
            try {
                window.dispatchEvent(new CustomEvent('u3:logout', { detail: { reason } }));
            } catch (e) {}
        }

        throw {
            status: response.status,
            detail: data?.detail,
        }
    }

    return data;
}

export async function fetchParseHandlerForFiles(url, options) {
    let response;
    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new Error(`Network error: ${error.message}`);
    }

    if (!response.ok) {
        if (response.status === 401) {
            try { localStorage.removeItem("token"); } catch (e) {}
            try {
                window.dispatchEvent(new CustomEvent('u3:logout', { detail: { reason: 'Unauthorized' } }));
            } catch (e) {}
        }
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.blob();
}