<template>
  <aside class="hidden md:flex w-64 bg-white border-r border-slate-100 flex-col z-20 shadow-sm flex-shrink-0">
    <div class="p-6 flex items-center gap-2 text-teal-500">
      <AppIcon name="paper-plane" size="lg" />
      <span class="font-bold text-xl text-slate-800">WanderFlow</span>
    </div>

    <nav class="flex-1 mt-4">
      <router-link
        v-for="item in items"
        :key="item.key"
        :to="item.to"
        :class="navClass(item.key)"
      >
        <AppIcon :name="item.icon" :prefix="item.prefix" class="w-6" /> {{ item.label }}
      </router-link>
    </nav>

    <slot name="afterNav" />
    <slot name="footer" />
  </aside>
</template>

<script setup lang="ts">
import AppIcon from '@/components/common/AppIcon.vue'

type ActiveKey = 'planner' | 'qa' | 'copywriter' | 'settings'

interface SidebarItem {
  key: ActiveKey
  label: string
  to: string
  icon: string
  prefix?: 'fas' | 'far' | 'fab'
}

const props = withDefaults(
  defineProps<{
    active: ActiveKey
    items?: SidebarItem[]
  }>(),
  {
    items: () => [
      { key: 'planner', label: '规划行程', to: '/planner', icon: 'map', prefix: 'fas' },
      { key: 'qa', label: 'AI 助手', to: '/qa', icon: 'comment-dots', prefix: 'fas' },
      { key: 'copywriter', label: '文案生成', to: '/copywriter', icon: 'pen-nib', prefix: 'fas' },
      { key: 'settings', label: '账户设置', to: '/settings', icon: 'cog', prefix: 'fas' }
    ]
  }
)

const navClass = (key: ActiveKey) => (props.active === key ? 'nav-item active' : 'nav-item')
</script>
