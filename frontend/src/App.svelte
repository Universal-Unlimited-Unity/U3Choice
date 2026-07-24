<script>
    import { signup, signin } from "./lib/api/auth";

    let mode = "signin";

    let signupForm = {
        username: "",
        email: "",
        phone: "",
        name: "",
        password: "",
        dob: "",
        country: ""
    };

    let signinForm = {
        email: "",
        password: ""
    };

    let loading = false;
    let error = "";
    let token = localStorage.getItem("token");

    async function handleSignup() {
        console.clear();
        console.log("========== SIGNUP ==========");
        console.log("Button clicked");
        console.log("Form:", signupForm);

        error = "";
        loading = true;

        try {
            console.log("Calling signup()...");

            const result = await signup(signupForm);

            console.log("signup() returned:");
            console.log(result);

            alert("Account created successfully!");

            mode = "signin";

            signinForm.email = signupForm.email;
            signinForm.password = "";

        } catch (err) {
            console.error("Signup failed:");
            console.error(err);

            error = err?.message || JSON.stringify(err) || "Unknown Error";
        }

        loading = false;

        console.log("Finished signup");
    }

    async function handleSignin() {
        console.clear();
        console.log("========== SIGNIN ==========");
        console.log("Button clicked");
        console.log("Credentials:", signinForm);

        error = "";
        loading = true;

        try {
            console.log("Calling signin()...");

            const data = await signin(signinForm);

            console.log("signin() returned:");
            console.log(data);

            token = data.token;

            console.log("Token:");
            console.log(token);

            localStorage.setItem("token", token);

        } catch (err) {
            console.error("Signin failed:");
            console.error(err);

            error = err?.message || JSON.stringify(err) || "Unknown Error";
        }

        loading = false;

        console.log("Finished signin");
    }

    function logout() {
        console.log("Logging out");

        localStorage.removeItem("token");
        token = null;
    }
</script>

<div class="container">

{#if token}

<div class="card">

<h1>✅ You are signed in</h1>

<p>Your JWT Token</p>

<pre>{token}</pre>

<button on:click={logout}>
Logout
</button>

</div>

{:else}

<div class="card">

<h1>Authentication Demo</h1>

<div class="tabs">

<button
class:active={mode==="signin"}
on:click={() => mode="signin"}>
Sign In
</button>

<button
class:active={mode==="signup"}
on:click={() => mode="signup"}>
Sign Up
</button>

</div>

{#if mode==="signup"}

<input bind:value={signupForm.username} placeholder="Username">

<input bind:value={signupForm.name} placeholder="Full Name">

<input
bind:value={signupForm.email}
type="email"
placeholder="Email">

<input
bind:value={signupForm.phone}
placeholder="Phone">

<input
bind:value={signupForm.password}
type="password"
placeholder="Password">

<input
bind:value={signupForm.dob}
type="date">

<input
bind:value={signupForm.country}
maxlength="2"
placeholder="Country">

<button
class="submit"
on:click={handleSignup}
disabled={loading}>

{loading ? "Creating..." : "Create Account"}

</button>

{:else}

<input
bind:value={signinForm.email}
type="email"
placeholder="Email">

<input
bind:value={signinForm.password}
type="password"
placeholder="Password">

<button
class="submit"
on:click={handleSignin}
disabled={loading}>

{loading ? "Signing In..." : "Sign In"}

</button>

{/if}

{#if error}

<div class="error">

{error}

</div>

{/if}

</div>

{/if}

</div>

<style>
:global(body){
margin:0;
font-family:Arial,Helvetica,sans-serif;
background:#f4f6f8;
}

.container{
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
padding:2rem;
}

.card{
width:420px;
background:white;
padding:2rem;
border-radius:12px;
box-shadow:0 10px 30px rgba(0,0,0,.15);
}

.tabs{
display:flex;
gap:.5rem;
margin-bottom:1rem;
}

.tabs button{
flex:1;
padding:.8rem;
}

.tabs .active{
background:#2563eb;
color:white;
}

input{
width:100%;
padding:.8rem;
margin-bottom:1rem;
box-sizing:border-box;
}

.submit{
width:100%;
background:#2563eb;
color:white;
}

.error{
margin-top:1rem;
background:#fee2e2;
color:#b91c1c;
padding:.75rem;
border-radius:8px;
}

pre{
white-space:pre-wrap;
word-break:break-word;
}
</style>