<script lang="ts">
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { authStore, authToken, updateProfile } from '$lib/auth';
  import { toast } from '$lib/toast';

  let displayName = $state('');
  let loading = $state(false);

  async function handleSave() {
    const name = displayName.trim();
    if (name.length < 2) { toast.error('Name must be at least 2 characters'); return; }
    if (name.length > 30) { toast.error('Name must be under 30 characters'); return; }

    const token = get(authToken);
    if (!token) { goto('/login'); return; }

    loading = true;
    try {
      const saved = await updateProfile(token, name);
      authStore.setDisplayName(saved);
      toast.success('Profile saved 🎉');
      goto('/');
    } catch (e: any) {
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
    <p class="sub">What should we call you? 👤</p>
    <p class="hint">This name will appear on the leaderboard</p>

    <input
      type="text"
      class="name-input"
      placeholder="Your display name"
      maxlength="30"
      bind:value={displayName}
      disabled={loading}
      onkeydown={(e) => e.key === 'Enter' && handleSave()}
    />

    <button class="btn" onclick={handleSave} disabled={loading}>
      {loading ? 'Saving...' : 'Save & Continue 🚀'}
    </button>

    <button class="skip" onclick={() => goto('/')} disabled={loading}>
      Skip for now
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
    width: 360px;
    text-align: center;
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
  }

  .sub {
    color: white;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 6px;
  }

  .hint {
    color: #888;
    font-size: 13px;
    margin-bottom: 24px;
  }

  .name-input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    color: white;
    font-size: 16px;
    text-align: center;
    padding: 13px;
    outline: none;
    margin-bottom: 14px;
    transition: border-color 0.2s;
  }

  .name-input:focus { border-color: #ff4d4d; }
  .name-input::placeholder { color: #555; }

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

  .btn:disabled { opacity: 0.55; cursor: not-allowed; }

  .skip {
    display: block;
    width: 100%;
    margin-top: 12px;
    padding: 10px;
    background: none;
    border: none;
    color: #555;
    font-size: 13px;
    cursor: pointer;
    transition: color 0.2s;
  }

  .skip:hover { color: #888; }
</style>
