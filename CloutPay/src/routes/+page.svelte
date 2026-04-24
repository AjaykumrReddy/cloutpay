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
      toast.success(`₹${amount} contributed! You\'re on the board 🔥`);
      setTimeout(() => showSuccess = false, 2800);
    } catch (e: any) {
      if (e?.message !== 'cancelled') {
        toast.error(e?.message || 'Payment failed');
      }
    } finally {
      paying = false;
    }
  }

  function connectWS() {
    const ws = new WebSocket(PUBLIC_WS_URL);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'NEW_ACTIVITY') {
        activities = [data.payload, ...activities].slice(0, 10);
      }
      if (data.type === 'INIT_ACTIVITIES') {
        activities = data.payload;
      }
      if (data.type === 'UPDATE_LEADERBOARD') {
        leaderboard = data.payload;
      }
    };

    ws.onerror = () => console.error('WebSocket error');
    ws.onclose = () => setTimeout(connectWS, 3000); // auto-reconnect

    return ws;
  }

  onMount(() => {
    getLeaderboard().then(data => leaderboard = data);
    const ws = connectWS();
    return () => ws.close();
  });
</script>

<div class="page">

  <!-- HERO -->
  <section class="hero">
    <div class="glow"></div>

    <div class="nav">
      {#if $isLoggedIn}
        <a href="/history" class="nav-btn">History</a>
        <button class="nav-btn" onclick={logout}>Logout</button>
      {:else}
        <a href="/login" class="nav-btn">Login</a>
      {/if}
    </div>

    <h1>CloutPay</h1>
    <p>Turn support into status. Climb the leaderboard.</p>

    {#if $isLoggedIn && $displayName}
      <p class="welcome">Welcome back, <span class="name-highlight">{$displayName}</span> 🔥</p>
    {/if}

    <div class="inputs">
      {#if !$isLoggedIn}
        <input
          type="text"
          placeholder="Your name (optional)"
          bind:value={userName}
          disabled={paying || anonymous}
        />
      {/if}
      <input
        type="number"
        placeholder="Amount (₹)"
        min="10"
        bind:value={amount}
        disabled={paying}
      />
    </div>

    <label class="anon-toggle">
      <input type="checkbox" bind:checked={anonymous} disabled={paying} />
      <span>Stay anonymous 🕵️</span>
    </label>

    <button class="cta" onclick={handlePayment} disabled={paying}>
      {paying ? 'Processing...' : '🚀 Get on the Board'}
    </button>
  </section>

  <div class="content">

    <!-- LEADERBOARD -->
    <section class="leaderboard">
      <h2>🏆 Top Supporters</h2>

      <div class="board">
        {#each leaderboard as user, i}
          <div class="card">
            <div class="rank">#{i + 1}</div>
            <div class="name">{user.name}</div>
            <div class="amount">₹{user.amount}</div>
          </div>
        {:else}
          <div class="empty">No supporters yet. Be the first! 🚀</div>
        {/each}
      </div>
    </section>

    <!-- LIVE FEED -->
    <section class="feed">
      <h2>⚡ Live Activity</h2>

      <div class="feed-box">
        {#each activities as act}
          <div class="feed-item">
            {act.text}
          </div>
        {:else}
          <div class="empty">Waiting for activity... ⚡</div>
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
  .page {
    min-height: 100vh;
    background: radial-gradient(circle at top, #1a1a1a, #0a0a0a);
    color: white;
    font-family: 'Inter', sans-serif;
  }

  .hero {
    text-align: center;
    padding: 100px 20px 60px;
    position: relative;
  }

  .nav {
    position: absolute;
    top: 24px;
    right: 28px;
    display: flex;
    gap: 8px;
  }

  .nav-btn {
    padding: 8px 18px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.06);
    color: white;
    font-size: 13px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
  }

  .nav-btn:hover {
    background: rgba(255,255,255,0.12);
  }

  .hero h1 {
    font-size: 3.5rem;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    -webkit-text-fill-color: transparent;
  }

  .hero p {
    color: #aaa;
    margin-top: 10px;
  }

  .welcome {
    color: #aaa;
    font-size: 14px;
    margin-top: 10px;
  }

  .name-highlight {
    color: #ffcc00;
    font-weight: 600;
  }

  .cta {
    margin-top: 20px;
    padding: 12px 26px;
    border-radius: 25px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: bold;
    cursor: pointer;
  }

  .cta:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .inputs {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-top: 24px;
    flex-wrap: wrap;
  }

  .inputs input {
    padding: 10px 16px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    background: rgba(255,255,255,0.07);
    color: white;
    font-size: 14px;
    outline: none;
    width: 180px;
  }

  .inputs input::placeholder {
    color: #888;
  }

  .inputs input:focus {
    border-color: #ff4d4d;
  }

  .anon-toggle {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    color: #aaa;
    font-size: 13px;
    cursor: pointer;
    user-select: none;
  }

  .anon-toggle input[type='checkbox'] {
    accent-color: #ff4d4d;
    width: 15px;
    height: 15px;
    cursor: pointer;
  }

  .empty {
    color: #555;
    font-size: 14px;
    text-align: center;
    padding: 20px 0;
  }

  .content {
    display: flex;
    gap: 30px;
    justify-content: center;
    padding: 40px;
    flex-wrap: wrap;
  }

  /* Leaderboard */
  .leaderboard {
    width: 350px;
    max-width: 100%;
  }

  .board {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .card {
    padding: 14px;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    transition: all 0.4s ease;
  }

  .card:hover {
    transform: translateY(-3px);
  }

  /* Feed */
  .feed {
    width: 350px;
    max-width: 100%;
  }

  .feed-box {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 400px;
    overflow: hidden;
  }

  @media (max-width: 480px) {
    .hero {
      padding: 80px 16px 40px;
    }

    .hero h1 {
      font-size: 2.4rem;
    }

    .content {
      padding: 20px 16px;
      gap: 20px;
    }

    .leaderboard,
    .feed {
      width: 100%;
    }

    .inputs {
      flex-direction: column;
      align-items: center;
    }

    .inputs input {
      width: 100%;
      max-width: 300px;
    }

    .nav {
      top: 16px;
      right: 16px;
    }
  }

  .feed-item {
    padding: 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    font-size: 14px;
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from {
      transform: translateY(10px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .glow {
    position: absolute;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,0,0,0.3), transparent);
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    filter: blur(120px);
  }

  /* Success overlay */
  .success-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.75);
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
    font-size: 72px;
    animation: bounce 0.6s ease 0.2s both;
  }

  .success-text {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 12px 0 6px;
  }

  .success-amount {
    color: #aaa;
    font-size: 15px;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
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
</style>