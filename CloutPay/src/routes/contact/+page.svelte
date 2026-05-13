<script lang="ts">
</script>

<svelte:head>
  <title>Contact Us · CloutPay</title>
</svelte:head>

<div class="page">
  <div class="container">
    <a href="/" class="back">← Back to home</a>
    <h1>Contact Us</h1>
    <p class="sub">Have a question, issue, or feedback? We're here to help.</p>

    <div class="cards">
      <div class="card">
        <span class="icon">📧</span>
        <h2>Email</h2>
        <p>For general queries, payment issues, or refund requests:</p>
        <a href="mailto:support@cloutpay.in">support@cloutpay.in</a>
      </div>

      <div class="card">
        <span class="icon">⏱️</span>
        <h2>Response Time</h2>
        <p>We typically respond within <strong>1–2 business days</strong>. For urgent payment issues, mention your payment reference ID in the subject line.</p>
      </div>

      <div class="card">
        <span class="icon">📍</span>
        <h2>Business Address</h2>
        <p>CloutPay<br />India</p>
      </div>
    </div>

    <div class="topics">
      <h2>Common Topics</h2>
      <div class="topic-links">
        <a href="/refund">Refund & Cancellation Policy →</a>
        <a href="/privacy">Privacy Policy →</a>
        <a href="/terms">Terms of Service →</a>
        <a href="/about">About CloutPay →</a>
      </div>
    </div>
  </div>
</div>

<style>
  .page { min-height: 100vh; background: #080808; color: white; font-family: 'Inter', sans-serif; padding: 100px 20px 60px; box-sizing: border-box; }
  .container { max-width: 720px; margin: 0 auto; }
  .back { color: #666; text-decoration: none; font-size: 13px; display: inline-block; margin-bottom: 32px; }
  .back:hover { color: #aaa; }
  h1 { font-size: 2.2rem; font-weight: 900; margin: 0 0 8px; background: linear-gradient(90deg, #ff4d4d, #ffcc00); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
  .sub { color: #666; font-size: 14px; margin: 0 0 36px; }
  .cards { display: flex; flex-direction: column; gap: 14px; margin-bottom: 40px; }
  .card { padding: 22px 24px; border-radius: 18px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); }
  .icon { font-size: 1.4rem; display: block; margin-bottom: 10px; }
  h2 { font-size: 0.95rem; font-weight: 700; color: #e0e0e0; margin: 0 0 8px; }
  p { color: #888; font-size: 14px; line-height: 1.6; margin: 0 0 8px; }
  strong { color: #ccc; }
  a { color: #ff9a9a; text-decoration: none; font-size: 14px; }
  a:hover { text-decoration: underline; }
  .topics h2 { font-size: 0.95rem; font-weight: 700; color: #e0e0e0; margin: 0 0 14px; }
  .topic-links { display: flex; flex-direction: column; gap: 10px; }
  .topic-links a { color: #666; font-size: 14px; }
  .topic-links a:hover { color: #aaa; }
</style>
