<script lang="ts">
  import { toast } from '$lib/toast';
</script>

<div class="toast-container">
  {#each $toast as t (t.id)}
    <div class="toast {t.type}">
      <span class="icon">
        {#if t.type === 'success'}✅{:else if t.type === 'error'}❌{:else}ℹ️{/if}
      </span>
      {t.message}
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: 28px;
    right: 24px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    z-index: 9999;
    pointer-events: none;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: 12px;
    font-size: 14px;
    font-family: 'Inter', sans-serif;
    color: white;
    min-width: 220px;
    max-width: 340px;
    backdrop-filter: blur(10px);
    animation: slideUp 0.3s ease;
  }

  .toast.success { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); }
  .toast.error   { background: rgba(239, 68, 68, 0.15);  border: 1px solid rgba(239, 68, 68, 0.3); }
  .toast.info    { background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); }

  .icon { font-size: 16px; flex-shrink: 0; }

  @keyframes slideUp {
    from { transform: translateY(16px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
  }

  @media (max-width: 480px) {
    .toast-container {
      bottom: 16px;
      right: 12px;
      left: 12px;
    }
    .toast { max-width: 100%; }
  }
</style>
