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

      <!-- 右侧主要内容区 -->
      <main ref="mainContent" class="flex-1 p-2 sm:p-4 overflow-y-auto h-full flex flex-col">
        <div v-if="images.length === 0 && !loading" class="text-center text-gray-500 mt-20 flex-1">
          没有找到匹配的图片
        </div>
        
        <div v-if="loading" class="text-center py-6 text-gray-400 flex-1 flex items-center justify-center">
          <span class="inline-block animate-pulse text-lg">加载中...</span>
        </div>

        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-4 flex-1 content-start">
          <div v-for="img in images" :key="img.id" 
               class="aspect-square bg-gray-800 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-blue-500 group relative"
               @click="openImage(img.id)">
            <img :src="api.getImageUrl(img.id)" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200" />
          </div>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalPages > 1 && !loading" class="mt-6 mb-4 flex flex-wrap justify-center items-center gap-2">
          <button 
            @click="changePage(1)" 
            :disabled="currentPage === 1"
            class="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded border border-gray-700 transition-colors"
          >首页</button>
          
          <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded border border-gray-700 transition-colors"
          >上一页</button>
          
          <span class="px-4 py-1 text-gray-300">
            第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
          </span>
          
          <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded border border-gray-700 transition-colors"
          >下一页</button>
          
          <button 
            @click="changePage(totalPages)" 
            :disabled="currentPage === totalPages"
            class="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded border border-gray-700 transition-colors"
          >尾页</button>
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
import { ref, computed, onMounted } from 'vue'
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
const isSidebarOpen = ref(false)
const mainContent = ref(null) // 用于翻页后回到顶部

// 分页状态
const currentPage = ref(1)
const limit = ref(50)

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(totalItems.value / limit.value) || 1
})

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
  currentPage.value = 1
  images.value = []
  if (window.innerWidth < 640) {
      isSidebarOpen.value = false
  }
  await loadImages()
}

const loadImages = async () => {
  if (loading.value) return
  loading.value = true
  
  try {
    const skip = (currentPage.value - 1) * limit.value
    const res = await api.search({
      tags: searchTags.value,
      directories: selectedDirs.value,
      skip: skip,
      limit: limit.value
    })
    
    // 直接替换数据，而非追加
    images.value = res.items
    totalItems.value = res.total
  } catch (error) {
    console.error("搜索失败:", error)
  } finally {
    loading.value = false
  }
}

const changePage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  
  currentPage.value = page
  await loadImages()
  
  // 翻页后将主内容区滚动回顶部
  if (mainContent.value) {
    mainContent.value.scrollTop = 0
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
