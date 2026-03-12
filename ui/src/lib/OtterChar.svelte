<script>
  export let state = 'idle' // 'idle' | 'thinking' | 'done'

  // GIF パスは Python 側から assets/ をサーブ
  const gifs = {
    idle:     './otter/idle.gif',
    thinking: './otter/thinking.gif',
    speaking: './otter/speaking.gif',
    done:     './otter/done.gif',
  }

  $: src = gifs[state] ?? gifs.idle

</script>

<div class="otter-wrap">
  {#key src}
    <img
      {src}
      alt="Otter"
      class="otter-img"
      on:error={() => {}}
    />
  {/key}
</div>

<style>
  .otter-wrap {
    width: 72px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .otter-img {
    width: 72px;
    height: 72px;
    object-fit: contain;
    image-rendering: auto;
    border-radius: 8px;
  }
</style>
