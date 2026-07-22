export async function fetchParseHandler(url, options) {
    const response = await fetch(url, options);
    let data = null;

    try {
        data = await response.json();
    } catch {}

    if (!response.ok) {
        throw {
            status: response.status,
            detail: data?.detail ?? "Unkown"
        };
    }

    return data;
}