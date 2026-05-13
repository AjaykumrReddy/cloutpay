<script lang="ts">
</script>

<svelte:head>
  <title>About Us · CloutPay</title>
</svelte:head>

<div class="page">
  <div class="container">
    <a href="/" class="back">← Back to home</a>
    <h1>About CloutPay</h1>

    <div class="hero-text">
      <p>CloutPay is a social leaderboard platform built for people who want to back their confidence with real money — and show the world exactly where they stand.</p>
    </div>

    <section>
      <h2>What is CloutPay?</h2>
      <p>CloutPay is a <strong>paid ranking platform</strong>. Users pay a participation fee to be listed on a live, public leaderboard. Your rank is determined by your total cumulative participation amount — the more you participate, the higher you rank.</p>
      <p>Think of it like a paid directory listing, but for social status. No prizes. No gambling. Just pure, transparent ranking based on how much you're willing to put in.</p>
    </section>

    <section>
      <h2>How It Works</h2>
      <div class="steps">
        <div class="step">
          <span class="num">01</span>
          <strong>Pay a participation fee</strong>
          <p>Choose any amount starting from Rs 10. Every rupee counts toward your rank.</p>
        </div>
        <div class="step">
          <span class="num">02</span>
          <strong>Get ranked instantly</strong>
          <p>Your name appears on the live leaderboard, ranked by total participation amount.</p>
        </div>
        <div class="step">
          <span class="num">03</span>
          <strong>Share your rank</strong>
          <p>Generate your rank card and share it. Let the world know where you stand.</p>
        </div>
      </div>
    </section>

    <section>
      <h2>What CloutPay is NOT</h2>
      <ul>
        <li>Not a lottery or gambling platform — there are no prizes or winnings</li>
        <li>Not a crowdfunding or donation platform — we are not a charity or NGO</li>
        <li>Not an investment platform — participation fees do not generate returns</li>
        <li>Not a subscription service — every payment is a one-time participation fee</li>
      </ul>
    </section>

    <section>
      <h2>Our Mission</h2>
      <p>We built CloutPay to create a transparent, real-money social ranking experience. In a world full of fake followers and inflated metrics, CloutPay is refreshingly honest — your rank is backed by actual money, not algorithms.</p>
    </section>

    <section>
      <h2>Legal & Compliance</h2>
      <p>CloutPay operates as a paid listing and ranking service under Indian law. We are committed to full compliance with applicable regulations. All payments are processed through licensed payment gateway partners.</p>
      <div class="links">
        <a href="/terms">Terms of Service</a>
        <a href="/privacy">Privacy Policy</a>
        <a href="/refund">Refund Policy</a>
        <a href="/contact">Contact Us</a>
      </div>
    </section>
  </div>
</div>

<style>
  .page { min-height: 100vh; background: #080808; color: white; font-family: 'Inter', sans-serif; padding: 100px 20px 60px; box-sizing: border-box; }
  .container { max-width: 720px; margin: 0 auto; }
  .back { color: #666; text-decoration: none; font-size: 13px; display: inline-block; margin-bottom: 32px; }
  .back:hover { color: #aaa; }
  h1 { font-size: 2.2rem; font-weight: 900; margin: 0 0 24px; background: linear-gradient(90deg, #ff4d4d, #ffcc00); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
  .hero-text p { font-size: 1.15rem; color: #ccc; line-height: 1.7; margin: 0 0 40px; border-left: 3px solid #ff4d4d; padding-left: 16px; }
  section { margin-bottom: 36px; padding-bottom: 36px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  section:last-child { border-bottom: none; }
  h2 { font-size: 1rem; font-weight: 700; color: #e0e0e0; margin: 0 0 12px; }
  p { color: #888; line-height: 1.7; font-size: 14px; margin: 0 0 10px; }
  ul { color: #888; font-size: 14px; line-height: 1.8; padding-left: 20px; margin: 8px 0; }
  strong { color: #ccc; }
  .steps { display: flex; flex-direction: column; gap: 16px; }
  .step { padding: 18px 20px; border-radius: 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); }
  .num { display: block; font-size: 11px; font-weight: 800; letter-spacing: 2px; color: #ff4d4d; margin-bottom: 6px; }
  .step strong { display: block; font-size: 15px; color: #e0e0e0; margin-bottom: 4px; }
  .step p { margin: 0; }
  .links { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 14px; }
  a { color: #ff9a9a; text-decoration: none; font-size: 14px; }
  a:hover { text-decoration: underline; }
</style>
