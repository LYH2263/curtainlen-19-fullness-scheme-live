<script setup>
import FullnessEditor from '../components/FullnessEditor.vue'
</script>
<template><div class="page"><h1>褶倍方案</h1>
<p>成品宽 = 窗宽 × 褶倍；幅数 = ceil(成品宽 / 门幅)。</p>
<p>窗户未单独填写褶倍时，按此处默认褶倍算料；窗户自己写过褶倍的以窗为准。</p>
<FullnessEditor />
</div></template>
