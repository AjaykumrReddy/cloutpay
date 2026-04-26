<script lang="ts">
  import { PUBLIC_API_BASE } from '$env/static/public';

  let { data } = $props();

  const rankText = $derived(data.rank ? `Rank #${data.rank} on CloutPay` : 'On the CloutPay board');
  const totalText = $derived(`Rs ${data.total.toLocaleString('en-IN')} contributed`);
  const cardUrl = $derived(`${PUBLIC_API_BASE}/share/${data.shareToken}/card.png`);
</script>

<svelte:head>
  <title>{data.name} · CloutPay</title>
  <meta property="og:title" content="{data.name} is {rankText}" />
  <meta property="og:description" content="{totalText}. Can you beat them?" />
  <meta property="og:image" content={cardUrl} />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{data.name} is {rankText}" />
  <meta name="twitter:description" content="{totalText}. Can you beat them?" />
  <meta name="twitter:image" content={cardUrl} />
</svelte:head>

<div class="page">
  <div class="glow-a"></div>
  <div class="glow-b"></div>

  <div class="card">
    <p class="brand">CloutPay</p>

    {#if data.name}
      <p class="rank">{data.rank ? `#${data.rank}` : '🔥'}</p>
      <p class="name">{data.name}</p>
      <p class="total">{totalText}</p>
      <p class="tagline">{data.rank === 1 ? 'Leading the board.' : 'Can you beat them?'}</p>
    {:else}
      <p class="rank">🔥</p>
      <p class="name">CloutPay</p>
      <p class="total">Turn Money Into Status</p>
    {/if}

    <a href="/" class="cta">Get on the board</a>
  </div>
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

  :global(body) {
    margin: 0;
    background: #080808;
  }

  .page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(circle at top, rgba(255, 77, 77, 0.14), transparent 30%),
      radial-gradient(circle at 80% 80%, rgba(255, 204, 0, 0.08), transparent 30%),
      #080808;
    font-family: 'Inter', sans-serif;
    position: relative;
    overflow: hidden;
    padding: 20px;
    box-sizing: border-box;
  }

  .glow-a {
    position: absolute;
    width: 500px;
    height: 500px;
    top: -160px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 999px;
    background: rgba(255, 77, 77, 0.18);
    filter: blur(80px);
    pointer-events: none;
  }

  .glow-b {
    position: absolute;
    width: 300px;
    height: 300px;
    bottom: -80px;
    right: -60px;
    border-radius: 999px;
    background: rgba(255, 204, 0, 0.12);
    filter: blur(80px);
    pointer-events: none;
  }

  .card {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 52px 40px 44px;
    width: min(360px, 100%);
    border-radius: 32px;
    background:
      linear-gradient(160deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02)),
      rgba(10, 10, 10, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 32px 80px rgba(0, 0, 0, 0.5);
    color: white;
  }

  .brand {
    margin: 0 0 28px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .rank {
    margin: 0 0 10px;
    font-size: 5rem;
    font-weight: 900;
    letter-spacing: -3px;
    line-height: 1;
    background: linear-gradient(180deg, #ffffff 40%, #888888);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .name {
    margin: 0 0 8px;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0f0f0;
  }

  .total {
    margin: 0 0 6px;
    font-size: 1rem;
    font-weight: 600;
    color: #ffdf71;
  }

  .tagline {
    margin: 0 0 32px;
    font-size: 13px;
    color: #666;
  }

  .cta {
    display: block;
    padding: 14px;
    border-radius: 14px;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 800;
    font-size: 15px;
    text-decoration: none;
    transition: opacity 0.2s;
  }

  .cta:hover {
    opacity: 0.9;
  }
</style>
