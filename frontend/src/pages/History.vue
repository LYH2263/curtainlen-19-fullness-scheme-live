<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([]); const detail = ref(null)
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
async function open(id){ detail.value = await getJSON(`/api/runs/${id}`) }
</script>
<template><div class="page"><h1>记录</h1>
<ul><li v-for="r in items" :key="r.id">
  <a href="#" @click.prevent="open(r.id)">#{{ r.id }}</a>
  {{ r.window_name }} · 褶倍 {{ r.result?.fullness ?? '—' }} · {{ r.result?.meters }}m
</li></ul>
<div v-if="detail" class="run-detail">
  <h2>#{{ detail.id }} {{ detail.window_name }}</h2>
  <p>褶倍 {{ detail.result.fullness ?? '—' }} · 成品宽 {{ detail.result.finished_width }} m · {{ detail.result.panels }} 幅 × {{ detail.result.cut_height }} m = {{ detail.result.meters }} m</p>
  <p>{{ detail.created_at }}</p>
</div>
</div></template>
