<script>
  import { marked } from 'marked'
  import { tick } from 'svelte'

  export let text = ''
  export let visible = false

  let container

  $: html = text ? marked.parse(text) : ''

  $: if (visible && text) {
    tick().then(() => {
      if (container) container.scrollTop = 0
    })
  }
</script>

{#if visible && text}
  <div class="response-wrap fade-in" bind:this={container}>
    <div class="response-content">{@html html}</div>
  </div>
{:else if visible}
  <div class="empty-state">
    <span>どうした？気軽に聞いて 🦦</span>
  </div>
{/if}

<style>
  .response-wrap {
    flex: 1;
    overflow-y: auto;
    padding: 14px 16px;
    background: var(--bubble);
    font-size: 14px;
    line-height: 1.6;
    color: var(--text);
  }
  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-sub);
    font-size: 14px;
    background: var(--bubble);
  }
</style>
