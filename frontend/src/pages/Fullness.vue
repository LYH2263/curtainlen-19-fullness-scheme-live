<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const def = ref(null)
const input = ref('')
const msg = ref('')
const err = ref('')
onMounted(async () => {
  const s = await getJSON('/api/settings')
  def.value = s.default_fullness
  input.value = String(s.default_fullness)
})
async function save() {
  msg.value = ''; err.value = ''
  const v = Number(input.value)
  if (!(v > 0)) { err.value = '褶倍必须为正数'; return }
  try {
    const r = await putJSON('/api/settings/default_fullness', { value: v })
    def.value = r.default_fullness
    msg.value = '已保存，算料台新试算立即按此褶倍计算'
  } catch (e) { err.value = '保存失败：褶倍必须为正数' }
}
</script>
<template><div class="page"><h1>褶倍方案</h1>
<p>成品宽 = 窗宽 × 褶倍；幅数 = ceil(成品宽 / 门幅)。</p>
<p>当前默认褶倍：<b>{{ def }}</b>（未单独设置褶倍的窗户按此计算）</p>
<input v-model="input" type="number" step="0.1" min="0.1" />
<button @click="save">保存</button>
<p v-if="msg">{{ msg }}</p>
<p v-if="err" class="bad">{{ err }}</p>
</div></template>
