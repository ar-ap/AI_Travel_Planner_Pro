<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 shadow-lg z-[9999] md:hidden safe-area-bottom">
    <div class="flex items-center justify-around h-16 px-2">
      <router-link
        v-for="item in items"
        :key="item.key"
        :to="item.to"
        class="flex flex-col items-center justify-center flex-1 py-2 transition-all duration-200"
        :class="isActive(item.key) ? 'text-teal-500' : 'text-slate-400'"
      >
        <div 
          class="relative flex items-center justify-center w-12 h-8 transition-transform duration-200"
          :class="isActive(item.key) ? 'scale-110' : 'scale-100'"
        >
          <AppIcon 
            :name="item.icon" 
            :prefix="item.prefix" 
            class="text-2xl"
          />
          <!-- 激活指示器 -->
          <div 
            v-if="isActive(item.key)"
            class="absolute -top-1 w-1 h-1 rounded-full bg-teal-500"
          ></div>
        </div>
        <span 
          class="text-xs font-medium mt-1 transition-colors"
          :class="isActive(item.key) ? 'text-teal-500' : 'text-slate-500'"
        >
          {{ item.label }}
        </span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '@/components/common/AppIcon.vue'

type ActiveKey = 'planner' | 'qa' | 'copywriter' | 'settings'

interface NavigationItem {
  key: ActiveKey
  label: string
  to: string
  icon: string
  prefix?: 'fas' | 'far' | 'fab'
}

const props = withDefaults(
  defineProps<{
    items?: NavigationItem[]
  }>(),
  {
    items: () => [
      { key: 'planner', label: '行程', to: '/planner', icon: 'map', prefix: 'fas' },
      { key: 'qa', label: '助手', to: '/qa', icon: 'comment-dots', prefix: 'fas' },
      { key: 'copywriter', label: '文案', to: '/copywriter', icon: 'pen-nib', prefix: 'fas' },
      { key: 'settings', label: '设置', to: '/settings', icon: 'cog', prefix: 'fas' }
    ]
  }
)

const route = useRoute()

const isActive = (key: ActiveKey) => {
  const path = route.path
  switch (key) {
    case 'planner':
      return path.includes('/planner')
    case 'qa':
      return path.includes('/qa')
    case 'copywriter':
      return path.includes('/copywriter')
    case 'settings':
      return path.includes('/settings')
    default:
      return false
  }
}
</script>

<style scoped>
/* iOS 安全区域适配 */
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom);
}

/* 点击反馈效果 */
.flex-1:active {
  transform: scale(0.95);
}
</style>
