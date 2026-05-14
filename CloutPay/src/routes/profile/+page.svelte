<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { authStore, authToken, displayName, updateProfile } from '$lib/auth';
  import { AuthError, getMyBadges, getMySummary, getMyLocation, type Badge } from '$lib/api';
  import LocationPicker from '$lib/LocationPicker.svelte';
  import { toast } from '$lib/toast';

  let name = $state(get(displayName) ?? '');
  let loading = $state(false);
  let badges = $state<Badge[]>([]);
  let currentStreak = $state(0);
  let longestStreak = $state(0);
  let totalPaid = $state(0);
  let rank = $state<number | null>(null);
  let city = $state('');
  let region = $state('');

  onMount(async () => {
    const token = get(authToken);
    if (!token) return;
    try {
      const [b, summary, loc] = await Promise.all([
        getMyBadges(token),
        getMySummary(token),
        getMyLocation(token),
      ]);
      badges = b;
      currentStreak = summary.current_streak ?? 0;
      longestStreak = summary.longest_streak ?? 0;
      totalPaid = summary.total_contributed ?? 0;
      rank = summary.current_rank ?? null;
      city = loc.city ?? '';
      region = loc.state ?? '';
    } catch {}
  });

  async function handleSave() {
    const trimmed = name.trim();
    if (trimmed.length < 2) { toast.error('Name must be at least 2 characters'); return; }
    if (trimmed.length > 30) { toast.error('Name must be under 30 characters'); return; }

    const token = get(authToken);
    if (!token) { goto('/login'); return; }

    loading = true;
    try {
      const result = await updateProfile(token, trimmed, city || null, region || null);
      authStore.setDisplayName(result.display_name);
      authStore.setLocation(result.city, result.state);
      toast.success('Profile updated ✓');
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

  function streakEmoji(streak: number) {
    if (streak >= 30) return '👑';
    if (streak >= 14) return '⚡';
    if (streak >= 7) return '🔥';
    return '🎯';
  }

  const earnedBadges = $derived(badges.filter(b => b.earned));
  const lockedBadges = $derived(badges.filter(b => !b.earned));
</script>

<div class="page">
  <div class="glow-a"></div>
  <div class="glow-b"></div>

  <div class="layout">

    <!-- Left: Identity card -->
    <div class="identity-col">
      <a href="/" class="back">← Home</a>

      <div class="avatar-wrap">
        <div class="avatar">
          {name ? name[0].toUpperCase() : '?'}
        </div>
        {#if currentStreak > 0}
          <span class="streak-badge">{streakEmoji(currentStreak)} {currentStreak}d</span>
        {/if}
      </div>

      <h2 class="identity-name">{name || 'Your Name'}</h2>
      {#if city || region}
        <p class="identity-location">📍 {city}{city && region ? ', ' : ''}{region}</p>
      {/if}

      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-val">{rank ? `#${rank}` : '—'}</span>
          <span class="stat-lbl">Rank</span>
        </div>
        <div class="stat-box">
          <span class="stat-val">Rs {totalPaid.toLocaleString('en-IN')}</span>
          <span class="stat-lbl">Total paid</span>
        </div>
        <div class="stat-box">
          <span class="stat-val">{currentStreak}d</span>
          <span class="stat-lbl">Streak</span>
        </div>
        <div class="stat-box">
          <span class="stat-val">{longestStreak}d</span>
          <span class="stat-lbl">Best streak</span>
        </div>
      </div>

      {#if earnedBadges.length > 0}
        <div class="earned-badges">
          <p class="section-label">Earned badges</p>
          <div class="badge-row">
            {#each earnedBadges as badge}
              <div class="badge-pill" title={badge.desc}>
                <span>{badge.emoji}</span>
                <span>{badge.label}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if lockedBadges.length > 0}
        <div class="locked-badges">
          <p class="section-label">Locked</p>
          <div class="badge-row">
            {#each lockedBadges as badge}
              <div class="badge-pill locked" title={badge.desc}>
                <span>🔒</span>
                <span>{badge.label}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <!-- Right: Edit form -->
    <div class="form-col">
      <h1>Edit Profile</h1>
      <p class="form-sub">Changes apply to your leaderboard name and local rankings.</p>

      <div class="field">
        <label for="dname">Display name</label>
        <input
          id="dname"
          type="text"
          placeholder="Your display name"
          maxlength="30"
          bind:value={name}
          disabled={loading}
          onkeydown={(e) => e.key === 'Enter' && handleSave()}
        />
        <span class="char-count">{name.length}/30</span>
      </div>

      <div class="field">
        <label for="city-picker">Your city <span class="optional">optional</span></label>
        <p class="field-hint">Unlock local leaderboards after your first payment.</p>
        <div id="city-picker">
          <LocationPicker bind:city bind:region disabled={loading} />
        </div>
      </div>

      <div class="actions">
        <button class="btn-save" onclick={handleSave} disabled={loading || name.trim().length < 2}>
          {loading ? 'Saving...' : 'Save changes'}
        </button>
        <button class="btn-cancel" onclick={() => goto('/')} disabled={loading}>
          Cancel
        </button>
      </div>

      <a href="/history" class="history-link">View payment history →</a>
    </div>

  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    background:
      radial-gradient(circle at 20% 0%, rgba(255,77,77,0.1), transparent 40%),
      radial-gradient(circle at 80% 100%, rgba(255,204,0,0.07), transparent 40%),
      #080808;
    color: white;
    font-family: 'Inter', sans-serif;
    position: relative;
    overflow-x: hidden;
    padding: 100px 24px 60px;
    box-sizing: border-box;
  }

  .glow-a {
    position: fixed;
    width: 600px; height: 600px;
    top: -200px; left: -100px;
    background: radial-gradient(circle, rgba(255,77,77,0.12), transparent 60%);
    filter: blur(80px);
    pointer-events: none;
  }

  .glow-b {
    position: fixed;
    width: 400px; height: 400px;
    bottom: -100px; right: -100px;
    background: radial-gradient(circle, rgba(255,204,0,0.1), transparent 60%);
    filter: blur(80px);
    pointer-events: none;
  }

  .layout {
    max-width: 900px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 24px;
    align-items: start;
    position: relative;
    z-index: 1;
  }

  /* ── Identity col ── */
  .identity-col {
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: sticky;
    top: 100px;
  }

  .back {
    display: none;
  }

  .avatar-wrap {
    position: relative;
    width: fit-content;
  }

  .avatar {
    width: 80px;
    height: 80px;
    border-radius: 24px;
    background: linear-gradient(135deg, #ff4d4d, #ffcc00);
    display: grid;
    place-items: center;
    font-size: 2rem;
    font-weight: 900;
    color: black;
    box-shadow: 0 8px 32px rgba(255,100,0,0.3);
  }

  .streak-badge {
    position: absolute;
    bottom: -8px;
    right: -8px;
    background: #1a1a1a;
    border: 1px solid rgba(255,77,77,0.3);
    border-radius: 999px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
    color: #ff9a9a;
    white-space: nowrap;
  }

  .identity-name {
    margin: 4px 0 0;
    font-size: 1.4rem;
    font-weight: 900;
    letter-spacing: -0.5px;
  }

  .identity-location {
    margin: 0;
    font-size: 13px;
    color: #666;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .stat-box {
    padding: 14px;
    border-radius: 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .stat-val {
    font-size: 1rem;
    font-weight: 800;
    color: #fff2b6;
    line-height: 1.2;
  }

  .stat-lbl {
    font-size: 10px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .section-label {
    margin: 0 0 8px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #444;
  }

  .badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .badge-pill {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(255,204,0,0.08);
    border: 1px solid rgba(255,204,0,0.2);
    font-size: 12px;
    font-weight: 600;
    color: #ffdf71;
  }

  .badge-pill.locked {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.06);
    color: #444;
    filter: grayscale(1);
  }

  /* ── Form col ── */
  .form-col {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 24px;
    padding: 28px;
  }

  h1 {
    margin: 0 0 4px;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.3px;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .form-sub { margin: 0 0 24px; color: #444; font-size: 12px; line-height: 1.5; }

  .field {
    margin-bottom: 20px;
    position: relative;
  }

  .field label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #666;
    margin-bottom: 8px;
  }

  .optional {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }

  .field-hint { margin: -4px 0 8px; font-size: 11px; color: #444; }

  .field input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 10px;
    color: white;
    font-size: 14px;
    font-weight: 600;
    padding: 11px 40px 11px 14px;
    outline: none;
    transition: border-color 0.2s;
  }

  .field input:focus { border-color: rgba(255,77,77,0.5); }
  .field input::placeholder { color: #333; font-weight: 400; }

  .char-count {
    position: absolute;
    right: 12px;
    bottom: 11px;
    font-size: 10px;
    color: #333;
    pointer-events: none;
  }

  .actions {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    margin-top: 4px;
  }

  .btn-save {
    flex: 1;
    padding: 11px 16px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

  .btn-cancel {
    padding: 11px 16px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.08);
    background: transparent;
    color: #555;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: color 0.2s, border-color 0.2s;
  }

  .btn-cancel:hover { color: #aaa; border-color: rgba(255,255,255,0.14); }
  .btn-cancel:disabled { opacity: 0.4; cursor: not-allowed; }

  .history-link {
    display: block;
    font-size: 12px;
    color: #333;
    text-decoration: none;
    transition: color 0.2s;
  }

  .history-link:hover { color: #666; }

  @media (max-width: 760px) {
    .layout {
      grid-template-columns: 1fr;
    }

    .identity-col {
      position: static;
      flex-direction: row;
      flex-wrap: wrap;
      align-items: flex-start;
      gap: 16px;
    }

    .avatar-wrap { flex-shrink: 0; }

    .identity-name, .identity-location { width: 100%; }

    .stats-grid { width: 100%; grid-template-columns: repeat(4, 1fr); }

    .earned-badges, .locked-badges { width: 100%; }

    .form-col { padding: 24px 20px; }
  }

  @media (max-width: 480px) {
    .stats-grid { grid-template-columns: 1fr 1fr; }
    .actions { flex-direction: column; }
  }
</style>
