<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const val = ref(null); const err = ref(''); const saved = ref(false)
onMounted(async () => { val.value = (await getJSON('/api/settings')).default_fullness })
async function save() {
  err.value = ''; saved.value = false
  try {
    const s = await putJSON('/api/settings', { default_fullness: Number(val.value) })
    val.value = s.default_fullness; saved.value = true
  } catch (e) { err.value = '保存失败：默认褶倍须为正数' }
}
</script>
<template>
  <div class="fullness-editor">
    <p>当前默认褶倍：<strong>{{ val }}</strong></p>
    <label>默认褶倍 <input type="number" step="0.1" min="0.1" v-model.number="val"></label>
    <button @click="save">保存</button>
    <span v-if="saved">已保存</span>
    <p v-if="err" class="bad">{{ err }}</p>
  </div>
</template>
