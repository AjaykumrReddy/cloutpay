<script lang="ts">
  import { onMount } from "svelte";
  import { PUBLIC_WS_URL } from '$env/static/public';
  import { initiatePayment } from '$lib/razorpay';
  import { getLeaderboard } from '$lib/api';
  import { authStore, isLoggedIn, displayName } from '$lib/auth';

  let leaderboard = $state<{ name: string; amount: number }[]>([]);
  let activities = $state<{ text: string }[]>([]);

  let paying = $state(false);
  let amount = $state(100);
  let userName = $state('');
  let error = $state('');

  function logout() {
    authStore.clear();
  }

  async function handlePayment() {
    error = '';
    // Use saved display name if logged in, else use input
    const name = $displayName || userName.trim() || 'Anonymous';
    if (amount < 10) { error = 'Minimum amount is ₹10'; return; }
    paying = true;
    try {
      await initiatePayment(amount, name);
    } catch (e: any) {
      error = e?.message || 'Payment failed';
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
          disabled={paying}
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

    {#if error}
      <p class="error">{error}</p>
    {/if}

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
        {/each}
      </div>
    </section>

  </div>

</div>

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

  .error {
    color: #ff4d4d;
    font-size: 13px;
    margin-top: 8px;
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
  }

  .feed-box {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 400px;
    overflow: hidden;
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
</style>