<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { authToken, authStore } from '$lib/auth';
  import { getHistory, getMySummary, AuthError, type HistoryPayment } from '$lib/api';
  import { toast } from '$lib/toast';

  interface MySummary {
    display_name: string | null;
    total_contributed: number;
    payments_count: number;
    biggest_payment: number;
    average_payment: number;
    current_rank: number | null;
    amount_to_next_rank: number | null;
    next_rank_name: string | null;
    last_payment_at: string | null;
  }

  let payments = $state<HistoryPayment[]>([]);
  let summary = $state<MySummary | null>(null);
  let loading = $state(true);
  let loadingMore = $state(false);
  let error = $state('');
  let page = $state(1);
  let hasMore = $state(false);

  const totalAmount = $derived(summary?.total_contributed ?? 0);
  const biggestPayment = $derived(summary?.biggest_payment ?? 0);
  const averagePayment = $derived(summary?.average_payment ?? 0);

  onMount(async () => {
    const token = get(authToken);
    if (!token) {
      goto('/login');
      return;
    }

    try {
      const [history, mySummary] = await Promise.all([
        getHistory(token, 1),
        getMySummary(token)
      ]);
      payments = history.items;
      hasMore = history.has_more;
      summary = mySummary;
    } catch (e: any) {
      if (e instanceof AuthError) {
        authStore.clear();
        toast.error(e.message);
        goto('/login');
        return;
      }
      error = e?.message || 'Failed to load your history';
    } finally {
      loading = false;
    }
  });

  async function loadMore() {
    const token = get(authToken);
    if (!token) return;
    loadingMore = true;
    try {
      const next = page + 1;
      const result = await getHistory(token, next);
      payments = [...payments, ...result.items];
      hasMore = result.has_more;
      page = next;
    } catch (e: any) {
      if (e instanceof AuthError) {
        authStore.clear();
        toast.error(e.message);
        goto('/login');
        return;
      }
      toast.error(e?.message || 'Failed to load more');
    } finally {
      loadingMore = false;
    }
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  async function copyReference(reference: string) {
    try {
      await navigator.clipboard.writeText(reference);
      toast.success('Payment reference copied');
    } catch {
      toast.error('Could not copy the payment reference');
    }
  }
</script>

<div class="page">
  <div class="glow"></div>

  <div class="container">
    <div class="header">
      <div>
        <a href="/" class="back">Back to home</a>
        <h1>Your Contribution History</h1>
        <p class="sub">Track how much you have contributed, how often you show up, and where you stand right now.</p>
      </div>
      <a href="/profile" class="profile-link">Edit profile</a>
    </div>

    {#if loading}
      <p class="status">Loading your history...</p>
    {:else if error}
      <p class="status error">{error}</p>
    {:else}
      <div class="summary-grid">
        <div class="summary-card">
          <span class="summary-label">Current rank</span>
          <strong>{summary?.current_rank ? `#${summary.current_rank}` : 'Unranked'}</strong>
        </div>
        <div class="summary-card">
          <span class="summary-label">Total contributed</span>
          <strong>Rs {totalAmount.toLocaleString('en-IN')}</strong>
        </div>
        <div class="summary-card">
          <span class="summary-label">Largest payment</span>
          <strong>Rs {biggestPayment.toLocaleString('en-IN')}</strong>
        </div>
        <div class="summary-card">
          <span class="summary-label">Average payment</span>
          <strong>Rs {averagePayment.toLocaleString('en-IN')}</strong>
        </div>
      </div>

      {#if summary?.current_rank && summary.amount_to_next_rank && summary.next_rank_name}
        <div class="insight">
          Rs {summary.amount_to_next_rank.toLocaleString('en-IN')} more will move you ahead of {summary.next_rank_name}.
        </div>
      {:else if summary?.current_rank === 1}
        <div class="insight">You are currently leading the board.</div>
      {/if}

      {#if payments.length === 0}
        <div class="empty">
          <p>No payments yet.</p>
          <a href="/" class="cta">Make your first contribution</a>
        </div>
      {:else}
        <div class="list">
          {#each payments as payment}
            <div class="row">
              <div class="row-main">
                <div class="row-top">
                  <span class="name">{payment.user_name}</span>
                  <span class="amount">Rs {payment.amount.toLocaleString('en-IN')}</span>
                </div>
                <div class="row-meta">
                  <span>{formatDate(payment.created_at)}</span>
                  <button class="copy-btn" onclick={() => copyReference(payment.payment_reference)}>
                    Copy ref
                  </button>
                  <span class="ref">{payment.payment_reference}</span>
                </div>
              </div>
            </div>
          {/each}
        </div>

        {#if hasMore}
          <button class="load-more" onclick={loadMore} disabled={loadingMore}>
            {loadingMore ? 'Loading...' : 'Load more'}
          </button>
        {/if}
      {/if}
    {/if}
  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    background: radial-gradient(circle at top, #1a1a1a, #0a0a0a 56%);
    color: white;
    font-family: 'Inter', sans-serif;
    position: relative;
    overflow-x: hidden;
  }

  .glow {
    position: absolute;
    width: 520px;
    height: 420px;
    background: radial-gradient(circle, rgba(255, 90, 90, 0.22), transparent);
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    filter: blur(120px);
    pointer-events: none;
  }

  .container {
    max-width: 920px;
    margin: 0 auto;
    padding: 60px 20px 50px;
    position: relative;
    z-index: 1;
    box-sizing: border-box;
  }

  .header {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 30px;
  }

  .back,
  .profile-link {
    color: #969696;
    text-decoration: none;
    font-size: 14px;
  }

  h1 {
    margin: 12px 0 10px;
    font-size: clamp(2rem, 4vw, 3rem);
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .sub {
    margin: 0;
    max-width: 600px;
    color: #a2a2a2;
    line-height: 1.5;
  }

  .status {
    text-align: center;
    color: #8f8f8f;
    margin-top: 70px;
  }

  .status.error {
    color: #ff7070;
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 16px;
  }

  .summary-card,
  .row,
  .insight {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
  }

  .summary-card {
    padding: 18px;
  }

  .summary-label {
    display: block;
    color: #767676;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
  }

  .summary-card strong {
    font-size: 1.15rem;
    line-height: 1.4;
  }

  .insight {
    margin-bottom: 18px;
    padding: 14px 18px;
    color: #ffe49e;
  }

  .empty {
    text-align: center;
    margin-top: 60px;
    color: #6d6d6d;
  }

  .cta {
    display: inline-block;
    margin-top: 16px;
    padding: 10px 22px;
    border-radius: 999px;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    text-decoration: none;
    font-size: 14px;
  }

  .list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .row {
    padding: 16px 18px;
  }

  .row-main {
    min-width: 0;
  }

  .row-top {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: center;
    margin-bottom: 10px;
  }

  .name {
    font-size: 15px;
    font-weight: 600;
  }

  .amount {
    font-size: 16px;
    font-weight: 800;
    color: #ffda77;
  }

  .row-meta {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    color: #8a8a8a;
    font-size: 13px;
  }

  .copy-btn {
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.05);
    color: white;
    border-radius: 999px;
    padding: 6px 10px;
    cursor: pointer;
    font-size: 12px;
  }

  .load-more {
    display: block;
    width: 100%;
    margin-top: 16px;
    padding: 13px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.04);
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .load-more:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.08);
  }

  .load-more:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .ref {
    color: #666;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12px;
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  @media (max-width: 760px) {
    .header {
      flex-direction: column;
    }

    .summary-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 540px) {
    .container {
      padding: 40px 16px;
    }

    .summary-grid {
      grid-template-columns: 1fr;
    }

    .row-top {
      align-items: flex-start;
      flex-direction: column;
    }

    .row {
      padding: 14px;
    }

    .row-meta {
      align-items: flex-start;
      flex-direction: column;
    }
  }
</style>
