<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const input = ref('')
const msg = ref('')
const err = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  input.value = String(s.value.default_fullness)
})
async function save() {
  msg.value = ''; err.value = ''
  const v = Number(input.value)
  if (!(v > 0)) { err.value = '褶倍必须为正数'; return }
  try {
    const r = await putJSON('/api/settings/default_fullness', { value: v })
    s.value = { ...s.value, default_fullness: r.default_fullness }
    msg.value = '已保存'
  } catch (e) { err.value = '保存失败：褶倍必须为正数' }
}
</script>
<template><div class="page"><h1>设置</h1>
<p>默认褶倍 {{ s.default_fullness }}</p>
<input v-model="input" type="number" step="0.1" min="0.1" />
<button @click="save">保存</button>
<p v-if="msg">{{ msg }}</p>
<p v-if="err" class="bad">{{ err }}</p>
</div></template>
