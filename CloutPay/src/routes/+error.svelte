<script lang="ts">
  import { page } from '$app/stores';
</script>

<svelte:head>
  <title>{$page.status} · CloutPay</title>
</svelte:head>

<div class="page">
  <div class="glow-a"></div>
  <div class="glow-b"></div>

  <div class="card">
    <p class="brand">CloutPay</p>
    <p class="code">{$page.status}</p>
    <p class="title">
      {$page.status === 404 ? 'This page does not exist.' : 'Something went wrong.'}
    </p>
    <p class="sub">
      {$page.status === 404
        ? 'The link might be broken or the page may have moved.'
        : $page.error?.message || 'An unexpected error occurred.'}
    </p>
    <a href="/" class="cta">Back to the board</a>
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
      radial-gradient(circle at top, rgba(255, 77, 77, 0.12), transparent 30%),
      #080808;
    font-family: 'Inter', sans-serif;
    color: white;
    position: relative;
    overflow: hidden;
    padding: 100px 20px 40px;
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
    background: rgba(255, 77, 77, 0.16);
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
    background: rgba(255, 204, 0, 0.1);
    filter: blur(80px);
    pointer-events: none;
  }

  .card {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 52px 40px 44px;
    width: min(400px, 100%);
    border-radius: 32px;
    background:
      linear-gradient(160deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)),
      rgba(10, 10, 10, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 32px 80px rgba(0, 0, 0, 0.5);
  }

  .brand {
    margin: 0 0 24px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .code {
    margin: 0 0 8px;
    font-size: 5.5rem;
    font-weight: 900;
    letter-spacing: -4px;
    line-height: 1;
    background: linear-gradient(180deg, #ffffff 40%, #444);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .title {
    margin: 0 0 10px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e0e0e0;
  }

  .sub {
    margin: 0 0 32px;
    font-size: 13px;
    color: #555;
    line-height: 1.6;
    max-width: 280px;
    margin-left: auto;
    margin-right: auto;
  }

  .cta {
    display: block;
    padding: 13px;
    border-radius: 14px;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 800;
    font-size: 15px;
    text-decoration: none;
  }

  .cta:hover {
    opacity: 0.9;
  }
</style>
