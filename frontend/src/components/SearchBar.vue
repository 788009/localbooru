<template>
  <div class="relative w-full max-w-3xl">
    <div class="flex flex-wrap items-center gap-2 bg-gray-800 p-2 rounded-lg border border-gray-700">
      <span
        v-for="tag in modelValue"
        :key="tag"
        :class="[
          'px-2 py-1 text-sm rounded flex items-center gap-1 cursor-pointer',
          tag.startsWith('-') ? 'bg-red-700 hover:bg-red-800' : 'bg-blue-600 hover:bg-blue-700'
        ]"
        @click="removeTag(tag)"
      >
        {{ tag }} &times;
      </span>

      <input
        v-model="query"
        @input="handleInput"
        @keydown.enter.prevent="submitInput"
        @keydown.down.prevent="nav(1)"
        @keydown.up.prevent="nav(-1)"
        @keydown.esc="suggestions = []"
        type="text"
        placeholder="搜索标签 (多个标签用空格分隔，支持 - 排除)"
        class="flex-1 bg-transparent outline-none text-gray-100 min-w-[150px]"
      />
    </div>

    <div
      v-if="suggestions.length > 0"
      class="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded shadow-lg max-h-60 overflow-y-auto"
    >
      <div
        v-for="(item, index) in suggestions"
        :key="item.tag"
        @click="selectSuggestion(item.tag)"
        :class="[
          'px-4 py-2 cursor-pointer flex justify-between',
          selectedIndex === index ? 'bg-blue-600' : 'hover:bg-gray-700'
        ]"
      >
        <span :class="item.tag.startsWith('-') ? 'text-red-400' : 'text-green-400'">{{ item.tag }}</span>
        <span class="text-gray-400 text-sm">{{ item.count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue', 'search'])

const query = ref('')
const suggestions = ref([])
const selectedIndex = ref(-1)

let debounceTimer = null

const getCurrentToken = (text) => {
  if (!text || /\s$/.test(text)) {
    return ''
  }
  const parts = text.trim().split(/\s+/)
  return parts[parts.length - 1] || ''
}

const replaceCurrentToken = (text, replacement) => {
  const match = text.match(/^(.*\s)?(\S*)$/)
  const prefix = match && match[1] ? match[1] : ''
  return prefix + replacement
}

const handleInput = () => {
  clearTimeout(debounceTimer)
  selectedIndex.value = -1

  const token = getCurrentToken(query.value)
  if (!token || token === '-') {
    suggestions.value = []
    return
  }

  debounceTimer = setTimeout(async () => {
    const res = await api.autocomplete(token)
    if (getCurrentToken(query.value) === token) {
      suggestions.value = res
    }
  }, 200)
}

const nav = (dir) => {
  if (suggestions.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + dir + suggestions.value.length) % suggestions.value.length
  const chosenTag = suggestions.value[selectedIndex.value].tag
  query.value = replaceCurrentToken(query.value, chosenTag)
}

const commitTokens = (rawText) => {
  const tokens = rawText
    .trim()
    .split(/\s+/)
    .filter((t) => t && t !== '-')

  if (tokens.length > 0) {
    const newTags = [...props.modelValue]
    for (const t of tokens) {
      if (!newTags.includes(t)) {
        newTags.push(t)
      }
    }
    emit('update:modelValue', newTags)
  }

  query.value = ''
  suggestions.value = []
  selectedIndex.value = -1
  emit('search')
}

const submitInput = () => {
  commitTokens(query.value)
}

const selectSuggestion = (tag) => {
  const fullText = replaceCurrentToken(query.value, tag)
  commitTokens(fullText)
}

const removeTag = (tag) => {
  const newTags = props.modelValue.filter((t) => t !== tag)
  emit('update:modelValue', newTags)
  emit('search')
}
</script>
