<script>
  import { createEventDispatcher } from 'svelte'

  export let disabled = false
  export let showCopy = false

  const dispatch = createEventDispatcher()

  let text = ''
  let textarea

  function submit() {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    dispatch('submit', trimmed)
    text = ''
  }

  function onKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function paste() {
    if (navigator.clipboard) {
      navigator.clipboard.readText().then(t => {
        text += t
        textarea?.focus()
      })
    }
  }

  function copy() {
    dispatch('copy')
  }

  // コピー完了フィードバック
  let copyLabel = 'Copy response'
  function handleCopy() {
    copy()
    copyLabel = 'Copied!'
    setTimeout(() => copyLabel = 'Copy response', 1200)
  }
</script>

<div class="input-area">
  {#if showCopy}
    <div class="copy-row fade-in">
      <button class="copy-btn" on:click={handleCopy}>{copyLabel}</button>
    </div>
  {/if}

  <textarea
    bind:this={textarea}
    bind:value={text}
    on:keydown={onKeydown}
    {disabled}
    placeholder={disabled ? '考え中...' : 'メッセージを入力　Enter で送信'}
    rows="3"
    class="input-field"
    class:disabled
    data-testid="input-textarea"
  ></textarea>

  <div class="btn-row">
    <button class="paste-btn" on:click={paste} {disabled} data-testid="paste-button">
      Paste
    </button>
    <button
      class="send-btn"
      on:click={submit}
      disabled={disabled || !text.trim()}
      data-testid="send-button"
    >
      Send ↵
    </button>
  </div>
</div>

<style>
  .input-area {
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 10px 12px 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-shrink: 0;
  }
  .copy-row {
    display: flex;
  }
  .copy-btn {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-sub);
    font-size: 11px;
    padding: 3px 10px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .copy-btn:hover { background: var(--border); }

  .input-field {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-size: 14px;
    font-family: inherit;
    padding: 9px 12px;
    resize: none;
    outline: none;
    line-height: 1.5;
    transition: border-color 0.15s;
  }
  .input-field:focus { border-color: var(--accent); }
  .input-field.disabled { opacity: 0.5; cursor: not-allowed; }
  .input-field::placeholder { color: var(--text-sub); }

  .btn-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .paste-btn {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 14px;
    color: var(--text-sub);
    font-size: 12px;
    padding: 5px 14px;
    cursor: pointer;
    transition: background 0.15s;
  }
  .paste-btn:hover:not(:disabled) { background: var(--border); }
  .paste-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .send-btn {
    background: var(--accent);
    border: none;
    border-radius: 18px;
    color: #fff;
    font-size: 13px;
    font-weight: 600;
    padding: 7px 20px;
    cursor: pointer;
    transition: background 0.15s, opacity 0.15s;
  }
  .send-btn:hover:not(:disabled) { background: var(--accent-hover); }
  .send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
