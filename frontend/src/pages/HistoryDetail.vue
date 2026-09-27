<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const r = ref(null)
onMounted(async () => { r.value = await getJSON(`/api/runs/${props.id}`) })
</script>
<template><div class="page" v-if="r"><h1>记录 #{{ r.id }}</h1>
<p>{{ r.window_name }} · {{ r.fabric_name }} · {{ r.created_at }}</p>
<p>褶倍 {{ r.result.fullness ?? '未记录' }} · 成品宽 {{ r.result.finished_width }} m · {{ r.result.panels }} 幅 × {{ r.result.cut_height }} m = {{ r.result.meters }} m</p>
</div></template>
