<script>
    import { signup, signin } from "./lib/api/auth";
    import CountryData from "country-list-with-dial-code-and-flag";
    import logo from "./assets/logo.png";

    // Handle CJS/ESM module wrapper differences in Vite
    const rawCountries = Array.isArray(CountryData) 
        ? CountryData 
        : (CountryData?.default || []);

    // Sanitize country list and calculate lowercase codes for flag-icons CSS
    const countries = rawCountries.map(c => ({
        ...c,
        lowerCode: c.code ? c.code.toLowerCase() : ""
    }));

    let mode = "signin";

    // Selection states
    let selectedCountry = countries.find(c => c.code === "US") || countries[0];
    let selectedPhonePrefix = selectedCountry?.dial_code || "+1";
    let rawPhoneNumber = "";

    let signupForm = {
        username: "",
        email: "",
        phone: "",
        name: "",
        pwd_hash: "",
        dob: "",
        country: "US"
    };

    let signinForm = {
        email: "",
        pwd: ""
    };

    let loading = false;
    let error = "";
    let successMessage = "";
    let successCountdown = 3;
    let redirectTimer = null;
    let invalidFields = {}; 
    let token = localStorage.getItem("token");

    // Searchable dropdown state
    let phoneDropdownOpen = false;
    let countryDropdownOpen = false;
    let phoneSearch = "";
    let countrySearch = "";

    // Reactive search filters
    $: filteredPhoneCountries = countries.filter(c => 
        c.name.toLowerCase().includes(phoneSearch.toLowerCase()) ||
        c.dial_code.includes(phoneSearch) ||
        c.code.toLowerCase().includes(phoneSearch.toLowerCase())
    );

    $: filteredCountries = countries.filter(c => 
        c.name.toLowerCase().includes(countrySearch.toLowerCase()) ||
        c.code.toLowerCase().includes(countrySearch.toLowerCase())
    );

    function selectPhoneCountry(country) {
        selectedPhonePrefix = country.dial_code;
        phoneDropdownOpen = false;
        phoneSearch = "";
    }

    function selectCountry(country) {
        selectedCountry = country;
        signupForm.country = country.code;
        countryDropdownOpen = false;
        countrySearch = "";
    }

    function clearNotice() {
        error = "";
        successMessage = "";
        if (redirectTimer) clearInterval(redirectTimer);
    }

    // Validation logic
    function validateSignup() {
        invalidFields = {};
        const missing = [];

        if (!signupForm.username.trim()) { invalidFields.username = true; missing.push("username"); }
        if (!signupForm.name.trim()) { invalidFields.name = true; missing.push("full name"); }
        if (!signupForm.email.trim()) { invalidFields.email = true; missing.push("email"); }
        if (!rawPhoneNumber.trim()) { invalidFields.phone = true; missing.push("phone number"); }
        if (!signupForm.pwd_hash.trim()) { invalidFields.pwd_hash = true; missing.push("password"); }
        if (!signupForm.dob.trim()) { invalidFields.dob = true; missing.push("date of birth"); }
        if (!signupForm.country.trim()) { invalidFields.country = true; missing.push("country"); }

        if (missing.length > 0) {
            error = `Please fill in all required fields (${missing.join(", ")}).`;
            return false;
        }

        return true;
    }

    function validateSignin() {
        invalidFields = {};
        const missing = [];

        if (!signinForm.email.trim()) { invalidFields.email = true; missing.push("email"); }
        if (!signinForm.pwd.trim()) { invalidFields.pwd = true; missing.push("password"); }

        if (missing.length > 0) {
            error = `Please fill in all required fields (${missing.join(", ")}).`;
            return false;
        }

        return true;
    }

    function executeRedirectToSignin() {
        if (redirectTimer) clearInterval(redirectTimer);
        mode = "signin";
        signinForm.email = signupForm.email;
        signinForm.pwd = "";
        successMessage = "";
        invalidFields = {};
    }

    async function handleSignup() {
        clearNotice();

        if (!validateSignup()) return;

        loading = true;
        signupForm.phone = `${selectedPhonePrefix} ${rawPhoneNumber.trim()}`;

        try {
            await signup(signupForm);

            // Trigger success message and start 3-second redirect countdown
            successMessage = `Account created successfully! Redirecting to Sign In in ${successCountdown}s...`;
            
            redirectTimer = setInterval(() => {
                successCountdown -= 1;
                if (successCountdown > 0) {
                    successMessage = `Account created successfully! Redirecting to Sign In in ${successCountdown}s...`;
                } else {
                    executeRedirectToSignin();
                }
            }, 1000);

        } catch (err) {
            if (err?.detail === "USERNAME_TAKEN") {
                error = "Username is already taken.";
            } else if (err?.detail === "EMAIL_TAKEN") {
                error = "Email is already registered.";
            } else if (err?.detail === "PASSWORD_NOT_STRONG") {
                error = "Password is not strong enough, must be at least 8 characters long and contain a mix of letters, numbers, and special characters.";
            } else if (err?.detail === "USER_UNDERAGE") {
                error = "You must be at least 18 years old to create an account.";
            } else if (err?.status === 422) {
                error = err?.data?.detail?.[0]?.msg || "Phone number is invalid";
            } else {
                error = "An unexpected error occurred. Please try again.";
                console.error(err);
            }           
        }

        loading = false;
    }

    async function handleSignin() {
        clearNotice();

        if (!validateSignin()) return;

        loading = true;

        try {
            const data = await signin(signinForm);
            token = data.token;
            localStorage.setItem("token", token);
            invalidFields = {};
        } catch (err) {
            if (err?.detail === "INVALID_CREDENTIALS") {
                error = "Invalid email or password.";
            } else if (err?.detail === "USER_SUSPENDED") {
                error = "Your account has been suspended. Please contact support.";
            } else {
                error = "An unexpected error occurred. Please try again.";
                console.error(err);
            }
        }

        loading = false;
    }

    function logout() {
        localStorage.removeItem("token");
        token = null;
    }
</script>

<svelte:head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.0.0/css/flag-icons.min.css" />
</svelte:head>

<header class="app-brand">
    <img src={logo} alt="U3 Choice Logo" class="brand-logo" />
</header>

<div class="container">

{#if token}

<div class="card">
    <h1>✅ You are signed in</h1>
    <p>Your JWT Token</p>
    <pre>{token}</pre>
    <button class="submit" on:click={logout}>Logout</button>
</div>

{:else}

<div class="card">
    <h1>Authentication</h1>

    <div class="tabs">
        <button
            class:active={mode === "signin"}
            on:click={() => { mode = "signin"; clearNotice(); invalidFields = {}; }}>
            Sign In
        </button>

        <button
            class:active={mode === "signup"}
            on:click={() => { mode = "signup"; clearNotice(); invalidFields = {}; }}>
            Sign Up
        </button>
    </div>

    {#if successMessage}
        <!-- Animated Success Redirect Card -->
        <div class="success-box">
            <div class="success-icon">🎉</div>
            <p>{successMessage}</p>
            <button type="button" class="link-btn" on:click={executeRedirectToSignin}>
                Go to Sign In now &rarr;
            </button>
        </div>
    {:else if mode === "signup"}

        <input 
            class:invalid={invalidFields.username} 
            bind:value={signupForm.username} 
            placeholder="Username *"
        >

        <input 
            class:invalid={invalidFields.name} 
            bind:value={signupForm.name} 
            placeholder="Full Name *"
        >

        <input
            class:invalid={invalidFields.email}
            bind:value={signupForm.email}
            type="email"
            placeholder="Email *"
        >

        <!-- Searchable Phone Dropdown -->
        <div class="phone-group">
            <div class="custom-select prefix-select">
                <button type="button" class="select-btn" on:click={() => phoneDropdownOpen = !phoneDropdownOpen}>
                    <span class="fi fi-{countries.find(c => c.dial_code === selectedPhonePrefix)?.lowerCode}"></span>
                    <span>{selectedPhonePrefix}</span>
                </button>

                {#if phoneDropdownOpen}
                    <div class="dropdown-menu">
                        <input 
                            type="text" 
                            class="search-input" 
                            placeholder="Search code..." 
                            bind:value={phoneSearch}
                            autofocus
                        />
                        <div class="options-list">
                            {#each filteredPhoneCountries as c}
                                <button type="button" class="option-item" on:click={() => selectPhoneCountry(c)}>
                                    <span class="fi fi-{c.lowerCode}"></span>
                                    <span class="opt-text">{c.name} ({c.dial_code})</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>

            <input 
                class:invalid={invalidFields.phone} 
                bind:value={rawPhoneNumber} 
                type="tel" 
                placeholder="Phone Number *"
            >
        </div>

        <input
            class:invalid={invalidFields.pwd_hash}
            bind:value={signupForm.pwd_hash}
            type="password"
            placeholder="Password *"
        >

        <!-- Explicit Label for Date of Birth Field -->
        <div class="field-container">
            <label for="dob-input" class="field-label">Date of Birth *</label>
            <input
                id="dob-input"
                class:invalid={invalidFields.dob}
                bind:value={signupForm.dob}
                type="date"
            >
        </div>

        <!-- Searchable Country Dropdown -->
        <div class="custom-select full-width">
            <button 
                type="button" 
                class="select-btn" 
                class:invalid={invalidFields.country}
                on:click={() => countryDropdownOpen = !countryDropdownOpen}
            >
                <span class="fi fi-{selectedCountry?.lowerCode}"></span>
                <span>{selectedCountry?.name || "Select Country *"}</span>
            </button>

            {#if countryDropdownOpen}
                <div class="dropdown-menu">
                    <input 
                        type="text" 
                        class="search-input" 
                        placeholder="Search country..." 
                        bind:value={countrySearch}
                        autofocus
                    />
                    <div class="options-list">
                        {#each filteredCountries as c}
                            <button type="button" class="option-item" on:click={() => selectCountry(c)}>
                                <span class="fi fi-{c.lowerCode}"></span>
                                <span class="opt-text">{c.name}</span>
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>

        <button class="submit" on:click={handleSignup} disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
        </button>

    {:else}

        <input 
            class:invalid={invalidFields.email} 
            bind:value={signinForm.email} 
            type="email" 
            placeholder="Email *"
        >
        
        <input 
            class:invalid={invalidFields.pwd} 
            bind:value={signinForm.pwd} 
            type="password" 
            placeholder="Password *"
        >

        <button class="submit" on:click={handleSignin} disabled={loading}>
            {loading ? "Signing In..." : "Sign In"}
        </button>

    {/if}

    {#if error}
        <div class="error">{error}</div>
    {/if}

</div>

{/if}

</div>

<style>
:root {
    --bg-color: #0B1325;
    --card-bg: #152238;
    --text-color: #E2E8F0;
    --text-muted: #94A3B8;
    --border-color: #2D3E50;
    --primary-teal: #00A3C4;
    --primary-teal-hover: #0082A0;
    --gradient-btn: linear-gradient(135deg, #00A3C4 0%, #0068A8 100%);
    --gradient-btn-hover: linear-gradient(135deg, #00BBE2 0%, #007CC9 100%);
    --accent-amber: #E67E22;
    --tab-inactive: #1E2D42;
    --error-red: #EF4444;
    --success-teal: #10B981;
}

:global(body){
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg-color);
    color: var(--text-color);
}

.app-brand {
    position: fixed;
    top: 1.5rem;
    left: 1.5rem;
    display: flex;
    align-items: center;
    z-index: 2000;
}

.brand-logo {
    height: 48px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));
}

.container{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 2rem;
    box-sizing: border-box;
}

.card{
    width: 420px;
    background: var(--card-bg);
    padding: 2.2rem;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
}

h1{
    margin-top: 0;
    text-align: center;
    color: #FFFFFF;
    font-size: 1.6rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.tabs{
    display: flex;
    gap: .5rem;
    margin-bottom: 1.5rem;
    background: var(--bg-color);
    padding: 4px;
    border-radius: 10px;
}

.tabs button{
    flex: 1;
    padding: .7rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    background: transparent;
    color: var(--text-muted);
    font-weight: 600;
    transition: all 0.2s ease;
}

.tabs button.active{
    background: var(--primary-teal);
    color: #FFFFFF;
    box-shadow: 0 2px 8px rgba(0, 163, 196, 0.3);
}

.field-container {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    margin-bottom: 1rem;
}

.field-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-muted);
    padding-left: 2px;
}

input{
    width: 100%;
    padding: .8rem 1rem;
    margin-bottom: 1rem;
    box-sizing: border-box;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: .95rem;
    background: #0D172A;
    color: var(--text-color);
    outline: none;
    transition: border-color 0.2s ease;
    color-scheme: dark;
}

.field-container input {
    margin-bottom: 0;
}

input:focus {
    border-color: var(--primary-teal);
}

input.invalid, .select-btn.invalid {
    border-color: var(--error-red) !important;
    background: rgba(239, 68, 68, 0.05);
}

.phone-group {
    display: flex;
    gap: .5rem;
    margin-bottom: 1rem;
}

.phone-group input {
    margin-bottom: 0;
}

.custom-select {
    position: relative;
}

.prefix-select {
    width: 38%;
}

.full-width {
    width: 100%;
    margin-bottom: 1rem;
}

.select-btn {
    width: 100%;
    padding: .8rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: #0D172A;
    color: var(--text-color);
    display: flex;
    align-items: center;
    gap: .5rem;
    cursor: pointer;
    font-size: .95rem;
    box-sizing: border-box;
    height: 44px;
    text-align: left;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #121D30;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    z-index: 1000;
    padding: .5rem;
    margin-top: .2rem;
}

.search-input {
    width: 100%;
    padding: .5rem;
    margin-bottom: .5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    box-sizing: border-box;
    background: #080E1A;
    color: var(--text-color);
}

.options-list {
    max-height: 180px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.option-item {
    display: flex;
    align-items: center;
    gap: .5rem;
    padding: .6rem;
    border: none;
    background: transparent;
    color: var(--text-color);
    text-align: left;
    cursor: pointer;
    width: 100%;
    border-radius: 4px;
}

.option-item:hover {
    background: #1A283D;
    color: #FFFFFF;
}

.opt-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.submit{
    width: 100%;
    padding: .85rem;
    border: none;
    border-radius: 8px;
    background: var(--gradient-btn);
    color: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    margin-top: .5rem;
    transition: all 0.2s ease;
}

.submit:hover {
    background: var(--gradient-btn-hover);
    box-shadow: 0 4px 14px rgba(0, 163, 196, 0.4);
}

.submit:disabled{
    opacity: .5;
    cursor: not-allowed;
}

/* Success Redirect Box Styling */
.success-box {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--success-teal);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 1rem;
}

.success-icon {
    font-size: 2.2rem;
    margin-bottom: .5rem;
}

.success-box p {
    color: #A7F3D0;
    font-size: 0.95rem;
    line-height: 1.4;
    margin: 0 0 1rem 0;
}

.link-btn {
    background: transparent;
    border: none;
    color: var(--primary-teal);
    font-weight: 600;
    cursor: pointer;
    text-decoration: underline;
    font-size: 0.9rem;
}

.error{
    margin-top: 1rem;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid var(--error-red);
    color: #FCA5A5;
    padding: .75rem;
    border-radius: 8px;
    word-break: break-word;
    font-size: .9rem;
}

pre{
    background: #0D172A;
    color: #38BDF8;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
    overflow: auto;
    white-space: pre-wrap;
}
</style>