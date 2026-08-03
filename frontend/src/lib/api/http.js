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
        throw {
            status: response.status,
            detail: data.detail,
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
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.blob();
}