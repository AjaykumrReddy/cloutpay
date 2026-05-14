<script lang="ts">
  let { city = $bindable(''), region = $bindable(''), disabled = false } = $props();

  let pincode = $state('');
  let detecting = $state(false);
  let error = $state('');
  let mode = $state<'idle' | 'detected' | 'manual'>('idle');

  $effect(() => {
    if (city && region && mode === 'idle') mode = 'detected';
  });

  async function detectByGPS() {
    if (!navigator.geolocation) {
      error = 'Geolocation not supported by your browser';
      return;
    }
    detecting = true;
    error = '';
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords;
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`,
            { headers: { 'Accept-Language': 'en' } }
          );
          const data = await res.json();
          const addr = data.address || {};
          city = addr.city || addr.town || addr.village || addr.county || '';
          region = addr.state || '';
          mode = 'detected';
        } catch {
          error = 'Could not detect location. Try entering your pincode.';
        } finally {
          detecting = false;
        }
      },
      () => {
        error = 'Location permission denied. Try entering your pincode.';
        detecting = false;
        mode = 'manual';
      }
    );
  }

  async function detectByPincode() {
    const pin = pincode.trim();
    if (!/^\d{6}$/.test(pin)) { error = 'Enter a valid 6-digit pincode'; return; }
    detecting = true;
    error = '';
    try {
      const res = await fetch(`https://api.postalpincode.in/pincode/${pin}`);
      const data = await res.json();
      if (data[0]?.Status === 'Success' && data[0]?.PostOffice?.length > 0) {
        const po = data[0].PostOffice[0];
        city = po.District || po.Name || '';
        region = po.State || '';
        mode = 'detected';
      } else {
        error = 'Pincode not found. Please try again.';
      }
    } catch {
      error = 'Failed to fetch pincode data.';
    } finally {
      detecting = false;
    }
  }

  function clear() {
    city = '';
    region = '';
    pincode = '';
    error = '';
    mode = 'idle';
  }
</script>

<div class="location-picker">
  {#if mode === 'detected'}
    <div class="detected">
      <span class="detected-icon">📍</span>
      <span class="detected-text">{city}{city && region ? ', ' : ''}{region}</span>
      <button class="clear-btn" onclick={clear} {disabled} type="button">Change</button>
    </div>
  {:else}
    <div class="options">
      <button
        class="option-btn"
        onclick={detectByGPS}
        disabled={disabled || detecting}
        type="button"
      >
        {detecting && mode !== 'manual' ? '⏳ Detecting...' : '📍 Use my location'}
      </button>
      <span class="or">or</span>
      <button
        class="option-btn secondary"
        onclick={() => { mode = 'manual'; error = ''; }}
        {disabled}
        type="button"
      >
        Enter pincode
      </button>
    </div>

    {#if mode === 'manual'}
      <div class="pincode-row">
        <input
          type="tel"
          maxlength="6"
          placeholder="6-digit pincode"
          bind:value={pincode}
          {disabled}
          onkeydown={(e) => e.key === 'Enter' && detectByPincode()}
          class="pincode-input"
        />
        <button
          class="go-btn"
          onclick={detectByPincode}
          disabled={disabled || detecting}
          type="button"
        >
          {detecting ? '...' : 'Go'}
        </button>
      </div>
    {/if}

    {#if error}
      <p class="error">{error}</p>
    {/if}
  {/if}
</div>

<style>
  .location-picker { display: flex; flex-direction: column; gap: 8px; }

  .options { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

  .option-btn {
    padding: 9px 16px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.06);
    color: white;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .option-btn:hover:not(:disabled) { background: rgba(255,255,255,0.1); }
  .option-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .option-btn.secondary { color: #aaa; }
  .or { color: #444; font-size: 12px; }

  .pincode-row { display: flex; gap: 8px; }

  .pincode-input {
    flex: 1;
    padding: 9px 14px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.06);
    color: white;
    font-size: 14px;
    outline: none;
  }

  .pincode-input::placeholder { color: #555; }

  .go-btn {
    padding: 9px 18px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(90deg, #ff4d4d, #ffcc00);
    color: black;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
  }

  .go-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .detected {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-radius: 10px;
    background: rgba(255,204,0,0.07);
    border: 1px solid rgba(255,204,0,0.2);
  }

  .detected-icon { font-size: 1rem; }
  .detected-text { flex: 1; font-size: 14px; font-weight: 600; color: #ffdf71; }

  .clear-btn {
    background: none;
    border: none;
    color: #666;
    font-size: 12px;
    cursor: pointer;
    padding: 0;
    text-decoration: underline;
  }

  .clear-btn:hover { color: #aaa; }
  .error { margin: 0; font-size: 12px; color: #ff7070; }
</style>
