<script>
    import { signup, signin } from "./lib/api/auth";
    import { onMount, onDestroy } from 'svelte';
    import { 
        getProfile, 
        updateProfile, 
        updateProfilePhoto, 
        changePassword,
        changeEmail,
        changePhone,
        getfriends,
        getPhotoUrl
    } from "./lib/api/users";
    import { searchUsers } from "./lib/api/search_engine";
    import { 
        sendFriendRequest, 
        acceptFriendRequest, 
        rejectFriendRequest, 
        removeFriendship, 
        removeFriendRequest,
        BlockFriend, 
        UnblockFriend 
    } from "./lib/api/friendships";
    import { fetchParseHandlerForFiles } from "./lib/api/http";
    import CountryData from "country-list-with-dial-code-and-flag";
    import logo from "./assets/logo.png";

    const API_URL = import.meta.env.VITE_API_URL;

    const rawCountries = Array.isArray(CountryData) 
        ? CountryData 
        : (CountryData?.default || []);

    const countries = rawCountries.map(c => ({
        ...c,
        lowerCode: c.code ? c.code.toLowerCase() : ""
    }));

    let mode = "signin";

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
        gender: "",
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

    // Authenticated App State
    let activeTab = "profile";
    let profileData = null;
    let profilePhotoUrl = null;
    let loadingProfile = false;
    
    // Tracks the specific profile currently being viewed (null = logged-in user)
    let activeProfileUsername = null; 

    // Search Feature State
    let searchQuery = "";
    let searchResults = [];
    let isSearching = false;
    let searchPhotoUrls = {};
    let _prevSearchPhotoUrls = [];
    let friendsPhotoUrls = {};
    let _prevFriendsPhotoUrls = [];

    // Friends Feature State
    let friendsList = [];
    let totalFriends = 0;
    let loadingFriends = false;

    // Edit Profile Modal State
    let isEditModalOpen = false;
    let isPhotoModalOpen = false;
    let photoFile = null;
    let isSettingsMenuOpen = false;
    let isSettingsModalOpen = false;
    let settingsAction = "";
    let settingsCurrentPassword = "";
    let settingsNewValue = "";
    let settingsConfirmValue = "";
    let settingsPhonePrefix = selectedPhonePrefix;
    let settingsPhoneNumber = "";
    let settingsPhoneDropdownOpen = false;
    let settingsPhoneSearch = "";
    let settingsError = "";
    let settingsLoading = false;

    let editForm = {
        username: "",
        name: "",
        bio: "",
        country: "",
        gender: "",
        dob: ""
    };

    let phoneDropdownOpen = false;
    let countryDropdownOpen = false;
    let phoneSearch = "";
    let countrySearch = "";

    $: filteredPhoneCountries = countries.filter(c => 
        c.name.toLowerCase().includes(phoneSearch.toLowerCase()) ||
        c.dial_code.includes(phoneSearch) ||
        c.code.toLowerCase().includes(phoneSearch.toLowerCase())
    );

    $: filteredCountries = countries.filter(c => 
        c.name.toLowerCase().includes(countrySearch.toLowerCase()) ||
        c.code.toLowerCase().includes(countrySearch.toLowerCase())
    );

    $: filteredSettingsPhoneCountries = countries.filter(c => 
        c.name.toLowerCase().includes(settingsPhoneSearch.toLowerCase()) ||
        c.dial_code.includes(settingsPhoneSearch) ||
        c.code.toLowerCase().includes(settingsPhoneSearch.toLowerCase())
    );

    function getPayloadFromToken(jwtToken) {
        if (!jwtToken) return null;
        try {
            const base64Url = jwtToken.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (e) {
            console.error("Failed to decode token", e);
            return null;
        }
    }

    function formatApiError(err, fallbackMessage) {
        const detail = err?.detail;

        if (Array.isArray(detail) && detail.length > 0) {
            const messages = detail
                .map((item) => item?.msg || item?.message)
                .filter(Boolean);

            if (messages.length > 0) {
                return messages.join(" ");
            }
        }

        if (typeof detail === "string" && detail.trim()) {
            return detail;
        }

        return fallbackMessage;
    }

    function getMyUsername() {
        const payload = getPayloadFromToken(token);
        return payload?.username || null;
    }

    function getUsernameFromPath() {
        const path = window.location.pathname.replace(/^\/+|\/+$/g, "");
        if (!path) return null;

        return path.split("/")[0].toLowerCase();
    }

    activeProfileUsername = getUsernameFromPath();

    async function fetchUserProfile(targetUsername = null) {
        if (!token) return;

        if (targetUsername) {
            activeProfileUsername = targetUsername;
        } else if (!activeProfileUsername) {
            activeProfileUsername = getUsernameFromPath() || getMyUsername();
        }

        const usernameToFetch = activeProfileUsername;

        if (!usernameToFetch) {
            error = "Invalid or expired session. Please sign in again.";
            logout();
            return;
        }

        loadingProfile = true;
        error = "";

        try {
            const data = await getProfile(token, usernameToFetch);
            profileData = data;
            
            editForm = {
                username: data.username || "",
                name: data.name || "",
                bio: data.bio || "",
                country: data.country || "US",
                gender: data.gender || "",
                dob: data.dob || ""
            };

            await fetchPhoto(usernameToFetch);
        } catch (err) {
            console.error("Error loading profile:", err);
            error = err?.detail || "Failed to load profile details.";
        } finally {
            loadingProfile = false;
        }
    }

    async function fetchPhoto(username) {
        if (!username) return;
        try {
            // Append timestamp to bypass browser blob caching on photo update
            const timestamp = new Date().getTime();
            const blob = await fetchParseHandlerForFiles(`${API_URL}/${username}/photo?t=${timestamp}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (blob) {
                if (profilePhotoUrl) URL.revokeObjectURL(profilePhotoUrl);
                profilePhotoUrl = URL.createObjectURL(blob);
            } else {
                profilePhotoUrl = null;
            }
        } catch (err) {
            console.error("Failed to load photo", err);
            profilePhotoUrl = null;
        }
    }

    function viewUserProfile(targetUsername) {
        if (!targetUsername) return;
        isSettingsMenuOpen = false;
        activeProfileUsername = targetUsername;
        profileData = null;
        activeTab = "profile";
        fetchUserProfile(targetUsername);
    }

    function viewMyProfile() {
        const myUsername = getMyUsername();
        isSettingsMenuOpen = false;
        activeProfileUsername = myUsername;
        profileData = null;
        activeTab = "profile";
        fetchUserProfile(myUsername);
    }

    async function handleSearch() {
        if (!searchQuery.trim()) return;
        isSearching = true;
        error = "";

        try {
            const results = await searchUsers(token, searchQuery, 10);
            searchResults = results || [];
            fetchSearchPhotos(searchResults);
        } catch (err) {
            console.error("Search failed:", err);
            searchResults = [];
            error = err?.detail || "No users found.";
        } finally {
            isSearching = false;
        }
    }

    function clearSearchPhotoUrls() {
        for (const url of _prevSearchPhotoUrls) {
            try { URL.revokeObjectURL(url); } catch (e) {}
        }
        _prevSearchPhotoUrls = [];
        searchPhotoUrls = {};
    }

    async function fetchSearchPhotos(results) {
        clearSearchPhotoUrls();
        if (!results || !results.length) return;
        const promises = results.map(async (user) => {
            try {
                const url = await getPhotoUrl(token, user.username);
                if (url) {
                    searchPhotoUrls = { ...searchPhotoUrls, [user.username]: url };
                    _prevSearchPhotoUrls.push(url);
                }
            } catch (e) {
                // ignore per-user failures
            }
        });
        await Promise.all(promises);
    }

    async function fetchFriendsList() {
        if (!token) return;
        const myUsername = getMyUsername();
        if (!myUsername) return;

        loadingFriends = true;
        try {
            const res = await getfriends(token, myUsername);
            friendsList = res.friends || [];
            totalFriends = res.total_friends || 0;
            fetchFriendsPhotos(friendsList);
        } catch (err) {
            console.error("Error fetching friends:", err);
        } finally {
            loadingFriends = false;
        }
    }

    function clearFriendsPhotoUrls() {
        for (const url of _prevFriendsPhotoUrls) {
            try { URL.revokeObjectURL(url); } catch (e) {}
        }
        _prevFriendsPhotoUrls = [];
        friendsPhotoUrls = {};
    }

    async function fetchFriendsPhotos(results) {
        clearFriendsPhotoUrls();
        if (!results || !results.length) return;
        const promises = results.map(async (user) => {
            try {
                const url = await getPhotoUrl(token, user.username);
                if (url) {
                    friendsPhotoUrls = { ...friendsPhotoUrls, [user.username]: url };
                    _prevFriendsPhotoUrls.push(url);
                }
            } catch (e) {
                // ignore per-user failures
            }
        });
        await Promise.all(promises);
    }

    async function handleSendRequest() {
        const payload = getPayloadFromToken(token);
        try {
            await sendFriendRequest(token, {
                sender_id: payload.id,
                receiver_id: profileData.viwed_id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not send friend request.";
        }
    }

    async function handleAcceptRequest() {
        const payload = getPayloadFromToken(token);
        try {
            await acceptFriendRequest(token, {
                sender_id: profileData.viwed_id,
                receiver_id: payload.id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not accept friend request.";
        }
    }

    async function handleRejectRequest() {
        const payload = getPayloadFromToken(token);
        try {
            await rejectFriendRequest(token, {
                sender_id: profileData.viwed_id,
                receiver_id: payload.id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not reject friend request.";
        }
    }

    async function handleRemoveFriendship() {
        const payload = getPayloadFromToken(token);
        try {
            await removeFriendship(token, {
                sender_id: payload.id,
                receiver_id: profileData.viwed_id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not remove friend.";
        }
    }

    async function handleRemoveFriendRequest() {
        const payload = getPayloadFromToken(token);
        try {
            await removeFriendRequest(token, {
                sender_id: payload.id,
                receiver_id: profileData.viwed_id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not remove friend request.";
        }
    }

    async function handleBlockUser() {
        const payload = getPayloadFromToken(token);
        try {
            await BlockFriend(token, {
                blocker_id: payload.id,
                blocked_id: profileData.viwed_id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not block user.";
        }
    }

    async function handleUnblockUser() {
        const payload = getPayloadFromToken(token);
        try {
            await UnblockFriend(token, {
                blocker_id: payload.id,
                blocked_id: profileData.viwed_id
            });
            await fetchUserProfile(profileData.username);
        } catch (err) {
            error = err?.detail || "Could not unblock user.";
        }
    }

    async function handleUpdateProfile() {
        const myUsername = getMyUsername();
        if (!myUsername) return;

        try {
            const updatePayload = {};
            if (editForm.username && editForm.username !== myUsername) updatePayload.username = editForm.username;
            if (editForm.name) updatePayload.name = editForm.name;
            if (editForm.bio !== undefined) updatePayload.bio = editForm.bio;
            if (editForm.country) updatePayload.country = editForm.country;
            if (editForm.gender) updatePayload.gender = editForm.gender;
            if (editForm.dob) updatePayload.dob = editForm.dob;

            const res = await updateProfile(token, myUsername, updatePayload);
            
            // SAVE AND REPLACE JWT TOKEN IMMEDIATELY
            if (res?.token) {
                token = res.token;
                localStorage.setItem("token", token);
            }

            isEditModalOpen = false;
            const updatedUsername = updatePayload.username || myUsername;
            activeProfileUsername = updatedUsername;
            await fetchUserProfile(updatedUsername);
        } catch (err) {
            error = err?.detail || "Failed to update profile.";
        }
    }

    async function handleUpdatePhoto() {
        if (!photoFile) return;
        const myUsername = getMyUsername();
        if (!myUsername) return;

        try {
            const res = await updateProfilePhoto(token, myUsername, photoFile);
            
            // SAVE AND REPLACE JWT TOKEN IMMEDIATELY
            if (res?.token) {
                token = res.token;
                localStorage.setItem("token", token);
            }

            isPhotoModalOpen = false;
            photoFile = null;

            // Re-fetch profile and fresh photo blob
            await fetchUserProfile(myUsername);
        } catch (err) {
            error = err?.detail || "Failed to update profile photo.";
        }
    }

    function resetSettingsState() {
        isSettingsMenuOpen = false;
        isSettingsModalOpen = false;
        settingsAction = "";
        settingsCurrentPassword = "";
        settingsNewValue = "";
        settingsConfirmValue = "";
        settingsPhonePrefix = selectedPhonePrefix;
        settingsPhoneNumber = "";
        settingsPhoneDropdownOpen = false;
        settingsPhoneSearch = "";
        settingsError = "";
        settingsLoading = false;
    }

    function openSettingsAction(action) {
        settingsAction = action;
        settingsCurrentPassword = "";
        settingsNewValue = "";
        settingsConfirmValue = "";
        settingsPhonePrefix = selectedPhonePrefix;
        settingsPhoneNumber = "";
        settingsPhoneDropdownOpen = false;
        settingsPhoneSearch = "";
        settingsError = "";
        settingsLoading = false;
        isSettingsMenuOpen = false;
        isSettingsModalOpen = true;
    }

    function closeSettingsModal() {
        resetSettingsState();
    }

    async function handleSettingsSave() {
        const currentPassword = settingsCurrentPassword.trim();
        const nextValue = settingsNewValue.trim();

        if (!currentPassword) {
            settingsError = "Current password is required.";
            return;
        }

        if (settingsAction === "password") {
            if (!nextValue) {
                settingsError = "Please provide the new password.";
                return;
            }

            if (!settingsConfirmValue.trim()) {
                settingsError = "Please confirm the new password.";
                return;
            }

            if (settingsNewValue !== settingsConfirmValue) {
                settingsError = "New passwords do not match.";
                return;
            }
        }

        settingsLoading = true;
        settingsError = "";

        try {
            if (settingsAction === "password") {
                await changePassword(token, currentPassword, nextValue);
            } else if (settingsAction === "email") {
                await changeEmail(token, currentPassword, nextValue);
            } else if (settingsAction === "phone") {
                const phoneNumber = settingsPhoneNumber.trim();
                if (!phoneNumber) {
                    settingsError = "Please provide the new phone number.";
                    settingsLoading = false;
                    return;
                }

                await changePhone(token, currentPassword, `${settingsPhonePrefix} ${phoneNumber}`);
            }

            closeSettingsModal();
        } catch (err) {
            settingsError = formatApiError(err, "Failed to update settings.");
        } finally {
            settingsLoading = false;
        }
    }

    $: if (token && activeTab === "profile" && !profileData && !loadingProfile && !error) {
        fetchUserProfile(activeProfileUsername);
    }

    $: if (token && activeTab === "friends") {
        fetchFriendsList();
    }

    function selectPhoneCountry(country) {
        selectedPhonePrefix = country.dial_code;
        phoneDropdownOpen = false;
        phoneSearch = "";
    }

    function selectSettingsPhoneCountry(country) {
        settingsPhonePrefix = country.dial_code;
        settingsPhoneDropdownOpen = false;
        settingsPhoneSearch = "";
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

    function validateSignup() {
        invalidFields = {};
        const missing = [];

        if (!signupForm.username.trim()) { invalidFields.username = true; missing.push("username"); }
        if (!signupForm.name.trim()) { invalidFields.name = true; missing.push("full name"); }
        if (!signupForm.email.trim()) { invalidFields.email = true; missing.push("email"); }
        if (!rawPhoneNumber.trim()) { invalidFields.phone = true; missing.push("phone number"); }
        if (!signupForm.pwd_hash.trim()) { invalidFields.pwd_hash = true; missing.push("password"); }
        if (!signupForm.dob.trim()) { invalidFields.dob = true; missing.push("date of birth"); }
        if (!signupForm.gender.trim()) { invalidFields.gender = true; missing.push("gender"); }
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
                error = "Password must be at least 8 characters long and contain letters, numbers, and special characters.";
            } else if (err?.detail === "USER_UNDERAGE") {
                error = "You must be at least 18 years old to create an account.";
            } else if (err?.status === 422) {
                error = err?.data?.detail?.[0]?.msg || "Invalid input received";
            } else {
                error = "An unexpected error occurred during sign up. Please try again.";
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
            viewMyProfile();
        } catch (err) {
            if (err?.detail === "INVALID_CREDENTIALS") {
                error = "Invalid email or password.";
            } else if (err?.detail === "USER_SUSPENDED") {
                error = "Your account has been suspended. Please contact support.";
            } else {
                error = "An unexpected error occurred during sign in. Please try again.";
                console.error(err);
            }
        }

        loading = false;
    }

    function logout() {
        localStorage.removeItem("token");
        if (profilePhotoUrl) URL.revokeObjectURL(profilePhotoUrl);
        token = null;
        profileData = null;
        profilePhotoUrl = null;
        activeProfileUsername = null;
        resetSettingsState();
    }

    // Listen for global unauthorized events from fetch helpers
    let _u3_unauth_handler = (ev) => {
        const reason = ev?.detail?.reason || 'Session expired. Please sign in again.';
        error = reason;
        logout();
    }

    onMount(() => {
        window.addEventListener('u3:logout', _u3_unauth_handler);
    });

    onDestroy(() => {
        window.removeEventListener('u3:logout', _u3_unauth_handler);
    });
</script>

<svelte:head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.0.0/css/flag-icons.min.css" />
</svelte:head>

<header class="app-brand">
    <img src={logo} alt="U3 Choice Logo" class="brand-logo" />
</header>

<div class="container">

{#if token}
    <div class="app-screen">

        <header class="top-nav">
            {#if activeTab === 'profile' && profileData}
                <div class="username-header">
                    <h2>@{profileData.username}</h2>
                    {#if profileData.verified}
                        <span class="badge-verified" title="Verified Account">✓</span>
                    {/if}
                </div>
            {:else if activeTab === 'home'}
                <h2>Feed</h2>
            {:else if activeTab === 'search'}
                <h2>Explore Users</h2>
            {:else if activeTab === 'friends'}
                <h2>My Friends ({totalFriends})</h2>
            {:else}
                <h2>Profile</h2>
            {/if}

            <button class="logout-link" on:click={logout}>Logout</button>
        </header>

        <main class="content-body">
            {#if error}
                <div class="error-banner">{error} <button on:click={() => error = ""}>×</button></div>
            {/if}

            {#if activeTab === "home"}
                <div class="empty-state">
                    <span class="icon">🏠</span>
                    <h3>Home Feed Unavailable</h3>
                    <p>No posts to display right now. Check back later!</p>
                </div>

            {:else if activeTab === "search"}
                <div class="search-container">
                    <form class="search-bar" on:submit|preventDefault={handleSearch}>
                        <input 
                            type="text" 
                            placeholder="Search by name or @username..." 
                            bind:value={searchQuery}
                        />
                        <button type="submit" disabled={isSearching}>
                            {isSearching ? "..." : "Search"}
                        </button>
                    </form>

                    {#if isSearching}
                        <div class="loading-spinner">Searching users...</div>
                    {:else if searchResults.length > 0}
                        <div class="results-grid">
                            {#each searchResults as user}
                                <div class="user-card" on:click={() => viewUserProfile(user.username)}>
                                    <div class="user-avatar-small">
                                        {#if searchPhotoUrls[user.username]}
                                            <img src={searchPhotoUrls[user.username]} alt={user.username} />
                                        {:else if user.photo_url && user.photo_url !== 'assets/default_profile.png'}
                                            <img src={`${API_URL}/${user.username}/photo`} alt={user.username} />
                                        {:else}
                                            <div class="avatar-placeholder-small">{user.name ? user.name[0].toUpperCase() : 'U'}</div>
                                        {/if}
                                    </div>
                                    <div class="user-details">
                                        <h4>{user.name}</h4>
                                        <p>@{user.username}</p>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {:else if searchQuery}
                        <div class="empty-state">
                            <span class="icon">🔍</span>
                            <p>No user accounts matched your search keyword.</p>
                        </div>
                    {/if}
                </div>

            {:else if activeTab === "friends"}
                {#if loadingFriends}
                    <div class="loading-spinner">Loading friends...</div>
                        {:else if friendsList.length > 0}
                    <div class="results-grid">
                        {#each friendsList as friend}
                            <div class="user-card" on:click={() => viewUserProfile(friend.username)}>
                                <div class="user-avatar-small">
                                    {#if friendsPhotoUrls[friend.username]}
                                        <img src={friendsPhotoUrls[friend.username]} alt={friend.username} />
                                    {:else if friend.photo_url && friend.photo_url !== 'assets/default_profile.png'}
                                        <img src={`${API_URL}/${friend.username}/photo`} alt={friend.username} />
                                    {:else}
                                        <div class="avatar-placeholder-small">{friend.name ? friend.name[0].toUpperCase() : 'U'}</div>
                                    {/if}
                                </div>
                                <div class="user-details">
                                    <h4>{friend.name}</h4>
                                    <p>@{friend.username}</p>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="empty-state">
                        <span class="icon">👥</span>
                        <h3>No Friends Yet</h3>
                        <p>Search for friends and connect with them!</p>
                    </div>
                {/if}

            {:else if activeTab === "profile"}
                {#if loadingProfile}
                    <div class="loading-spinner">Loading Profile...</div>
                {:else if profileData}
                    <div class="profile-card">

                        <div class="profile-header">
                            <div class="avatar-wrapper">
                                {#if profilePhotoUrl}
                                    <img src={profilePhotoUrl} alt={profileData.username} class="avatar-img" />
                                {:else}
                                    <div class="avatar-placeholder">
                                        {profileData.name ? profileData.name[0].toUpperCase() : 'U'}
                                    </div>
                                {/if}
                            </div>
                            
                            <div class="profile-info">
                                <h3 class="display-name">{profileData.name}</h3>
                                <p class="user-handle">@{profileData.username}</p>
                                {#if profileData.country}
                                    <span class="country-tag">
                                        <span class="fi fi-{profileData.country.toLowerCase()}"></span>
                                        {profileData.country}
                                    </span>
                                {/if}
                            </div>
                        </div>

                        {#if profileData.bio}
                            <div class="bio-box">
                                <p>{profileData.bio}</p>
                            </div>
                        {/if}

                        <div class="action-bar">
                            {#if profileData.is_owner}
                                <button class="btn-secondary" on:click={() => isEditModalOpen = true}>Edit Profile</button>
                                <button class="btn-secondary" on:click={() => isPhotoModalOpen = true}>Change Photo</button>
                                <div class="settings-menu">
                                    <button
                                        type="button"
                                        class="settings-trigger"
                                        aria-haspopup="menu"
                                        aria-expanded={isSettingsMenuOpen}
                                        on:click={() => isSettingsMenuOpen = !isSettingsMenuOpen}>
                                        ⚙
                                    </button>

                                    {#if isSettingsMenuOpen}
                                        <div class="settings-dropdown" role="menu">
                                            <button type="button" on:click={() => openSettingsAction("password")}>Change Password</button>
                                            <button type="button" on:click={() => openSettingsAction("email")}>Change Email</button>
                                            <button type="button" on:click={() => openSettingsAction("phone")}>Change Phone</button>
                                        </div>
                                    {/if}
                                </div>
                            {:else if profileData.they_blocked_me}
                                <button class="btn-secondary" disabled>You got blocked</button>
                            {:else}
                                {#if profileData.i_blocked_them}
                                    <button class="btn-secondary" on:click={handleUnblockUser}>Unblock User</button>
                                {:else}
                                    {#if profileData.is_friends}
                                        <button class="btn-primary" on:click={() => { /* message no-op for now */ }}>Message</button>
                                        <button class="btn-secondary danger" on:click={handleRemoveFriendship}>Remove Friend</button>
                                    {:else if profileData.has_sent_friendship_request}
                                        <button class="btn-primary" on:click={handleAcceptRequest}>Accept Request</button>
                                        <button class="btn-secondary" on:click={handleRejectRequest}>Reject Request</button>
                                    {:else if profileData.has_received_friendship_request}
                                        <button class="btn-secondary" on:click={handleRemoveFriendRequest}>Cancel Request</button>
                                    {:else}
                                        <button class="btn-primary" on:click={handleSendRequest}>Add Friend</button>
                                    {/if}

                                    <button class="btn-secondary" on:click={handleBlockUser}>Block User</button>
                                {/if}
                            {/if}
                        </div>

                    </div>
                {/if}
            {/if}
        </main>

        <nav class="bottom-nav">
            <button 
                class="nav-item" 
                class:active={activeTab === 'home'} 
                on:click={() => activeTab = 'home'}>
                <span class="nav-icon">🏠</span>
                <span class="nav-label">Home</span>
            </button>

            <button 
                class="nav-item" 
                class:active={activeTab === 'search'} 
                on:click={() => activeTab = 'search'}>
                <span class="nav-icon">🔍</span>
                <span class="nav-label">Search</span>
            </button>

            <button 
                class="nav-item" 
                class:active={activeTab === 'friends'} 
                on:click={() => activeTab = 'friends'}>
                <span class="nav-icon">👥</span>
                <span class="nav-label">Friends</span>
            </button>

            <button 
                class="nav-item" 
                class:active={activeTab === 'profile'} 
                on:click={viewMyProfile}>
                <span class="nav-icon">👤</span>
                <span class="nav-label">Profile</span>
            </button>
        </nav>

    </div>

    <!-- Edit Profile Modal -->
    {#if isEditModalOpen}
        <div class="modal-overlay">
            <div class="modal-card">
                <h3>Edit Profile</h3>
                
                <input type="text" placeholder="Username" bind:value={editForm.username} />
                <input type="text" placeholder="Full Name" bind:value={editForm.name} />
                <textarea placeholder="Bio" bind:value={editForm.bio}></textarea>
                
                <select class="select-input" bind:value={editForm.gender}>
                    <option value="" disabled>Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                </select>

                <div class="field-container">
                    <label for="edit-dob" class="field-label">Date of Birth</label>
                    <input id="edit-dob" type="date" bind:value={editForm.dob} />
                </div>

                <div class="modal-actions">
                    <button class="btn-secondary" on:click={() => isEditModalOpen = false}>Cancel</button>
                    <button class="btn-primary" on:click={handleUpdateProfile}>Save Changes</button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Edit Photo Modal -->
    {#if isPhotoModalOpen}
        <div class="modal-overlay">
            <div class="modal-card">
                <h3>Upload Profile Photo</h3>
                <input type="file" accept="image/png, image/jpeg" on:change={(e) => photoFile = e.target.files[0]} />
                <div class="modal-actions">
                    <button class="btn-secondary" on:click={() => isPhotoModalOpen = false}>Cancel</button>
                    <button class="btn-primary" on:click={handleUpdatePhoto} disabled={!photoFile}>Upload</button>
                </div>
            </div>
        </div>
    {/if}

    {#if isSettingsModalOpen}
        <div class="modal-overlay">
            <div class="modal-card settings-modal">
                <h3>
                    {#if settingsAction === "password"}
                        Change Password
                    {:else if settingsAction === "email"}
                        Change Email
                    {:else}
                        Change Phone
                    {/if}
                </h3>

                <p class="modal-copy">Enter your current password and the new value in the same form.</p>

                <input
                    type="password"
                    placeholder="Current password"
                    bind:value={settingsCurrentPassword}
                    disabled={settingsLoading}
                />

                {#if settingsAction === "password"}
                    <input
                        type="password"
                        placeholder="New password"
                        bind:value={settingsNewValue}
                        disabled={settingsLoading}
                    />
                    <input
                        type="password"
                        placeholder="Confirm new password"
                        bind:value={settingsConfirmValue}
                        disabled={settingsLoading}
                    />
                {:else if settingsAction === "email"}
                    <input
                        type="email"
                        placeholder="New email"
                        bind:value={settingsNewValue}
                        disabled={settingsLoading}
                    />
                {:else}
                    <div class="phone-group settings-phone-group">
                        <div class="custom-select prefix-select settings-prefix-select">
                            <button type="button" class="select-btn" on:click={() => settingsPhoneDropdownOpen = !settingsPhoneDropdownOpen} disabled={settingsLoading}>
                                <span class="fi fi-{countries.find(c => c.dial_code === settingsPhonePrefix)?.lowerCode}"></span>
                                <span>{settingsPhonePrefix}</span>
                            </button>

                            {#if settingsPhoneDropdownOpen}
                                <div class="dropdown-menu">
                                    <input
                                        type="text"
                                        class="search-input"
                                        placeholder="Search code..."
                                        bind:value={settingsPhoneSearch}
                                        autofocus
                                    />
                                    <div class="options-list">
                                        {#each filteredSettingsPhoneCountries as c}
                                            <button type="button" class="option-item" on:click={() => selectSettingsPhoneCountry(c)}>
                                                <span class="fi fi-{c.lowerCode}"></span>
                                                <span class="opt-text">{c.name} ({c.dial_code})</span>
                                            </button>
                                        {/each}
                                    </div>
                                </div>
                            {/if}
                        </div>

                        <input
                            type="tel"
                            placeholder="New phone number"
                            bind:value={settingsPhoneNumber}
                            disabled={settingsLoading}
                        />
                    </div>
                {/if}

                {#if settingsError}
                    <div class="modal-error">{settingsError}</div>
                {/if}

                <div class="modal-actions">
                    <button class="btn-secondary" type="button" on:click={closeSettingsModal} disabled={settingsLoading}>Cancel</button>
                    <button class="btn-primary" type="button" on:click={handleSettingsSave} disabled={settingsLoading}>
                        {settingsLoading ? "Saving..." : "Save Changes"}
                    </button>
                </div>
            </div>
        </div>
    {/if}

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

        <div class="field-container">
            <label for="dob-input" class="field-label">Date of Birth *</label>
            <input
                id="dob-input"
                class:invalid={invalidFields.dob}
                bind:value={signupForm.dob}
                type="date"
            >
        </div>

        <select 
            class="select-input" 
            class:invalid={invalidFields.gender} 
            bind:value={signupForm.gender}>
            <option value="" disabled selected>Select Gender *</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
        </select>

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
    padding: 1rem;
    box-sizing: border-box;
}

.card{
    width: 100%;
    max-width: 460px;
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

input, textarea, .select-input{
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

textarea {
    min-height: 80px;
    resize: vertical;
}

input:focus, textarea:focus, .select-input:focus {
    border-color: var(--primary-teal);
}

input.invalid, .select-btn.invalid, .select-input.invalid {
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

.error-banner {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid var(--error-red);
    color: #FCA5A5;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.error-banner button {
    background: transparent;
    border: none;
    color: #FCA5A5;
    font-size: 1.2rem;
    cursor: pointer;
}

.app-screen {
    width: 100%;
    max-width: 900px;
    min-height: 650px;
    height: 85vh;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
    position: relative;
}

.top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.8rem;
    border-bottom: 1px solid var(--border-color);
    background: #0D172A;
}

.username-header {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.username-header h2, .top-nav h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.badge-verified {
    background: var(--primary-teal);
    color: white;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
}

.logout-link {
    background: transparent;
    border: none;
    color: var(--error-red);
    font-weight: 600;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 6px 12px;
    border-radius: 6px;
    transition: background 0.2s ease;
}

.logout-link:hover {
    background: rgba(239, 68, 68, 0.1);
}

.content-body {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    text-align: center;
}

.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
}

.search-bar {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.search-bar input {
    margin-bottom: 0;
}

.search-bar button {
    padding: 0 1.5rem;
    background: var(--gradient-btn);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
}

.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
}

.user-card {
    background: #0D172A;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 0.8rem;
    cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.user-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary-teal);
}

.user-avatar-small {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    border: 2px solid var(--primary-teal);
}

.user-avatar-small img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-placeholder-small {
    width: 100%;
    height: 100%;
    background: #1A283D;
    color: var(--primary-teal);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.user-details h4 {
    margin: 0;
    font-size: 0.95rem;
}

.user-details p {
    margin: 2px 0 0 0;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.bottom-nav {
    display: flex;
    border-top: 1px solid var(--border-color);
    background: #0D172A;
    height: 65px;
}

.nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    transition: color 0.2s ease;
}

.nav-item.active {
    color: var(--primary-teal);
}

.nav-icon {
    font-size: 1.3rem;
}

.nav-label {
    font-size: 0.8rem;
    margin-top: 2px;
}

.profile-card {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    max-width: 650px;
    margin: 0 auto;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.avatar-wrapper {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 3px solid var(--primary-teal);
    overflow: hidden;
    flex-shrink: 0;
}

.avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-placeholder {
    width: 100%;
    height: 100%;
    background: #1A283D;
    color: var(--primary-teal);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    font-weight: 700;
}

.display-name {
    margin: 0;
    font-size: 1.5rem;
}

.user-handle {
    margin: 4px 0 8px 0;
    color: var(--text-muted);
    font-size: 1rem;
}

.country-tag {
    font-size: 0.85rem;
    background: #0D172A;
    padding: 3px 10px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

.bio-box {
    background: #0D172A;
    padding: 1.2rem;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    font-size: 0.95rem;
    line-height: 1.5;
}

.action-bar {
    display: flex;
    gap: 0.8rem;
    align-items: stretch;
}

.action-bar button {
    flex: 1;
    padding: 0.85rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
}

.btn-primary {
    background: var(--gradient-btn);
    color: white;
    border: none;
    transition: background 0.2s ease;
}

.btn-primary:hover {
    background: var(--gradient-btn-hover);
}

.btn-secondary {
    background: transparent;
    color: var(--text-color);
    border: 1px solid var(--border-color);
}

.btn-secondary.danger {
    color: var(--error-red);
    border-color: var(--error-red);
}

.btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.settings-menu {
    position: relative;
    flex: 0 0 auto;
}

.settings-trigger {
    width: 48px;
    min-width: 48px;
    height: 100%;
    flex: 0 0 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    font-size: 1.1rem;
    border-radius: 8px;
    color: var(--primary-teal);
    background: #0D172A;
}

.settings-trigger:hover {
    border-color: var(--primary-teal);
}

.settings-dropdown {
    position: absolute;
    top: calc(100% + 0.45rem);
    right: 0;
    min-width: 180px;
    padding: 0.45rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background: #121D30;
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35);
    z-index: 40;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}

.settings-dropdown button {
    flex: initial;
    width: 100%;
    padding: 0.7rem 0.8rem;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: var(--text-color);
    text-align: left;
}

.settings-dropdown button:hover {
    background: rgba(0, 163, 196, 0.12);
    color: #FFFFFF;
}

.loading-spinner {
    text-align: center;
    color: var(--text-muted);
    padding-top: 3rem;
    font-size: 1.1rem;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 3000;
}

.modal-card {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    width: 90%;
    max-width: 420px;
}

.settings-modal {
    max-width: 460px;
}

.modal-card h3 {
    margin-top: 0;
    margin-bottom: 1rem;
}

.modal-copy {
    margin: -0.25rem 0 1rem 0;
    color: var(--text-muted);
    font-size: 0.92rem;
    line-height: 1.4;
}

.modal-error {
    margin-top: 0.75rem;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid var(--error-red);
    color: #FCA5A5;
    padding: 0.7rem 0.8rem;
    border-radius: 8px;
    word-break: break-word;
    font-size: 0.9rem;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.8rem;
    margin-top: 1rem;
}

.modal-actions button {
    padding: 0.6rem 1.2rem;
    border-radius: 6px;
    cursor: pointer;
}

@media (max-width: 600px) {
    .app-brand {
        top: 1rem;
        left: 1rem;
    }
    
    .brand-logo {
        height: 36px;
    }

    .container {
        padding: 0;
    }

    .app-screen {
        height: 100vh;
        border-radius: 0;
        border: none;
    }

    .profile-header {
        flex-direction: column;
        text-align: center;
    }

    .action-bar {
        flex-direction: column;
    }
}
</style>