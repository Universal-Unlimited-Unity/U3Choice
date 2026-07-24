export async function signup(user) {
    console.log("signup called");

    const response = await fetch("http://localhost:8000/auth/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(user)
    });

    console.log(response);

    return response.json();
}