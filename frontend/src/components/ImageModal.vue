<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto md:overflow-hidden bg-black bg-opacity-95 md:bg-opacity-90" @click.self="close">
    <!-- 响应式容器：移动端纵向排列，桌面端横向铺满 -->
    <div class="flex flex-col md:flex-row min-h-screen md:h-screen w-full md:p-4 md:gap-4" @click.self="close">
      
      <!-- 移动端关闭按钮 (悬浮于右上角) -->
      <button @click="close" class="md:hidden fixed top-4 right-4 z-50 px-3 py-1 text-sm text-white bg-black bg-opacity-60 border border-gray-600 rounded">
        关闭
      </button>

      <!-- 预览区 -->
      <div class="w-full md:flex-1 flex items-center justify-center relative min-h-[50vh] md:min-h-0" @click.self="close">
        <!-- 桌面端关闭按钮 -->
        <button @click="close" class="hidden md:block absolute top-0 right-0 px-3 py-1 text-white bg-red-600 hover:bg-red-700 rounded z-10">
          关闭
        </button>
        <!-- 图片样式：移动端宽度铺满高度自适应，桌面端限制最大宽高 -->
        <img :src="imageUrl" class="w-full h-auto md:w-auto md:max-w-full md:max-h-full md:object-contain block" />
      </div>
      
      <!-- 信息区 -->
      <div class="w-full md:w-80 bg-gray-900 md:bg-gray-800 p-4 md:rounded-lg md:overflow-y-auto border-t md:border border-gray-800 md:border-gray-700 shrink-0">
        <h2 class="text-xl font-bold mb-4 break-all text-gray-100">{{ detail?.filename }}</h2>
        <a :href="imageUrl" target="_blank" class="block text-center bg-blue-600 hover:bg-blue-700 text-white py-2 rounded mb-6 transition-colors">
          查看原图
        </a>
        
        <div v-if="detail?.tags">
          <div v-for="(tags, category) in detail.tags" :key="category" class="mb-4">
            <h3 class="text-gray-400 capitalize mb-2 text-sm">{{ category }}</h3>
            <div class="flex flex-wrap gap-2">
              <span v-for="tag in tags" :key="tag" 
                    class="px-2 py-1 bg-gray-800 md:bg-gray-700 border border-gray-700 md:border-none text-sm rounded text-gray-300 md:text-gray-200 cursor-pointer hover:bg-gray-600 transition-colors"
                    @click="$emit('add-tag', tag)">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import api from '../api'

const props = defineProps(['imgId', 'show'])
const emit = defineEmits(['close', 'add-tag'])

const detail = ref(null)
const imageUrl = ref('')

// 监听弹窗状态以控制底层页面的滚动
watch(() => props.show, (isShow) => {
  if (isShow) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
})

watch(() => props.imgId, async (newId) => {
  if (newId) {
    imageUrl.value = api.getImageUrl(newId)
    detail.value = await api.getImageDetail(newId)
  }
})

const close = () => {
  emit('close')
}
</script>
