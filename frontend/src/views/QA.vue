<template>
  <div class="bg-[#F8FAFC] h-screen flex flex-col md:flex-row md:overflow-hidden">
    <AppSidebar active="qa">
      <template #afterNav>
        <div class="p-4 border-t border-slate-100">
          <div class="bg-teal-50 rounded-xl p-4">
            <h4 class="text-sm font-bold text-teal-800 mb-1">对话模式</h4>
             <div class="space-y-2 text-xs">
               <div class="flex items-center gap-2 text-slate-600">
                 <AppIcon name="circle" size="xs" class="text-green-500" />
                 <span>智能对话</span>
               </div>
               <div class="flex items-center gap-2 text-slate-600">
                 <AppIcon name="circle" size="xs" class="text-yellow-500" />
                 <span>天气查询</span>
               </div>
             </div>
          </div>
        </div>
      </template>
    </AppSidebar>

    <ChatContainer>
      <template #header>
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <h2 class="text-lg font-bold text-slate-700">WanderBot 智能向导</h2>
            <span class="text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">在线</span>
          </div>
          <div class="flex items-center gap-3">
            <FeatureToggle
              :label="`天气: ${weatherEnabled ? 'ON' : 'OFF'}`"
              icon="cloud-sun"
              :active="weatherEnabled"
              active-class="bg-yellow-200 text-yellow-700"
              inactive-class="bg-yellow-100 text-yellow-600"
              @toggle="toggleFeature('weather')"
            />
          </div>
        </div>
      </template>

      <template #body>
        <div class="max-w-4xl mx-auto space-y-6">
          <div v-if="messages.length === 0" class="flex justify-center fade-in-up">
            <div class="glass-card p-6 max-w-2xl text-center">
              <div class="w-16 h-16 bg-gradient-to-br from-teal-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl shadow-lg float-anim">
                <AppIcon name="robot" size="lg" />
              </div>
              <h3 class="text-xl font-bold text-slate-800 mb-2">嗨，我是您的全能旅行助理！</h3>
              <p class="text-slate-500 text-sm mb-6">您可以向我咨询天气、签证政策、行程规划或任何旅行问题。</p>
              <QuickQuestions :questions="quickQuestions" @select="handleQuickQuestion">
                <template #icon="{ question }">
                  <AppIcon
                    :name="quickQuestionIcon(question).name"
                    :class="`mr-2 ${quickQuestionIcon(question).className}`"
                  />
                </template>
              </QuickQuestions>
            </div>
          </div>

          <MessageList :messages="messages" />
        </div>
      </template>

      <template #footer>
        <div class="max-w-4xl mx-auto">
          <WeatherPanel
            :visible="weatherEnabled"
            :city="weatherCity"
            :loading="weatherLoading"
            :error="weatherError"
            :results="weatherResults"
            @update:city="weatherCity = $event"
            @query="queryWeather"
            @close="weatherEnabled = false"
          />

          <InputBox
            v-model="inputMessage"
            placeholder="输入您的问题..."
            @send="sendMessage"
          />
          <div class="flex justify-center mt-3">
            <div class="flex gap-2 text-xs text-slate-400">
              <span><AppIcon name="keyboard" class="mr-1" />Enter 发送</span>
              <span>|</span>
              <span><AppIcon name="magic" class="mr-1" />点击快捷问题</span>
            </div>
          </div>
        </div>
      </template>
    </ChatContainer>
  </div>

  <!-- 移动端底部导航 - 使用Teleport确保固定在最上层 -->
  <Teleport to="body">
    <BottomNavigation />
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import AppSidebar from '@/components/common/AppSidebar.vue'
import AppIcon from '@/components/common/AppIcon.vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import FeatureToggle from '@/components/chat/FeatureToggle.vue'
import MessageList from '@/components/chat/MessageList.vue'
import InputBox from '@/components/chat/InputBox.vue'
import QuickQuestions from '@/components/chat/QuickQuestions.vue'
import WeatherPanel from '@/components/chat/WeatherPanel.vue'

import { useQaStore } from '@/stores/qa'
import api from '@/utils/api'

interface WeatherItem {
  date: string
  icon: string
  desc: string
  high: number
  low: number
  humidity: number
  wind: number
}

const qaStore = useQaStore()
const { messages } = storeToRefs(qaStore)

const inputMessage = ref('')
const weatherEnabled = ref(false)

const weatherCity = ref('')
const weatherLoading = ref(false)
const weatherResults = ref<WeatherItem[]>([])
const weatherError = ref('')



const quickQuestions = [
  '查询北京未来3天的天气',
  '帮我制定一个3天上海旅行计划',
  '泰国签证办理需要哪些材料？',
  '播放刚才的回复'
]

const quickQuestionIcon = (question: string) => {
  if (question.includes('天气')) return { name: 'cloud-sun', className: 'text-yellow-500' }
  if (question.includes('行程')) return { name: 'map-marked-alt', className: 'text-green-500' }
  if (question.includes('签证')) return { name: 'passport', className: 'text-blue-500' }
  return { name: 'volume-up', className: 'text-purple-500' }
}

const toggleFeature = (feature: 'weather') => {
  if (feature === 'weather') weatherEnabled.value = !weatherEnabled.value
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  const message = inputMessage.value
  inputMessage.value = ''
  await qaStore.sendMessage(message, {
    weather: weatherEnabled.value
  })
}

const handleQuickQuestion = (question: string) => {
  inputMessage.value = question
  void sendMessage()
}

const queryWeather = () => {
  if (!weatherCity.value.trim()) return
  weatherLoading.value = true
  weatherResults.value = []
  weatherError.value = ''
  const city = weatherCity.value.trim()

  void (async () => {
    try {
      const response = await api.get<any>(`/api/v1/qa/weather/${encodeURIComponent(city)}`)
      const payload = response?.data ?? response
      const forecast = payload?.forecast || []

      if (!forecast.length) {
        weatherError.value = '暂无可用天气数据'
        return
      }

      const hasValidCodes = forecast.every((item: any) => Number.isFinite(Number(item.weather_code)))
      if (!hasValidCodes) {
        console.warn('天气接口返回的 weather_code 缺失，可能仍在使用演示数据:', forecast)
        weatherError.value = '天气数据无效，请确认后端已更新为真实天气服务'
        return
      }

      weatherResults.value = forecast.map((item: any) => {
        const { icon, desc } = mapWeather(item)
        return {
          date: formatDate(item.date),
          icon,
          desc,
          high: item.temp_high,
          low: item.temp_low,
          humidity: item.humidity,
          wind: item.wind
        }
      })
    } catch (error) {
      console.error('天气查询失败:', error)
      weatherError.value = '天气查询失败，请稍后再试'
    } finally {
      weatherLoading.value = false
    }
  })()
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const mapWeather = (item: any) => {
  const code = Number(item.weather_code)
  const desc = item.weather || '未知'
  const iconMap: Record<number, string> = {
    0: '☀️',
    1: '⛅',
    2: '⛅',
    3: '☁️',
    45: '🌫️',
    48: '🌫️',
    51: '🌦️',
    53: '🌦️',
    55: '🌧️',
    56: '🌧️',
    57: '🌧️',
    61: '🌧️',
    63: '🌧️',
    65: '🌧️',
    66: '🌧️',
    67: '🌧️',
    71: '❄️',
    73: '❄️',
    75: '❄️',
    77: '❄️',
    80: '🌦️',
    81: '🌦️',
    82: '⛈️',
    85: '❄️',
    86: '❄️',
    95: '⛈️',
    96: '⛈️',
    99: '⛈️'
  }
  return {
    icon: iconMap[code] || '☁️',
    desc
  }
}


</script>
