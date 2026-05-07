<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useConfigStore } from './stores/config'

const configStore = useConfigStore()

onMounted(() => {
  configStore.initDarkMode()
})
</script>
