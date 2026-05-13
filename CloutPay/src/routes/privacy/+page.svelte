<script lang="ts">
</script>

<svelte:head>
  <title>Privacy Policy · CloutPay</title>
</svelte:head>

<div class="page">
  <div class="container">
    <a href="/" class="back">← Back to home</a>
    <h1>Privacy Policy</h1>
    <p class="updated">Last updated: June 2025</p>

    <section>
      <h2>1. Information We Collect</h2>
      <p>We collect the following information when you use CloutPay:</p>
      <ul>
        <li><strong>Phone number</strong> — used for OTP-based authentication</li>
        <li><strong>Display name</strong> — shown publicly on the leaderboard</li>
        <li><strong>City and state</strong> — optional, used for local leaderboards</li>
        <li><strong>Payment information</strong> — processed by our payment gateway; we only store the payment amount and reference ID, never your card or bank details</li>
      </ul>
    </section>

    <section>
      <h2>2. How We Use Your Information</h2>
      <ul>
        <li>To authenticate you via OTP login</li>
        <li>To display your name and rank on the public leaderboard</li>
        <li>To show you your personal contribution history and statistics</li>
        <li>To generate your shareable rank card</li>
        <li>To show location-based leaderboards (if you opt in)</li>
      </ul>
    </section>

    <section>
      <h2>3. Information We Do Not Collect</h2>
      <ul>
        <li>We do not collect your email address</li>
        <li>We do not store card numbers, UPI IDs, or bank account details</li>
        <li>We do not track your browsing activity outside CloutPay</li>
        <li>We do not sell your data to third parties</li>
      </ul>
    </section>

    <section>
      <h2>4. Data Sharing</h2>
      <p>We share minimal data only with:</p>
      <ul>
        <li><strong>Payment gateway</strong> — to process your participation fee securely</li>
        <li><strong>Cloud infrastructure providers</strong> — to host and operate the platform</li>
      </ul>
      <p>We do not share your personal data with advertisers or marketing companies.</p>
    </section>

    <section>
      <h2>5. Public Information</h2>
      <p>Your <strong>display name</strong> and <strong>participation amount</strong> are publicly visible on the leaderboard. If you choose to stay anonymous during a payment, your name will appear as "Anonymous". Your phone number is never made public.</p>
    </section>

    <section>
      <h2>6. Data Retention</h2>
      <p>We retain your account data for as long as your account is active. You may request deletion of your account and associated data by contacting us at <a href="/contact">our contact page</a>.</p>
    </section>

    <section>
      <h2>7. Security</h2>
      <p>We use industry-standard security practices including HTTPS encryption, secure token-based authentication, and access controls to protect your data.</p>
    </section>

    <section>
      <h2>8. Changes to This Policy</h2>
      <p>We may update this policy from time to time. We will notify users of significant changes by updating the date at the top of this page.</p>
    </section>

    <section>
      <h2>9. Contact</h2>
      <p>For any privacy-related concerns, please <a href="/contact">contact us</a>.</p>
    </section>
  </div>
</div>

<style>
  .page { min-height: 100vh; background: #080808; color: white; font-family: 'Inter', sans-serif; padding: 100px 20px 60px; box-sizing: border-box; }
  .container { max-width: 720px; margin: 0 auto; }
  .back { color: #666; text-decoration: none; font-size: 13px; display: inline-block; margin-bottom: 32px; }
  .back:hover { color: #aaa; }
  h1 { font-size: 2.2rem; font-weight: 900; margin: 0 0 6px; background: linear-gradient(90deg, #ff4d4d, #ffcc00); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
  .updated { color: #555; font-size: 13px; margin: 0 0 40px; }
  section { margin-bottom: 32px; padding-bottom: 32px; border-bottom: 1px solid rgba(255,255,255,0.06); }
  section:last-child { border-bottom: none; }
  h2 { font-size: 1rem; font-weight: 700; color: #e0e0e0; margin: 0 0 10px; }
  p { color: #888; line-height: 1.7; font-size: 14px; margin: 0 0 10px; }
  ul { color: #888; font-size: 14px; line-height: 1.8; padding-left: 20px; margin: 8px 0; }
  a { color: #ff9a9a; text-decoration: none; }
  a:hover { text-decoration: underline; }
  strong { color: #ccc; }
</style>
