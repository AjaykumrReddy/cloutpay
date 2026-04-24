<script lang="ts">
  import { goto } from '$app/navigation';
  import { sendOtp, verifyOtp, authStore } from '$lib/auth';

  type Step = 'phone' | 'otp';

  let step = $state<Step>('phone');
  let phone = $state('');
  let code = $state('');
  let loading = $state(false);
  let error = $state('');

  async function handleSendOtp() {
    error = '';
    if (!/^[6-9]\d{9}$/.test(phone.trim())) {
      error = 'Enter a valid 10-digit Indian mobile number';
      return;
    }
    loading = true;
    try {
      await sendOtp(phone.trim());
      step = 'otp';
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function handleVerifyOtp() {
    error = '';
    if (!/^\d{6}$/.test(code.trim())) {
      error = 'Enter the 6-digit OTP';
      return;
    }
    loading = true;
    try {
      const result = await verifyOtp(phone.trim(), code.trim());
      authStore.setAuth(result.token, result.display_name);

      // New user with no name → profile setup, else go home
      if (result.is_new_user || !result.display_name) {
        goto('/profile/setup');
      } else {
        goto('/');
      }
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="page">
  <div class="glow"></div>

  <div class="card">
    <h1>CloutPay</h1>
    <p class="sub">Login to track your clout 🔥</p>

    {#if step === 'phone'}
      <div class="field">
        <span class="prefix">+91</span>
        <input
          type="tel"
          maxlength="10"
          placeholder="Mobile number"
          bind:value={phone}
          disabled={loading}
          onkeydown={(e) => e.key === 'Enter' && handleSendOtp()}
        />
      </div>
      <button class="btn" onclick={handleSendOtp} disabled={loading}>
        {loading ? 'Sending...' : 'Send OTP'}
      </button>
    {:else}
      <p class="hint">OTP sent to +91 {phone} · <button class="link" onclick={() => { step = 'phone'; code = ''; error = ''; }}>Change</button></p>
      <input
        class="otp-input"
        type="tel"
        maxlength="6"
        placeholder="Enter 6-digit OTP"
        bind:value={code}
        disabled={loading}
        onkeydown={(e) => e.key === 'Enter' && handleVerifyOtp()}
      />
      <button class="btn" onclick={handleVerifyOtp} disabled={loading}>
        {loading ? 'Verifying...' : 'Verify OTP'}
      </button>
    {/if}

    {#if error}
      <p class="error">{error}</p>
    {/if}

    <a href="/" class="skip">Continue as guest →</a>
  </div>
</div>

<style>
  .page {
    min-height: 100vh;
    background: radial-gradient(circle at top, #1a1a1a, #0a0a0a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    position: relative;
  }

  .glow {
    position: absolute;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(255, 0, 0, 0.25), transparent);
    top: -100px;
    left: 50%;
    transform: translateX(-50%);
    filter: blur(120px);
    pointer-events: none;
  }

  .card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 40px 36px;
    width: 360px;
    text-align: center;
    color: white;
    position: relative;
    z-index: 1;
  }

  h1 {
    font-size: 2rem;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px;
  }

  .sub {
    color: #aaa;
    font-size: 14px;
    margin-bottom: 28px;
  }

  .field {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 14px;
  }

  .prefix {
    padding: 12px 14px;
    color: #aaa;
    font-size: 14px;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    white-space: nowrap;
  }

  .field input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: white;
    font-size: 15px;
    padding: 12px 14px;
  }

  .field input::placeholder { color: #666; }

  .otp-input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    color: white;
    font-size: 22px;
    letter-spacing: 8px;
    text-align: center;
    padding: 12px;
    outline: none;
    margin-bottom: 14px;
  }

  .otp-input::placeholder { letter-spacing: 2px; font-size: 14px; color: #666; }

  .btn {
    width: 100%;
    padding: 13px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    font-size: 15px;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .btn:disabled { opacity: 0.55; cursor: not-allowed; }

  .hint {
    font-size: 13px;
    color: #888;
    margin-bottom: 14px;
  }

  .link {
    background: none;
    border: none;
    color: #ff4d4d;
    cursor: pointer;
    font-size: 13px;
    padding: 0;
    text-decoration: underline;
  }

  .error {
    color: #ff4d4d;
    font-size: 13px;
    margin-top: 12px;
  }

  .skip {
    display: block;
    margin-top: 20px;
    color: #555;
    font-size: 13px;
    text-decoration: none;
  }

  .skip:hover { color: #888; }
</style>
