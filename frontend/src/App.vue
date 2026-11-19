<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-gray-100">
    <!-- 顶部导航条 -->
    <header class="bg-gray-800 border-b border-gray-700 p-3 sm:p-4 sticky top-0 z-40">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <!-- 标题与移动端控制按钮 -->
        <div class="flex items-center justify-between">
          <h1 class="text-xl sm:text-2xl font-bold text-blue-400">Local Booru</h1>
          <!-- 移动端侧边栏切换按钮 -->
          <button 
            @click="isSidebarOpen = !isSidebarOpen" 
            class="sm:hidden p-2 rounded bg-gray-700 hover:bg-gray-600 text-sm"
          >
            {{ isSidebarOpen ? '隐藏目录' : '显示目录' }}
          </button>
        </div>
        
        <!-- 搜索栏 -->
        <div class="flex-1 w-full max-w-none sm:max-w-3xl">
          <SearchBar v-model="searchTags" @search="resetAndSearch" />
        </div>
        
        <!-- 统计信息 -->
        <div class="text-xs sm:text-sm text-gray-400 text-right sm:text-left">
          总计: {{ totalItems }}
        </div>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden relative">
      <!-- 侧边栏 (移动端支持折叠，桌面端常驻) -->
      <aside 
        :class="[
          'bg-gray-900 border-r border-gray-700 overflow-y-auto transition-all duration-300 absolute sm:relative z-30 h-full',
          isSidebarOpen ? 'w-64 translate-x-0' : '-translate-x-full sm:translate-x-0 sm:w-64'
        ]"
      >
        <div class="p-4">
          <h2 class="text-lg font-semibold mb-4 text-gray-300">图库目录</h2>
          <div class="flex flex-col gap-3">
            <label v-for="dir in directories" :key="dir.path" class="flex items-center gap-3 cursor-pointer p-2 rounded hover:bg-gray-800 transition-colors">
              <input type="checkbox" :value="dir.path" v-model="selectedDirs" @change="resetAndSearch" class="accent-blue-600 w-5 h-5" />
              <span class="text-sm break-all text-gray-300 select-none" :title="dir.path">{{ dir.name }}</span>
            </label>
          </div>
        </div>
      </aside>

      <!-- 移动端侧边栏展开时的遮罩 -->
      <div 
        v-if="isSidebarOpen" 
        @click="isSidebarOpen = false" 
        class="sm:hidden absolute inset-0 bg-black bg-opacity-50 z-20"
      ></div>

      <!-- 右侧图片网格 -->
      <main class="flex-1 p-2 sm:p-4 overflow-y-auto h-full" @scroll="handleScroll">
        <div v-if="images.length === 0 && !loading" class="text-center text-gray-500 mt-20">
          没有找到匹配的图片
        </div>
        
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-4">
          <div v-for="img in images" :key="img.id" 
               class="aspect-square bg-gray-800 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-blue-500 group relative"
               @click="openImage(img.id)">
            <img :src="api.getImageUrl(img.id)" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200" />
          </div>
        </div>

        <div v-if="loading" class="text-center py-6 text-gray-400">
          <span class="inline-block animate-pulse">加载中...</span>
        </div>
      </main>
    </div>

    <!-- 图片详情弹窗 -->
    <ImageModal 
      :show="showModal" 
      :img-id="activeImgId" 
      @close="showModal = false"
      @add-tag="appendTagFromModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from './api'
import SearchBar from './components/SearchBar.vue'
import ImageModal from './components/ImageModal.vue'

// 状态
const directories = ref([])
const selectedDirs = ref([])
const searchTags = ref([])
const images = ref([])
const totalItems = ref(0)
const loading = ref(false)
const isSidebarOpen = ref(false) // 控制移动端侧边栏

// 分页
const skip = ref(0)
const limit = ref(50)
const hasMore = ref(true)

// Modal
const showModal = ref(false)
const activeImgId = ref(null)

onMounted(async () => {
  const config = await api.getConfig()
  limit.value = config.default_page_size
  directories.value = config.directories
  selectedDirs.value = config.directories.filter(d => d.default).map(d => d.path)
  
  if (selectedDirs.value.length === 0 && config.directories.length > 0) {
    selectedDirs.value.push(config.directories[0].path)
  }
  
  resetAndSearch()
})

const resetAndSearch = async () => {
  skip.value = 0
  images.value = []
  hasMore.value = true
  if (window.innerWidth < 640) {
      isSidebarOpen.value = false // 移动端搜索或切换目录后自动收起侧边栏
  }
  await loadImages()
}

const loadImages = async () => {
  if (loading.value || !hasMore.value) return
  loading.value = true
  
  try {
    const res = await api.search({
      tags: searchTags.value,
      directories: selectedDirs.value,
      skip: skip.value,
      limit: limit.value
    })
    
    images.value.push(...res.items)
    totalItems.value = res.total
    
    if (images.value.length >= res.total) {
      hasMore.value = false
    } else {
      skip.value += limit.value
    }
  } catch (error) {
    console.error("搜索失败:", error)
  } finally {
    loading.value = false
  }
}

const handleScroll = (e) => {
  const target = e.target
  if (target.scrollTop + target.clientHeight >= target.scrollHeight - 200) {
    loadImages()
  }
}

const openImage = (id) => {
  activeImgId.value = id
  showModal.value = true
}

const appendTagFromModal = (tag) => {
  if (!searchTags.value.includes(tag)) {
    searchTags.value.push(tag)
    showModal.value = false
    resetAndSearch()
  }
}
</script>

<style>
/* 隐藏移动端原生滚动条以保持界面整洁 */
main::-webkit-scrollbar {
  width: 6px;
}
main::-webkit-scrollbar-track {
  background: transparent;
}
main::-webkit-scrollbar-thumb {
  background-color: #4b5563;
  border-radius: 20px;
}
</style>
