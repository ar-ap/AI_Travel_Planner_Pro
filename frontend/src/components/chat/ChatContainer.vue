<template>
  <main class="flex-1 flex flex-col relative bg-slate-50 min-h-0" :class="$attrs.class">
    <header class="h-16 bg-white/80 backdrop-blur border-b border-slate-100 flex items-center px-6">
      <slot name="header" />
    </header>
    <div class="flex-1 overflow-y-auto p-6 pb-24 md:pb-6">
      <slot name="body" />
    </div>
    <div class="p-6 pb-20 md:pb-6 bg-white border-t border-slate-100">
      <slot name="footer" />
    </div>
  </main>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false
})
</script>
