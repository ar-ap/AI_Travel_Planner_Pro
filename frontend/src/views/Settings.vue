<template>
  <div class="bg-[#F8FAFC] h-screen md:flex md:overflow-hidden">
    <AppSidebar active="settings" />

    <main class="flex-1 overflow-y-auto p-8 relative pb-24 md:pb-8">
      <div class="fixed top-0 right-0 w-[500px] h-[500px] bg-blue-50 rounded-full filter blur-[80px] -z-10"></div>

      <div class="max-w-5xl mx-auto space-y-8">
        <h2 class="text-2xl font-bold text-slate-800">账户与设置</h2>

        <UserProfile
          :user-name="user?.name || ''"
          :email="user?.email || ''"
          :membership="membership"
          :level="level"
          :avatar-url="avatarUrl"
          :phone="user?.phone || ''"
          :gender="user?.gender || ''"
          :birth-date="user?.birth_date || ''"
          :city="user?.city || ''"
          :country="user?.country || ''"
          :bio="user?.bio || ''"
          :preferred-language="user?.preferred_language || ''"
          :preferred-currency="user?.preferred_currency || ''"
          @edit="handleEditProfile"
        />

        <div class="grid md:grid-cols-2 gap-6">
          <PreferenceSettings
            :language="language"
            :currency="currency"
            :dark-mode="darkMode"
            @update:language="language = $event"
            @update:currency="currency = $event"
            @update:darkMode="darkMode = $event"
          />
          <SecuritySettings />
          <SubscriptionInfo :user="user" />
        </div>

        <div class="text-center pt-8">
          <AppButton variant="ghost" size="sm" class="text-red-500 hover:text-red-600" @click="handleLogout">
            退出登录
          </AppButton>
        </div>
      </div>
    </main>

    <!-- 移动端底部导航 -->
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/common/AppSidebar.vue'
import AppButton from '@/components/common/AppButton.vue'
import UserProfile from '@/components/settings/UserProfile.vue'
import PreferenceSettings from '@/components/settings/PreferenceSettings.vue'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'
import SubscriptionInfo from '@/components/settings/SubscriptionInfo.vue'
import { useAuthStore } from '@/stores/auth'
import BottomNavigation from '@/components/common/BottomNavigation.vue'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// 用户偏好设置
const language = ref('简体中文')
const currency = ref('CNY (￥)')
const darkMode = ref(false)

// 计算属性
const membership = computed(() => {
  if (!user.value) return '免费会员'
  const levels: Record<string, string> = {
    'free': '免费会员',
    'basic': '基础会员',
    'pro': 'Pro 会员',
    'premium': '高级会员'
  }
  return levels[user.value.membership_level] || '免费会员'
})

const level = computed(() => {
  if (!user.value) return 'Lv.1 新手'
  return 'Lv.5 旅行家'
})

const avatarUrl = computed(() => {
  if (user.value) {
    return `https://i.pravatar.cc/150?u=${user.value.id}`
  }
  return 'https://i.pravatar.cc/150?img=12'
})

const handleEditProfile = () => {
  router.push('/profile/edit')
}

// 退出登录
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
