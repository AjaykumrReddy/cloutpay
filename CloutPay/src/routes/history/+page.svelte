<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { authToken, isLoggedIn } from '$lib/auth';
  import { getHistory } from '$lib/api';

  interface Payment {
    id: number;
    amount: number;
    user_name: string;
    created_at: string;
  }

  let payments = $state<Payment[]>([]);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    const token = get(authToken);
    if (!token) { goto('/login'); return; }

    try {
      payments = await getHistory(token);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('en-IN', {
      day: 'numeric', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }
</script>

<div class="page">
  <div class="glow"></div>

  <div class="container">
    <div class="header">
      <a href="/" class="back">← Back</a>
      <h1>My Payments</h1>
    </div>

    {#if loading}
      <p class="status">Loading...</p>
    {:else if error}
      <p class="status error">{error}</p>
    {:else if payments.length === 0}
      <div class="empty">
        <p>No payments yet.</p>
        <a href="/" class="cta">Make your first contribution 🚀</a>
      </div>
    {:else}
      <div class="list">
        {#each payments as p}
          <div class="row">
            <div class="left">
              <span class="name">{p.user_name}</span>
              <span class="date">{formatDate(p.created_at)}</span>
            </div>
            <div class="amount">₹{p.amount}</div>
          </div>
        {/each}
      </div>

      <div class="total">
        Total: ₹{payments.reduce((s, p) => s + p.amount, 0).toLocaleString('en-IN')}
      </div>
    {/if}
  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    background: radial-gradient(circle at top, #1a1a1a, #0a0a0a);
    color: white;
    font-family: 'Inter', sans-serif;
    position: relative;
  }

  .glow {
    position: absolute;
    width: 500px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,0,0,0.2), transparent);
    top: -100px;
    left: 50%;
    transform: translateX(-50%);
    filter: blur(120px);
    pointer-events: none;
  }

  .container {
    max-width: 560px;
    margin: 0 auto;
    padding: 60px 20px 40px;
    position: relative;
    z-index: 1;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 32px;
  }

  .back {
    color: #888;
    text-decoration: none;
    font-size: 14px;
  }

  .back:hover { color: white; }

  h1 {
    font-size: 1.6rem;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }

  .status {
    text-align: center;
    color: #888;
    margin-top: 60px;
  }

  .status.error { color: #ff4d4d; }

  .empty {
    text-align: center;
    margin-top: 60px;
    color: #666;
  }

  .cta {
    display: inline-block;
    margin-top: 16px;
    padding: 10px 22px;
    border-radius: 20px;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    text-decoration: none;
    font-size: 14px;
  }

  .list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
  }

  .left {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .name {
    font-size: 15px;
    font-weight: 500;
  }

  .date {
    font-size: 12px;
    color: #666;
  }

  .amount {
    font-size: 16px;
    font-weight: 700;
    color: #ffcc00;
  }

  .total {
    margin-top: 20px;
    text-align: right;
    font-size: 15px;
    color: #aaa;
    border-top: 1px solid rgba(255,255,255,0.08);
    padding-top: 14px;
  }
</style>
