<script lang="ts">
  import { onMount } from 'svelte';
  import { afterNavigate } from '$app/navigation';
  import { PUBLIC_WS_URL } from '$env/static/public';
  import { getLeaderboard, getMySummary, AuthError } from '$lib/api';
  import { authToken, displayName, isLoggedIn, authStore, shareToken } from '$lib/auth';
  import { initiatePayment } from '$lib/razorpay';
  import { toast } from '$lib/toast';

  type Period = 'all' | 'month';

  interface LeaderboardEntry {
    name: string;
    amount: number;
  }

  interface ActivityItem {
    text: string;
  }

  interface MySummary {
    display_name: string | null;
    total_contributed: number;
    payments_count: number;
    current_rank: number | null;
    amount_to_next_rank: number | null;
    next_rank_name: string | null;
    last_payment_at: string | null;
  }

  let leaderboard = $state<LeaderboardEntry[]>([]);
  let activities = $state<ActivityItem[]>([]);
  let mySummary = $state<MySummary | null>(null);
  let period = $state<Period>('all');

  let paying = $state(false);
  let amount = $state(100);
  let userName = $state('');
  let anonymous = $state(false);
  let showSuccess = $state(false);
  let showShareCard = $state(false);
  let totalRaised = $state(0);
  let loadingSummary = $state(false);
  let loadedSummaryToken = $state<string | null | undefined>(undefined);

  $effect(() => {
    totalRaised = leaderboard.reduce((sum, entry) => sum + entry.amount, 0);
  });

  async function loadLeaderboard() {
    leaderboard = await getLeaderboard(period === 'month' ? 'month' : undefined);
  }

  async function loadMyStats() {
    if (!$authToken) {
      mySummary = null;
      loadedSummaryToken = null;
      return;
    }

    loadingSummary = true;
    try {
      mySummary = await getMySummary($authToken, period === 'month' ? 'month' : undefined);
      loadedSummaryToken = $authToken;
    } catch (e: any) {
      if (e instanceof AuthError) {
        authStore.clear();
        toast.error(e.message);
        return;
      }
      toast.error(e?.message || 'Failed to load your stats');
      loadedSummaryToken = $authToken;
    } finally {
      loadingSummary = false;
    }
  }

  async function onPeriodChange(newPeriod: Period) {
    period = newPeriod;
    await Promise.all([
      loadLeaderboard(),
      $authToken ? loadMyStats() : Promise.resolve()
    ]);
  }

  async function handlePayment() {
    const name = anonymous ? 'Anonymous' : ($displayName || userName.trim() || 'Anonymous');
    if (amount < 10) {
      toast.error('Minimum amount is Rs 10');
      return;
    }

    paying = true;
    try {
      await initiatePayment(amount, name, $authToken, anonymous);
      await loadLeaderboard();
      if ($isLoggedIn) await loadMyStats();
      showSuccess = true;
      toast.success(`Rs ${amount} contributed successfully`);
    } catch (e: any) {
      if (e instanceof AuthError) {
        authStore.clear();
        toast.error(e.message);
        return;
      }
      if (e?.message !== 'cancelled') toast.error(e?.message || 'Payment failed');
    } finally {
      paying = false;
    }
  }

  function connectWS() {
    const ws = new WebSocket(PUBLIC_WS_URL);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'NEW_ACTIVITY') activities = [data.payload, ...activities].slice(0, 10);
      if (data.type === 'INIT_ACTIVITIES') activities = data.payload;
      if (data.type === 'UPDATE_LEADERBOARD') leaderboard = data.payload;
    };
    ws.onerror = () => console.error('WebSocket error');
    ws.onclose = () => setTimeout(connectWS, 3000);
    return ws;
  }

  function formatLastPayment(date: string | null) {
    if (!date) return 'No contribution yet';
    return new Date(date).toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function getMedal(index: number) {
    if (index === 0) return '\u{1F947}';
    if (index === 1) return '\u{1F948}';
    if (index === 2) return '\u{1F949}';
    return `#${index + 1}`;
  }

  function getTierLabel(index: number) {
    if (index === 0) return 'Gold tier';
    if (index === 1) return 'Silver tier';
    if (index === 2) return 'Bronze tier';
    return '';
  }

  function getSuccessMessage() {
    if (!$isLoggedIn || !mySummary?.current_rank) {
      return 'Your contribution is live on the board.';
    }
    if (mySummary.current_rank === 1) {
      return 'You are leading the board right now.';
    }
    return `You are now ranked #${mySummary.current_rank}.`;
  }

  async function shareRank() {
    const rank = mySummary?.current_rank;
    const total = mySummary?.total_contributed ?? 0;
    const shareUrl = `${window.location.origin}/share/${$shareToken}`;
    const text = rank
      ? `I'm ranked #${rank} on CloutPay with Rs ${total.toLocaleString('en-IN')} contributed. Can you beat me?`
      : `I just contributed Rs ${total.toLocaleString('en-IN')} on CloutPay. Join the board!`;

    if (navigator.share) {
      try {
        await navigator.share({ title: 'CloutPay', text, url: shareUrl });
      } catch {}
    } else {
      try {
        await navigator.clipboard.writeText(`${text} ${shareUrl}`);
        toast.success('Copied to clipboard');
      } catch {
        toast.error('Could not copy');
      }
    }
  }

  onMount(() => {
    loadLeaderboard().catch(() => toast.error('Failed to load leaderboard'));
    const ws = connectWS();
    return () => ws.close();
  });

  $effect(() => {
    // $authToken starts null on mount (auth hydrates from localStorage after mount)
    // this fires once when it becomes available
    if ($authToken && loadedSummaryToken !== $authToken && !loadingSummary) {
      loadMyStats();
    }
    if (!$isLoggedIn) {
      mySummary = null;
      loadedSummaryToken = null;
    }
  });

  afterNavigate(({ from }) => {
    if (!from) return;
    if (from.url.pathname.startsWith('/profile')) {
      loadedSummaryToken = null; // force $effect to re-fetch with fresh data
      loadLeaderboard().catch(() => {});
    }
  });
</script>

<div class="page">

  {#if activities.length > 0}
    <div class="ticker-wrap">
      <div class="ticker-track">
        {#each [...activities, ...activities] as activity, i}
          <span class="ticker-item">
            <span class="ticker-dot"></span>{activity.text}
          </span>
        {/each}
      </div>
    </div>
  {/if}

  <section class="hero">
    <div class="glow glow-a"></div>
    <div class="glow glow-b"></div>

    <div class="badge">🔴 Live board · {activities.length} recent actions</div>
    <h1>Pay. Rank.<br /><span class="gradient-text">Flex.</span></h1>
    <p class="sub">The live leaderboard where your money talks. Top spot is open. Someone's about to take it.</p>

    {#if $isLoggedIn && $displayName}
      <p class="welcome">Welcome back, <span class="name-highlight">{$displayName}</span></p>
    {/if}

    <div class="hero-grid">
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
            <span class="rupee">Rs</span>
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
          {#each [50, 100, 500, 1000] as quickAmount}
            <button
              class:active={amount === quickAmount}
              class="quick-btn"
              onclick={() => amount = quickAmount}
              disabled={paying}
            >
              Rs {quickAmount}
            </button>
          {/each}
        </div>

        <label class="anon-toggle">
          <input type="checkbox" bind:checked={anonymous} disabled={paying} />
          <span>Stay anonymous</span>
        </label>

        <button class="cta" onclick={handlePayment} disabled={paying}>
          {paying ? 'Processing...' : 'Claim your spot'}
        </button>

        <div class="stats-bar">
          <div class="stat">
            <span class="stat-value">Rs {totalRaised.toLocaleString('en-IN')}</span>
            <span class="stat-label">Total raised</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-value">{leaderboard.length}</span>
            <span class="stat-label">On the board</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-value">{activities.length}</span>
            <span class="stat-label">Live actions</span>
          </div>
        </div>
      </div>

      {#if $isLoggedIn}
        <div class="personal-card">
          <div class="section-header">
            <h2>Your Standing</h2>
            <span class="period-label">{period === 'month' ? 'This month' : 'All time'}</span>
          </div>

          {#if loadingSummary}
            <p class="personal-copy">Loading your contribution stats...</p>
          {:else if mySummary}
            <div class="personal-grid">
              <div class="personal-stat">
                <span class="personal-label">Current rank</span>
                <strong>{mySummary.current_rank ? `#${mySummary.current_rank}` : 'Unranked'}</strong>
              </div>
              <div class="personal-stat">
                <span class="personal-label">Your total</span>
                <strong>Rs {mySummary.total_contributed.toLocaleString('en-IN')}</strong>
              </div>
              <div class="personal-stat">
                <span class="personal-label">Payments made</span>
                <strong>{mySummary.payments_count}</strong>
              </div>
              <div class="personal-stat">
                <span class="personal-label">Last payment</span>
                <strong>{formatLastPayment(mySummary.last_payment_at)}</strong>
              </div>
            </div>

            {#if !mySummary.display_name}
              <p class="personal-copy">
                Add a display name so your payments count toward the public leaderboard.
              </p>
            {:else if mySummary.current_rank && mySummary.amount_to_next_rank && mySummary.next_rank_name}
              <p class="personal-copy">
                You need Rs {mySummary.amount_to_next_rank.toLocaleString('en-IN')} more to pass {mySummary.next_rank_name}.
              </p>
            {:else if mySummary.current_rank === 1}
              <p class="personal-copy">You are currently leading the board.</p>
            {:else}
              <p class="personal-copy">Make a contribution to start climbing the board.</p>
            {/if}
          {:else}
            <p class="personal-copy">
              We are getting your rank and contribution stats ready.
            </p>
          {/if}
        </div>
      {:else if leaderboard.length > 0}
        <div class="spotlight-card">
          <p class="spotlight-label">👑 Currently leading</p>
          <p class="spotlight-name">{leaderboard[0].name}</p>
          <p class="spotlight-amount">Rs {leaderboard[0].amount.toLocaleString('en-IN')}</p>
          <p class="spotlight-copy">Think you can beat them?</p>
          <a href="/login" class="spotlight-cta">Login to compete</a>
        </div>
      {/if}
    </div>
  </section>

  <section class="how-it-works">
    <p class="hiw-label">How it works</p>
    <div class="hiw-steps">
      <div class="hiw-step">
        <span class="hiw-num">01</span>
        <strong>Pay</strong>
        <p>Contribute any amount — Rs 10 or Rs 10,000. Every rupee counts toward your rank.</p>
      </div>
      <div class="hiw-divider"></div>
      <div class="hiw-step">
        <span class="hiw-num">02</span>
        <strong>Rank</strong>
        <p>Your total contribution places you on the live leaderboard, updated in real time.</p>
      </div>
      <div class="hiw-divider"></div>
      <div class="hiw-step">
        <span class="hiw-num">03</span>
        <strong>Flex</strong>
        <p>Share your rank card. Let everyone know where you stand. Climb higher.</p>
      </div>
    </div>
  </section>

  <div class="content">
    <section class="leaderboard">
      <div class="section-header">
        <h2>Top Supporters</h2>
        <div class="period-toggle">
          <button class:active={period === 'all'} onclick={() => onPeriodChange('all')}>All time</button>
          <button class:active={period === 'month'} onclick={() => onPeriodChange('month')}>This month</button>
        </div>
      </div>
      <div class="board">
        {#each leaderboard as user, index}
          <div class="card" class:champion={index === 0} class:elite={index < 3}>
            <div class="rank-badge" class:medal-badge={index < 3} class:gold={index === 0} class:silver={index === 1} class:bronze={index === 2}>
              {getMedal(index)}
            </div>
            <div class="card-info">
              <span class="card-name">{user.name}</span>
              {#if index < 3}
                <span class="card-tier">{getTierLabel(index)}</span>
              {/if}
            </div>
            <div class="card-amount">Rs {user.amount.toLocaleString('en-IN')}</div>
          </div>
        {:else}
          <div class="empty">
            <p>No supporters yet</p>
            <span>Be the first to get on the board.</span>
          </div>
        {/each}
      </div>
    </section>

    <section class="feed">
      <div class="section-header">
        <h2>Live Activity</h2>
        <span class="live-dot"></span>
      </div>
      <div class="feed-box">
        {#each activities as activity}
          <div class="feed-item">{activity.text}</div>
        {:else}
          <div class="empty">
            <p>Waiting for activity</p>
            <span>New payments will show up here in real time.</span>
          </div>
        {/each}
      </div>
    </section>
  </div>
</div>

{#if showSuccess}
  <div class="success-overlay" role="dialog" aria-modal="true" tabindex="-1">
    <div class="success-burst">
      <div class="success-glow success-glow-a"></div>
      <div class="success-glow success-glow-b"></div>
      <div class="success-orbit"></div>
      <div class="success-icon">✓</div>
      <p class="success-kicker">Payment successful</p>
      <p class="success-text">You are on the board.</p>
      <p class="success-amount">Rs {amount.toLocaleString('en-IN')} contributed</p>
      <p class="success-copy">{getSuccessMessage()}</p>
      {#if $isLoggedIn && mySummary?.display_name}
        <button class="share-btn" onclick={() => { showSuccess = false; showShareCard = true; }}>
          Share your rank
        </button>
      {/if}
      <button class="close-btn success-close" onclick={() => showSuccess = false}>Close</button>
    </div>
  </div>
{/if}

{#if showShareCard}
  <div
    class="success-overlay"
    role="button"
    tabindex="0"
    aria-label="Close rank card"
    onclick={() => showShareCard = false}
    onkeydown={(e) => e.key === 'Escape' && (showShareCard = false)}
  >
    <div class="rank-card" role="dialog" aria-modal="true" tabindex="-1" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
      <div class="rank-card-glow-a"></div>
      <div class="rank-card-glow-b"></div>
      <p class="rank-card-brand">CloutPay</p>
      <p class="rank-card-rank">
        {mySummary?.current_rank ? `#${mySummary.current_rank}` : '🔥'}
      </p>
      <p class="rank-card-name">{mySummary?.display_name ?? $displayName}</p>
      <p class="rank-card-total">Rs {(mySummary?.total_contributed ?? 0).toLocaleString('en-IN')} contributed</p>
      <div class="rank-card-actions">
        <button class="share-btn" onclick={shareRank}>Share</button>
        <button class="close-btn" onclick={() => showShareCard = false}>Close</button>
      </div>
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
    background:
      radial-gradient(circle at top, rgba(255, 77, 77, 0.12), transparent 28%),
      radial-gradient(circle at 80% 20%, rgba(255, 204, 0, 0.08), transparent 24%),
      #080808;
    color: white;
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
  }

  .hero {
    position: relative;
    padding: 200px 20px 72px;
    text-align: center;
  }

  .glow {
    position: absolute;
    border-radius: 999px;
    filter: blur(60px);
    pointer-events: none;
  }

  .glow-a {
    width: 520px;
    height: 520px;
    top: -120px;
    left: 45%;
    background: rgba(255, 77, 77, 0.18);
    transform: translateX(-50%);
  }

  .glow-b {
    width: 340px;
    height: 340px;
    top: 40px;
    left: 64%;
    background: rgba(255, 204, 0, 0.12);
  }

  .badge {
    display: inline-flex;
    align-items: center;
    padding: 7px 14px;
    border-radius: 999px;
    border: 1px solid rgba(255, 77, 77, 0.3);
    background: rgba(255, 77, 77, 0.08);
    font-size: 12px;
    color: #ff9a9a;
    margin-bottom: 24px;
  }

  /* ── Ticker ───────────────────────────────────── */
  .ticker-wrap {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 101;
    overflow: hidden;
    background: rgba(8, 8, 8, 0.92);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255, 77, 77, 0.15);
    padding: 7px 0;
  }

  .ticker-track {
    display: flex;
    gap: 48px;
    width: max-content;
    animation: ticker-scroll 28s linear infinite;
  }

  .ticker-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #ff9a9a;
    white-space: nowrap;
    font-weight: 500;
  }

  .ticker-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #ff4d4d;
    flex-shrink: 0;
  }

  @keyframes ticker-scroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
  }

  /* ── Spotlight card (guest) ───────────────────── */
  .spotlight-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 204, 0, 0.2);
    backdrop-filter: blur(8px);
    border-radius: 24px;
    padding: 28px 30px;
    text-align: center;
  }

  .spotlight-label {
    margin: 0 0 12px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #ffcc00;
    font-weight: 700;
  }

  .spotlight-name {
    margin: 0 0 6px;
    font-size: 1.6rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    color: white;
  }

  .spotlight-amount {
    margin: 0 0 10px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffdf71;
  }

  .spotlight-copy {
    margin: 0 0 20px;
    font-size: 13px;
    color: #666;
  }

  .spotlight-cta {
    display: block;
    padding: 12px;
    border-radius: 14px;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 800;
    font-size: 14px;
    text-decoration: none;
  }

  /* ── How it works ─────────────────────────────── */
  .how-it-works {
    max-width: 860px;
    margin: 0 auto;
    padding: 0 32px 64px;
  }

  .hiw-label {
    margin: 0 0 24px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #555;
    font-weight: 700;
    text-align: center;
  }

  .hiw-steps {
    display: flex;
    align-items: flex-start;
    gap: 0;
  }

  .hiw-step {
    flex: 1;
    padding: 24px 28px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
  }

  .hiw-num {
    display: block;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #ff4d4d;
    margin-bottom: 10px;
  }

  .hiw-step strong {
    display: block;
    font-size: 1.1rem;
    font-weight: 800;
    color: white;
    margin-bottom: 8px;
  }

  .hiw-step p {
    margin: 0;
    font-size: 13px;
    color: #666;
    line-height: 1.6;
  }

  .hiw-divider {
    width: 40px;
    flex-shrink: 0;
    height: 1px;
    background: rgba(255, 255, 255, 0.07);
    align-self: center;
  }

  h1 {
    font-size: clamp(2.9rem, 7vw, 5rem);
    line-height: 1.05;
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
    color: #979797;
    font-size: 1.05rem;
    max-width: 620px;
    margin: 0 auto 14px;
  }

  .welcome {
    margin: 0;
    color: #9b9b9b;
    font-size: 14px;
  }

  .name-highlight {
    color: #ffcc00;
    font-weight: 600;
  }

  .hero-grid {
    display: grid;
    grid-template-columns: minmax(0, 420px) minmax(0, 340px);
    gap: 20px;
    justify-content: center;
    align-items: start;
    max-width: 860px;
    margin: 30px auto 0;
  }

  .form-card,
  .personal-card,
  .card,
  .feed-item {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(8px);
  }

  .form-card,
  .personal-card {
    border-radius: 24px;
    padding: 28px 30px;
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
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.06);
    color: white;
    font-size: 14px;
    outline: none;
  }

  .amount-wrap {
    flex: 1;
    min-width: 120px;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    overflow: hidden;
  }

  .rupee {
    padding: 0 10px 0 14px;
    color: #8e8e8e;
    font-size: 13px;
    font-weight: 700;
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

  .quick-amounts {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .quick-btn {
    padding: 6px 14px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.04);
    color: #b0b0b0;
    font-size: 13px;
    cursor: pointer;
  }

  .quick-btn.active {
    background: rgba(255, 77, 77, 0.18);
    border-color: #ff4d4d;
    color: white;
  }

  .anon-toggle {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    color: #8e8e8e;
    font-size: 13px;
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
  }

  .cta:disabled,
  .quick-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .stats-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 14px;
    padding: 16px 20px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .stat {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: center;
    text-align: center;
  }

  .stat-value {
    font-size: 1.1rem;
    font-weight: 800;
    color: #fff2b6;
  }

  .stat-label,
  .personal-label {
    color: #757575;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .stat-divider {
    width: 1px;
    height: 38px;
    background: rgba(255, 255, 255, 0.08);
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
  }

  .section-header h2 {
    margin: 0;
    font-size: 0.96rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #d1d1d1;
  }

  .personal-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .personal-stat {
    padding: 14px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.07);
  }

  .personal-stat strong {
    display: block;
    margin-top: 7px;
    font-size: 1rem;
    line-height: 1.4;
  }

  .personal-copy {
    margin: 16px 0 0;
    color: #969696;
    font-size: 14px;
    line-height: 1.5;
  }

  .content {
    display: flex;
    gap: 24px;
    justify-content: center;
    padding: 0 32px 70px;
    flex-wrap: wrap;
    max-width: 940px;
    margin: 0 auto;
  }

  .leaderboard {
    width: 420px;
    max-width: 100%;
  }

  .feed {
    width: 390px;
    max-width: 100%;
  }

  .board,
  .feed-box {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border-radius: 16px;
  }

  .card.champion {
    border-color: rgba(255, 204, 0, 0.28);
    background: rgba(255, 204, 0, 0.07);
  }

  .card.elite {
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  }

  .rank-badge {
    width: 38px;
    font-weight: 800;
    color: #ffcc00;
    text-align: center;
    flex-shrink: 0;
  }

  .medal-badge {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    font-size: 1.25rem;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18);
  }

  .medal-badge.gold {
    background: radial-gradient(circle at 30% 30%, #fff0a8, #ffcb3d 60%, #a86e00);
    color: #3c2700;
  }

  .medal-badge.silver {
    background: radial-gradient(circle at 30% 30%, #ffffff, #cfd5de 60%, #818a96);
    color: #28303a;
  }

  .medal-badge.bronze {
    background: radial-gradient(circle at 30% 30%, #ffd3a1, #d68435 60%, #7c4514);
    color: #2d1605;
  }

  .card-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .card-name {
    font-size: 15px;
    font-weight: 600;
    color: #f0f0f0;
  }

  .card-tier {
    color: #7f7f7f;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .card-amount {
    font-size: 15px;
    font-weight: 700;
    color: #ffdf71;
  }

  .live-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #22c55e;
    box-shadow: 0 0 8px #22c55e;
  }

  .period-toggle {
    display: flex;
    gap: 4px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    padding: 3px;
  }

  .period-toggle button {
    padding: 5px 12px;
    border-radius: 999px;
    border: none;
    background: transparent;
    color: #777;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.18s, color 0.18s;
  }

  .period-toggle button.active {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .period-label {
    font-size: 11px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .feed-item {
    padding: 12px 16px;
    border-radius: 14px;
    color: #d0d0d0;
    font-size: 14px;
  }

  .empty {
    padding: 28px 20px;
    border-radius: 14px;
    text-align: center;
    border: 1px dashed rgba(255, 255, 255, 0.08);
  }

  .empty p {
    margin: 0 0 6px;
    color: #6c6c6c;
  }

  .empty span {
    color: #555;
    font-size: 12px;
  }

  .success-overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.8);
    z-index: 200;
  }

  .success-burst {
    position: relative;
    text-align: center;
    padding: 38px 34px;
    width: min(360px, calc(100vw - 40px));
    border-radius: 28px;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03)),
      rgba(10, 10, 10, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
    overflow: hidden;
  }

  .success-glow {
    position: absolute;
    border-radius: 999px;
    filter: blur(40px);
    pointer-events: none;
  }

  .success-glow-a {
    width: 180px;
    height: 180px;
    top: -60px;
    left: -10px;
    background: rgba(255, 77, 77, 0.28);
  }

  .success-glow-b {
    width: 160px;
    height: 160px;
    top: -30px;
    right: -20px;
    background: rgba(255, 204, 0, 0.22);
  }

  .success-orbit {
    position: absolute;
    inset: 18px;
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .success-icon {
    position: relative;
    z-index: 1;
    display: grid;
    place-items: center;
    width: 72px;
    height: 72px;
    margin: 0 auto 14px;
    border-radius: 50%;
    background: linear-gradient(180deg, #ffea8f, #ff9f3f);
    color: #201200;
    font-size: 2rem;
    font-weight: 900;
    box-shadow: 0 10px 30px rgba(255, 169, 64, 0.3);
  }

  .success-kicker {
    position: relative;
    z-index: 1;
    margin: 0;
    color: #ffcf78;
    font-size: 12px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
  }

  .success-text {
    position: relative;
    z-index: 1;
    margin: 10px 0 8px;
    font-size: 2rem;
    font-weight: 800;
  }

  .success-amount {
    position: relative;
    z-index: 1;
    margin: 0;
    color: #f3f3f3;
    font-size: 1.05rem;
    font-weight: 700;
  }

  .success-copy {
    position: relative;
    z-index: 1;
    margin: 14px 0 0;
    color: #aaaaaa;
    line-height: 1.5;
    font-size: 14px;
  }

  .share-btn {
    position: relative;
    z-index: 1;
    margin-top: 18px;
    padding: 11px 0;
    width: 100%;
    border-radius: 999px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
  }

  .rank-card {
    position: relative;
    text-align: center;
    padding: 44px 36px 36px;
    width: min(320px, calc(100vw - 40px));
    border-radius: 28px;
    background: linear-gradient(160deg, #1a1a1a, #0d0d0d);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
    overflow: hidden;
  }

  .rank-card-glow-a {
    position: absolute;
    width: 200px;
    height: 200px;
    top: -60px;
    left: -40px;
    border-radius: 999px;
    background: rgba(255, 77, 77, 0.22);
    filter: blur(50px);
    pointer-events: none;
  }

  .rank-card-glow-b {
    position: absolute;
    width: 180px;
    height: 180px;
    bottom: -40px;
    right: -30px;
    border-radius: 999px;
    background: rgba(255, 204, 0, 0.18);
    filter: blur(50px);
    pointer-events: none;
  }

  .rank-card-brand {
    position: relative;
    z-index: 1;
    margin: 0 0 20px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .rank-card-rank {
    position: relative;
    z-index: 1;
    margin: 0 0 8px;
    font-size: 4rem;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
    background: linear-gradient(180deg, #ffffff, #aaaaaa);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .rank-card-name {
    position: relative;
    z-index: 1;
    margin: 0 0 6px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0f0f0;
  }

  .rank-card-total {
    position: relative;
    z-index: 1;
    margin: 0 0 28px;
    font-size: 14px;
    color: #ffdf71;
    font-weight: 600;
  }

  .rank-card-actions {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .close-btn {
    padding: 11px 0;
    width: 100%;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.05);
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  }

  .success-close {
    position: relative;
    z-index: 1;
    margin-top: 10px;
  }

  @media (max-width: 900px) {
    .hero-grid {
      grid-template-columns: 1fr;
      max-width: 460px;
    }
    .hiw-steps {
      flex-direction: column;
      gap: 12px;
    }
    .hiw-divider {
      width: 1px;
      height: 24px;
      align-self: center;
    }
  }

  @media (max-width: 600px) {
    .hero {
      padding: 170px 16px 56px;
    }

    .form-card,
    .personal-card {
      padding: 20px;
    }

    .stats-bar {
      padding: 14px 12px;
      gap: 8px;
    }

    .stat-value {
      font-size: 0.96rem;
    }

    .personal-grid {
      grid-template-columns: 1fr;
    }

    .content {
      padding: 0 16px 48px;
    }

    .leaderboard,
    .feed {
      width: 100%;
    }

    .success-burst {
      padding: 34px 22px;
    }

    .how-it-works {
      padding: 0 16px 48px;
    }

    .hiw-step {
      padding: 18px 20px;
    }
  }
</style>
