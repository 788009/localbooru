<template>
  <div class="relative w-full max-w-3xl">
    <div class="flex flex-wrap items-center gap-2 bg-gray-800 p-2 rounded-lg border border-gray-700">
      <!-- 已选标签 -->
      <span v-for="tag in modelValue" :key="tag" 
            class="px-2 py-1 bg-blue-600 text-sm rounded flex items-center gap-1 cursor-pointer hover:bg-blue-700"
            @click="removeTag(tag)">
        {{ tag }} &times;
      </span>
      
      <!-- 输入框 -->
      <input 
        v-model="query" 
        @input="handleInput"
        @keydown.enter.prevent="addTag(query)"
        @keydown.down.prevent="nav(1)"
        @keydown.up.prevent="nav(-1)"
        type="text" 
        placeholder="搜索标签 (支持 - 排除)" 
        class="flex-1 bg-transparent outline-none text-gray-100 min-w-[150px]"
      />
    </div>

    <!-- 自动补全下拉菜单 -->
    <div v-if="suggestions.length > 0" class="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded shadow-lg max-h-60 overflow-y-auto">
      <div v-for="(item, index) in suggestions" :key="item.tag"
           @click="addTag(item.tag)"
           :class="['px-4 py-2 cursor-pointer flex justify-between', selectedIndex === index ? 'bg-blue-600' : 'hover:bg-gray-700']">
        <span :class="item.tag.startsWith('-') ? 'text-red-400' : 'text-green-400'">{{ item.tag }}</span>
        <span class="text-gray-400 text-sm">{{ item.count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../api'

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue', 'search'])

const query = ref('')
const suggestions = ref([])
const selectedIndex = ref(-1)

let debounceTimer = null

const handleInput = () => {
  clearTimeout(debounceTimer)
  selectedIndex.value = -1
  if (!query.value) {
    suggestions.value = []
    return
  }
  debounceTimer = setTimeout(async () => {
    suggestions.value = await api.autocomplete(query.value)
  }, 200)
}

const nav = (dir) => {
  if (suggestions.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + dir + suggestions.value.length) % suggestions.value.length
  query.value = suggestions.value[selectedIndex.value].tag
}

const addTag = (tag) => {
  if (!tag) return
  const newTags = [...props.modelValue]
  if (!newTags.includes(tag)) {
    newTags.push(tag)
    emit('update:modelValue', newTags)
  }
  query.value = ''
  suggestions.value = []
  emit('search')
}

const removeTag = (tag) => {
  const newTags = props.modelValue.filter(t => t !== tag)
  emit('update:modelValue', newTags)
  emit('search')
}
</script>
