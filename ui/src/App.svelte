<script>
  import { onMount } from 'svelte'
  import OtterChar from './lib/OtterChar.svelte'
  import ResponseArea from './lib/ResponseArea.svelte'
  import InputArea from './lib/InputArea.svelte'

  let otterState = $state('idle')   // 'idle' | 'thinking' | 'done'
  let statusMsg  = $state('Ready')
  let responseText = $state('')
  let showCopy = $state(false)

  // ── Python → JS グローバル関数 ─────────────────────────────────────────
  onMount(() => {
    window._otterSetState = (state) => {
      otterState = state.toLowerCase()
      showCopy = state === 'DONE'
      if (state === 'DONE') {
        setTimeout(() => { otterState = 'idle' }, 2000)
      }
    }
    window._otterSetStatus = (msg) => {
      statusMsg = msg
    }
    window._otterDisplayResponse = (text) => {
      responseText = text
    }
    window._otterClearResponse = () => {
      responseText = ''
      showCopy = false
    }

    if (window.pywebview) {
      window.pywebview.api.on_ready()
    }
  })

  // ── JS → Python ────────────────────────────────────────────────────────
  async function onSubmit(e) {
    const text = e.detail
    if (!window.pywebview) {
      console.log('[dev] submit:', text)
      return
    }
    await window.pywebview.api.submit_text(text)
  }

  async function onCopy() {
    if (window.pywebview) {
      await window.pywebview.api.copy_response()
    }
  }

  // ── ドラッグ（フレームレスウィンドウ用）────────────────────────────────
  let dragStart = $state(null)
  function onHeaderMousedown(e) {
    if (e.button !== 0) return
    dragStart = { mx: e.screenX, my: e.screenY }
  }
  function onMousemove(e) {
    if (!dragStart || !window.pywebview) return
    window.pywebview.api.move_window(e.screenX - dragStart.mx, e.screenY - dragStart.my)
    dragStart = { mx: e.screenX, my: e.screenY }
  }
  function onMouseup() { dragStart = null }

  let inputDisabled = $derived(otterState === 'thinking')
</script>

<svelte:window on:mousemove={onMousemove} on:mouseup={onMouseup} />

<div class="app-shell">
  <!-- ヘッダー（ドラッグ可能） -->
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <header
    class="header"
    on:mousedown={onHeaderMousedown}
  >
    <OtterChar state={otterState} />

    <div class="header-info">
      <span class="title">Otter</span>
      <span class="status" class:thinking={otterState === 'thinking'}>
        {statusMsg}
      </span>
    </div>

    <div class="header-actions">
      <button
        class="close-btn"
        on:click={() => window.pywebview?.api.close_session()}
        title="閉じる"
        data-testid="close-button"
      >✕</button>
    </div>
  </header>

  <!-- 応答エリア -->
  <div class="response-wrap">
    <ResponseArea text={responseText} visible={true} />
  </div>

  <!-- 入力エリア -->
  <InputArea
    disabled={inputDisabled}
    showCopy={showCopy}
    on:submit={onSubmit}
    on:copy={onCopy}
  />
</div>

<style>
  .app-shell {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg);
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 4px 16px rgba(0,0,0,0.4);
  }

  header.header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    cursor: grab;
    user-select: none;
    flex-shrink: 0;
  }
  header.header:active { cursor: grabbing; }

  .header-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.3px;
  }
  .status {
    font-size: 11px;
    color: var(--text-sub);
    transition: color 0.2s;
  }
  .status.thinking {
    color: var(--accent);
    animation: blink 1.2s ease-in-out infinite;
  }

  .header-actions {
    display: flex;
    align-items: center;
  }
  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-sub);
    font-size: 14px;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .close-btn:hover { background: #3a1a1a; color: #ff6b6b; }

  .response-wrap {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
</style>
