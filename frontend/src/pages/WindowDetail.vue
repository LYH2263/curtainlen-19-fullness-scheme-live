<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const props = defineProps({ id: String })
const w = ref(null)
const input = ref('')
const err = ref('')
async function load() {
  w.value = await getJSON(`/api/windows/${props.id}`)
  input.value = w.value.fullness ?? ''
}
onMounted(load)
async function save() {
  err.value = ''
  const v = input.value === '' || input.value === null ? null : Number(input.value)
  if (v !== null && !(v > 0)) { err.value = '褶倍必须为正数'; return }
  try { w.value = await putJSON(`/api/windows/${props.id}/fullness`, { fullness: v }) }
  catch (e) { err.value = '保存失败：褶倍必须为正数' }
}
async function resetToDefault() { input.value = ''; await save() }
</script>
<template><div class="page" v-if="w"><h1>{{ w.name }}</h1>
<p v-if="w.data_quality==='dirty'" class="bad">{{ w.note }}</p>
<p>宽 {{ w.width }} 高 {{ w.height }}</p>
<p>生效褶倍 {{ w.effective_fullness }}（{{ w.fullness_source === 'window' ? '本窗自定义' : '默认方案' }}）</p>
<input v-model="input" type="number" step="0.1" min="0.1" placeholder="留空跟随默认" />
<button @click="save">保存</button><button @click="resetToDefault">恢复默认</button>
<p v-if="err" class="bad">{{ err }}</p>
</div></template>
