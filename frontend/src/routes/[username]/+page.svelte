<script>
    import { page } from '$app/state';
    import { getProfile } from '$lib/api';
    import { fetchParseHandlerForFiles } from '$lib/fetch';

    let profile = null;
    let profilePhotoUrl = null;
    let error = "";
    let loadingProfile = false;

    // Gets "tjay" from /tjay
    let username = page.params.username;

    async function fetchUserProfile() {
        if (!username) {
            error = "Invalid username.";
            return;
        }

        loadingProfile = true;
        error = "";

        try {
            // Fetch tjay's profile
            const data = await getProfile(token, username);

            profile = data;

            // Load tjay's photo
            await fetchPhoto(username);

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
            const timestamp = new Date().getTime();

            const blob = await fetchParseHandlerForFiles(
                `${API_URL}/${username}/photo?t=${timestamp}`,
                {
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );

            if (blob) {
                if (profilePhotoUrl) {
                    URL.revokeObjectURL(profilePhotoUrl);
                }

                profilePhotoUrl = URL.createObjectURL(blob);
            } else {
                profilePhotoUrl = null;
            }

        } catch (err) {
            console.error("Failed to load photo", err);
            profilePhotoUrl = null;
        }
    }

    fetchUserProfile();
</script>

{#if loadingProfile}
    <p>Loading...</p>

{:else if error}
    <p>{error}</p>

{:else if profile}
    <h1>{profile.username}</h1>
    <h2>{profile.name}</h2>
    <p>{profile.bio}</p>

    {#if profilePhotoUrl}
        <img src={profilePhotoUrl} alt="Profile" />
    {/if}
{/if}