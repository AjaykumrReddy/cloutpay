<script lang="ts">
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { authStore, authToken, updateProfile } from '$lib/auth';
  import { AuthError } from '$lib/api';
  import LocationPicker from '$lib/LocationPicker.svelte';
  import { toast } from '$lib/toast';

  let displayName = $state('');
  let city = $state('');
  let region = $state('');
  let loading = $state(false);

  async function handleSave() {
    const name = displayName.trim();
    if (name.length < 2) { toast.error('Name must be at least 2 characters'); return; }
    if (name.length > 30) { toast.error('Name must be under 30 characters'); return; }

    const token = get(authToken);
    if (!token) { goto('/login'); return; }

    loading = true;
    try {
      const result = await updateProfile(token, name, city || null, region || null);
      authStore.setDisplayName(result.display_name);
      authStore.setLocation(result.city, result.state);
      toast.success('Welcome to CloutPay 🔥');
      goto('/');
    } catch (e: any) {
      if (e instanceof AuthError) {
        authStore.clear();
        toast.error(e.message);
        goto('/login');
        return;
      }
      toast.error(e.message);
    } finally {
      loading = false;
    }
  }
</script>

<div class="page">
  <div class="glow"></div>

  <div class="card">
    <h1>CloutPay</h1>
    <p class="sub">Set up your profile 👤</p>
    <p class="hint">Your name appears on the leaderboard. You can change everything later.</p>

    <label class="label" for="dname">Display name <span class="req">*</span></label>
    <input
      id="dname"
      type="text"
      class="name-input"
      placeholder="Your display name"
      maxlength="30"
      bind:value={displayName}
      disabled={loading}
      onkeydown={(e) => e.key === 'Enter' && handleSave()}
    />

    <div class="location-section">
      <p class="location-label" id="city-label">Your city <span class="optional">optional</span></p>
      <p class="location-hint">Unlock local leaderboards after your first payment.</p>
      <div role="group" aria-labelledby="city-label">
        <LocationPicker bind:city bind:region disabled={loading} />
      </div>
    </div>

    <button class="btn" onclick={handleSave} disabled={loading || displayName.trim().length < 2}>
      {loading ? 'Saving...' : 'Save & Continue 🚀'}
    </button>
  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    background: radial-gradient(circle at top, #1a1a1a, #0a0a0a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    position: relative;
    padding: 100px 20px 40px;
    box-sizing: border-box;
  }

  .glow {
    position: absolute;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(255, 0, 0, 0.25), transparent);
    top: -100px;
    left: 50%;
    transform: translateX(-50%);
    filter: blur(120px);
    pointer-events: none;
  }

  .card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 40px 36px;
    width: min(380px, 100%);
    box-sizing: border-box;
    color: white;
    position: relative;
    z-index: 1;
  }

  h1 {
    font-size: 2rem;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px;
    text-align: center;
  }

  .sub { color: white; font-size: 17px; font-weight: 600; margin-bottom: 4px; text-align: center; }
  .hint { color: #666; font-size: 12px; margin-bottom: 24px; text-align: center; line-height: 1.5; }

  .label { display: block; font-size: 12px; font-weight: 700; color: #c7c7c7; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
  .req { color: #ff4d4d; }

  .name-input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    color: white;
    font-size: 16px;
    padding: 13px;
    outline: none;
    margin-bottom: 20px;
    transition: border-color 0.2s;
  }

  .name-input:focus { border-color: #ff4d4d; }
  .name-input::placeholder { color: #555; }

  .location-section { margin-bottom: 24px; }

  .location-label {
    font-size: 12px;
    font-weight: 700;
    color: #c7c7c7;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 4px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .optional {
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }

  .location-hint { font-size: 12px; color: #555; margin: 0 0 10px; }

  .btn {
    width: 100%;
    padding: 13px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    font-size: 15px;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .btn:disabled { opacity: 0.45; cursor: not-allowed; }

  @media (max-width: 540px) {
    .card { padding: 28px 20px; }
  }
</style>
