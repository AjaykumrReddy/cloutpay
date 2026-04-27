<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { authStore, authToken, displayName, updateProfile } from '$lib/auth';
  import { AuthError, getMyBadges, type Badge } from '$lib/api';
  import { toast } from '$lib/toast';

  let name = $state(get(displayName) ?? '');
  let loading = $state(false);
  let badges = $state<Badge[]>([]);

  onMount(async () => {
    const token = get(authToken);
    if (!token) return;
    try {
      badges = await getMyBadges(token);
    } catch {}
  });

  async function handleSave() {
    const trimmed = name.trim();
    if (trimmed.length < 2) {
      toast.error('Name must be at least 2 characters');
      return;
    }
    if (trimmed.length > 30) {
      toast.error('Name must be under 30 characters');
      return;
    }

    const token = get(authToken);
    if (!token) {
      goto('/login');
      return;
    }

    loading = true;
    try {
      const saved = await updateProfile(token, trimmed);
      authStore.setDisplayName(saved);
      toast.success('Profile updated');
      goto('/');
    } catch (e: any) {
      if (e instanceof AuthError) {
        authStore.clear();
        toast.error(e.message);
        goto('/login');
        return;
      }
      toast.error(e?.message || 'Failed to update profile');
    } finally {
      loading = false;
    }
  }
</script>

<div class="page">
  <div class="glow"></div>

  <div class="card">
    <div class="topline">
      <a href="/" class="back">Back to home</a>
      <a href="/history" class="secondary-link">View history</a>
    </div>

    <h1>Edit Profile</h1>
    <p class="sub">Keep your public name sharp so your contributions look intentional on the board.</p>

    <label class="label" for="display-name">Display name</label>
    <input
      id="display-name"
      type="text"
      class="name-input"
      placeholder="Your display name"
      maxlength="30"
      bind:value={name}
      disabled={loading}
      onkeydown={(event) => event.key === 'Enter' && handleSave()}
    />

    <p class="hint">This name is used on the leaderboard and in your payment history.</p>

    {#if badges.length > 0}
      <div class="badges-section">
        <p class="badges-label">Your badges</p>
        <div class="badges-grid">
          {#each badges as badge}
            <div class="badge-item" class:earned={badge.earned} title={badge.desc}>
              <span class="badge-emoji">{badge.emoji}</span>
              <span class="badge-name">{badge.label}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <button class="btn primary" onclick={handleSave} disabled={loading}>
      {loading ? 'Saving...' : 'Save changes'}
    </button>
    <button class="btn ghost" onclick={() => goto('/')} disabled={loading}>Cancel</button>
  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle at top, #1a1a1a, #0a0a0a 58%);
    position: relative;
    font-family: 'Inter', sans-serif;
    color: white;
    padding: 100px 20px 40px;
    box-sizing: border-box;
    overflow-x: hidden;
  }

  .glow {
    position: absolute;
    width: 520px;
    height: 520px;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    background: radial-gradient(circle, rgba(255, 90, 90, 0.22), transparent 62%);
    filter: blur(120px);
    pointer-events: none;
  }

  .card {
    box-sizing: border-box;
    width: min(420px, 100%);
    padding: 34px;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    position: relative;
    z-index: 1;
  }

  .topline {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }

  .back,
  .secondary-link {
    color: #9b9b9b;
    text-decoration: none;
    font-size: 13px;
  }

  h1 {
    margin: 0 0 8px;
    font-size: 2rem;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .sub {
    margin: 0 0 22px;
    color: #a0a0a0;
    line-height: 1.5;
    font-size: 14px;
  }

  .label {
    display: block;
    margin-bottom: 8px;
    font-size: 13px;
    color: #c7c7c7;
  }

  .name-input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    color: white;
    font-size: 16px;
    padding: 14px 16px;
    outline: none;
  }

  .hint {
    margin: 10px 0 20px;
    color: #7e7e7e;
    font-size: 12px;
  }

  .btn {
    width: 100%;
    border-radius: 14px;
    padding: 13px 16px;
    font-weight: 700;
    font-size: 15px;
    cursor: pointer;
  }

  .btn.primary {
    border: none;
    color: black;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
  }

  .btn.ghost {
    margin-top: 10px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
    color: white;
  }

  .btn:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .badges-section {
    margin-bottom: 20px;
  }

  .badges-label {
    margin: 0 0 10px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #555;
    font-weight: 700;
  }

  .badges-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }

  .badge-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    padding: 12px 8px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    background: rgba(255, 255, 255, 0.03);
    opacity: 0.3;
    filter: grayscale(1);
    transition: opacity 0.2s, filter 0.2s;
  }

  .badge-item.earned {
    opacity: 1;
    filter: none;
    border-color: rgba(255, 204, 0, 0.2);
    background: rgba(255, 204, 0, 0.05);
  }

  .badge-emoji {
    font-size: 1.5rem;
    line-height: 1;
  }

  .badge-name {
    font-size: 10px;
    font-weight: 700;
    color: #aaa;
    text-align: center;
    letter-spacing: 0.3px;
  }

  .badge-item.earned .badge-name {
    color: #ffdf71;
  }

  @media (max-width: 540px) {
    .card {
      padding: 28px 20px;
    }

    .topline {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
