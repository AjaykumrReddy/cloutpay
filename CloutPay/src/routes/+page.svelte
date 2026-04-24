<script lang="ts">
  import { onMount } from "svelte";
  import { PUBLIC_WS_URL } from '$env/static/public';
  import { initiatePayment } from '$lib/razorpay';
  import { getLeaderboard } from '$lib/api';
  import { authStore, isLoggedIn, displayName, authToken } from '$lib/auth';
  import { toast } from '$lib/toast';

  let leaderboard = $state<{ name: string; amount: number }[]>([]);
  let activities = $state<{ text: string }[]>([]);

  let paying = $state(false);
  let amount = $state(100);
  let userName = $state('');
  let anonymous = $state(false);
  let showSuccess = $state(false);
  let totalRaised = $state(0);

  $effect(() => {
    totalRaised = leaderboard.reduce((s, u) => s + u.amount, 0);
  });

  function logout() {
    authStore.clear();
    toast.info('Logged out');
  }

  async function handlePayment() {
    const name = anonymous ? 'Anonymous' : ($displayName || userName.trim() || 'Anonymous');
    if (amount < 10) { toast.error('Minimum amount is ₹10'); return; }
    paying = true;
    try {
      await initiatePayment(amount, name, $authToken, anonymous);
      showSuccess = true;
      toast.success(`₹${amount} contributed! You're on the board 🔥`);
      setTimeout(() => showSuccess = false, 2800);
    } catch (e: any) {
      if (e?.message !== 'cancelled') toast.error(e?.message || 'Payment failed');
    } finally {
      paying = false;
    }
  }

  function connectWS() {
    const ws = new WebSocket(PUBLIC_WS_URL);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'NEW_ACTIVITY')    activities = [data.payload, ...activities].slice(0, 10);
      if (data.type === 'INIT_ACTIVITIES') activities = data.payload;
      if (data.type === 'UPDATE_LEADERBOARD') leaderboard = data.payload;
    };
    ws.onerror = () => console.error('WebSocket error');
    ws.onclose = () => setTimeout(connectWS, 3000);
    return ws;
  }

  onMount(() => {
    getLeaderboard().then(data => leaderboard = data);
    const ws = connectWS();
    return () => ws.close();
  });
</script>

<div class="page">

  <!-- NAV -->
  <nav class="nav">
    <span class="logo">CloutPay</span>
    <div class="nav-links">
      {#if $isLoggedIn}
        <a href="/history" class="nav-btn">History</a>
        <button class="nav-btn" onclick={logout}>Logout</button>
      {:else}
        <a href="/login" class="nav-btn primary">Login</a>
      {/if}
    </div>
  </nav>

  <!-- HERO -->
  <section class="hero">
    <div class="glow-1"></div>
    <div class="glow-2"></div>

    <div class="badge">⚡ Live · {activities.length} recent actions</div>

    <h1>Turn Money Into<br/><span class="gradient-text">Status.</span></h1>
    <p class="sub">Support the board. Climb the ranks. Get seen.</p>

    {#if $isLoggedIn && $displayName}
      <p class="welcome">Welcome back, <span class="name-highlight">{$displayName}</span> 🔥</p>
    {/if}

    <div class="hero-body">

      <!-- PAYMENT FORM -->
      <div class="form-card">
      <div class="inputs">
        {#if !$isLoggedIn}
          <input
            type="text"
            placeholder="Your name (optional)"
            bind:value={userName}
            disabled={paying || anonymous}
          />
        {/if}
        <div class="amount-wrap">
          <span class="rupee">₹</span>
          <input
            type="number"
            placeholder="Amount"
            min="10"
            bind:value={amount}
            disabled={paying}
          />
        </div>
      </div>
      <div class="quick-amounts">
        {#each [50, 100, 500, 1000] as q}
          <button
            class="quick-btn {amount === q ? 'active' : ''}"
            onclick={() => amount = q}
            disabled={paying}
          >₹{q}</button>
        {/each}
      </div>
      <label class="anon-toggle">
        <input type="checkbox" bind:checked={anonymous} disabled={paying} />
        <span>Stay anonymous 🕵️</span>
      </label>
      <button class="cta" onclick={handlePayment} disabled={paying}>
        {paying ? 'Processing...' : '🚀 Get on the Board'}
      </button>
    </div>

      <!-- STATS BAR -->
      <div class="stats-bar">
        <div class="stat">
          <span class="stat-value">₹{totalRaised.toLocaleString('en-IN')}</span>
          <span class="stat-label">Total Raised</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">{leaderboard.length}</span>
          <span class="stat-label">Contributors</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">{activities.length}</span>
          <span class="stat-label">Live Actions</span>
        </div>
      </div>

    </div>
  </section>

  <!-- LEADERBOARD + FEED -->
  <div class="content">

    <section class="leaderboard">
      <div class="section-header">
        <h2>🏆 Top Supporters</h2>
      </div>
      <div class="board">
        {#each leaderboard as user, i}
          <div class="card rank-{i}">
            <div class="rank-badge rank-{i}">{i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i+1}`}</div>
            <div class="card-info">
              <span class="card-name">{user.name}</span>
            </div>
            <div class="card-amount">₹{user.amount.toLocaleString('en-IN')}</div>
          </div>
        {:else}
          <div class="empty">
            <p>🚀 No supporters yet</p>
            <span>Be the first to get on the board!</span>
          </div>
        {/each}
      </div>
    </section>

    <section class="feed">
      <div class="section-header">
        <h2>⚡ Live Activity</h2>
        <span class="live-dot"></span>
      </div>
      <div class="feed-box">
        {#each activities as act}
          <div class="feed-item">{act.text}</div>
        {:else}
          <div class="empty">
            <p>⚡ Waiting for activity</p>
            <span>Actions will appear here in real-time</span>
          </div>
        {/each}
      </div>
    </section>

  </div>

</div>

{#if showSuccess}
  <div class="success-overlay">
    <div class="success-burst">
      <div class="success-icon">🔥</div>
      <p class="success-text">You're on the board!</p>
      <p class="success-amount">₹{amount} contributed</p>
    </div>
  </div>
{/if}

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

  :global(body) {
    margin: 0;
    background: #080808;
  }

  .page {
    min-height: 100vh;
    background: #080808;
    color: white;
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
  }

  /* NAV */
  .nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    background: rgba(8,8,8,0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }

  .logo {
    font-size: 1.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .nav-links { display: flex; gap: 8px; }

  .nav-btn {
    padding: 7px 16px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.05);
    color: white;
    font-size: 13px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: background 0.2s ease;
  }

  .nav-btn:hover { background: rgba(255,255,255,0.1); }

  .nav-btn.primary {
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    border: none;
  }

  /* HERO */
  .hero {
    text-align: center;
    padding: 140px 20px 80px;
    position: relative;
    overflow: hidden;
  }

  .glow-1 {
    position: absolute;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(255,77,77,0.18), transparent 70%);
    top: -100px; left: 50%;
    transform: translateX(-50%);
    filter: blur(40px);
    pointer-events: none;
  }

  .glow-2 {
    position: absolute;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,204,0,0.1), transparent 70%);
    top: 60px; left: 60%;
    filter: blur(60px);
    pointer-events: none;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid rgba(255,77,77,0.3);
    background: rgba(255,77,77,0.08);
    font-size: 12px;
    color: #ff8080;
    margin-bottom: 24px;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }

  h1 {
    font-size: clamp(2.8rem, 7vw, 5rem);
    font-weight: 900;
    line-height: 1.1;
    margin: 0 0 16px;
    letter-spacing: -2px;
  }

  .gradient-text {
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .sub {
    color: #888;
    font-size: 1.1rem;
    margin: 0 0 12px;
  }

  .welcome {
    font-size: 14px;
    color: #888;
    margin: 8px 0 0;
  }

  .name-highlight {
    color: #ffcc00;
    font-weight: 600;
  }

  /* STATS BAR */
  .hero-body {
    display: inline-flex;
    flex-direction: column;
    align-items: stretch;
    width: 420px;
    max-width: calc(100vw - 40px);
    margin-top: 28px;
  }

  .stats-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 12px 0 0;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 28px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .stat-value {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .stat-label {
    font-size: 11px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .stat-divider {
    width: 1px;
    height: 36px;
    background: rgba(255,255,255,0.08);
  }

  /* FORM CARD */
  .form-card {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 32px;
    text-align: left;
  }

  .inputs {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }

  .inputs input {
    flex: 1;
    min-width: 120px;
    padding: 11px 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.06);
    color: white;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }

  .inputs input:focus { border-color: #ff4d4d; }
  .inputs input::placeholder { color: #555; }
  .inputs input:disabled { opacity: 0.5; }

  .amount-wrap {
    flex: 1;
    min-width: 120px;
    display: flex;
    align-items: center;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s;
  }

  .amount-wrap:focus-within { border-color: #ff4d4d; }

  .rupee {
    padding: 0 10px 0 14px;
    color: #888;
    font-size: 15px;
  }

  .amount-wrap input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: white;
    font-size: 15px;
    font-weight: 600;
    padding: 11px 14px 11px 0;
  }

  .amount-wrap input::placeholder { color: #555; }

  /* QUICK AMOUNTS */
  .quick-amounts {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .quick-btn {
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    color: #aaa;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .quick-btn:hover {
    border-color: #ff4d4d;
    color: white;
  }

  .quick-btn.active {
    background: rgba(255,77,77,0.15);
    border-color: #ff4d4d;
    color: #ff8080;
    font-weight: 600;
  }

  .quick-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .anon-toggle {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    color: #666;
    font-size: 13px;
    cursor: pointer;
    user-select: none;
  }

  .anon-toggle input[type='checkbox'] {
    accent-color: #ff4d4d;
    width: 14px; height: 14px;
    cursor: pointer;
  }

  .cta {
    width: 100%;
    padding: 14px;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 800;
    font-size: 15px;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.1s;
    letter-spacing: 0.3px;
  }

  .cta:hover:not(:disabled) { transform: translateY(-1px); opacity: 0.92; }
  .cta:active:not(:disabled) { transform: translateY(0); }
  .cta:disabled { opacity: 0.5; cursor: not-allowed; }

  /* CONTENT */
  .content {
    display: flex;
    gap: 24px;
    justify-content: center;
    padding: 60px 32px;
    flex-wrap: wrap;
    max-width: 900px;
    margin: 0 auto;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
  }

  .section-header h2 {
    font-size: 1rem;
    font-weight: 700;
    color: #ccc;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .live-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 6px #22c55e;
    animation: pulse 1.5s infinite;
  }

  /* LEADERBOARD */
  .leaderboard { width: 400px; max-width: 100%; }

  .board { display: flex; flex-direction: column; gap: 8px; }

  .card {
    padding: 14px 16px;
    border-radius: 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    gap: 14px;
    transition: transform 0.2s, background 0.2s;
  }

  .card:hover {
    transform: translateX(4px);
    background: rgba(255,255,255,0.07);
  }

  .card.rank-0 { border-color: rgba(255,215,0,0.3); background: rgba(255,215,0,0.05); }
  .card.rank-1 { border-color: rgba(192,192,192,0.25); }
  .card.rank-2 { border-color: rgba(205,127,50,0.25); }

  .rank-badge {
    font-size: 1.3rem;
    width: 32px;
    text-align: center;
    flex-shrink: 0;
  }

  .card-info { flex: 1; }

  .card-name {
    font-size: 15px;
    font-weight: 600;
    color: #eee;
  }

  .card-amount {
    font-size: 15px;
    font-weight: 700;
    color: #ffcc00;
  }

  /* FEED */
  .feed { width: 380px; max-width: 100%; }

  .feed-box {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 420px;
    overflow: hidden;
  }

  .feed-item {
    padding: 12px 16px;
    border-radius: 12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    font-size: 14px;
    color: #ccc;
    animation: slideIn 0.3s ease;
  }

  .empty {
    padding: 32px 20px;
    text-align: center;
    border-radius: 14px;
    border: 1px dashed rgba(255,255,255,0.08);
  }

  .empty p {
    font-size: 15px;
    color: #555;
    margin: 0 0 6px;
  }

  .empty span {
    font-size: 12px;
    color: #333;
  }

  /* ANIMATIONS */
  @keyframes slideIn {
    from { transform: translateY(8px); opacity: 0; }
    to   { transform: translateY(0);   opacity: 1; }
  }

  /* SUCCESS OVERLAY */
  .success-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
  }

  .success-burst {
    text-align: center;
    animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }

  .success-icon {
    font-size: 80px;
    animation: bounce 0.6s ease 0.2s both;
  }

  .success-text {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 14px 0 6px;
  }

  .success-amount { color: #888; font-size: 15px; }

  @keyframes fadeIn {
    from { opacity: 0; } to { opacity: 1; }
  }

  @keyframes popIn {
    from { transform: scale(0.6); opacity: 0; }
    to   { transform: scale(1);   opacity: 1; }
  }

  @keyframes bounce {
    0%   { transform: scale(0.5) rotate(-10deg); opacity: 0; }
    60%  { transform: scale(1.2) rotate(5deg); }
    100% { transform: scale(1)   rotate(0deg); opacity: 1; }
  }

  /* MOBILE */
  @media (max-width: 600px) {
    .nav { padding: 14px 20px; }
    .hero { padding: 110px 16px 60px; }
    h1 { letter-spacing: -1px; }
    .hero-body { width: 100%; }
    .stats-bar { padding: 14px 20px; }
    .form-card { padding: 20px; }
    .content { padding: 32px 16px; }
    .leaderboard, .feed { width: 100%; }
    .inputs { flex-direction: column; }
    .amount-wrap, .inputs input { width: 100%; }
  }
</style>