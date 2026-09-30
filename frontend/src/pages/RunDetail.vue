<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">写入时钉住的标称与订货米，不随后续标称修改重托。</p>
      <ul class="item-list">
        <li><span>盒型</span><span class="meta">{{ run.box_name }}</span></li>
        <li><span>纸卷</span><span class="meta">{{ run.result?.paper_name ?? '—' }}</span></li>
        <li><span>用纸面积</span><span class="meta">{{ run.result?.paper_m2 ?? '—' }} m²</span></li>
        <li><span>卷宽</span><span class="meta">{{ run.result?.roll_width ?? '—' }} m</span></li>
        <li><span>下料长</span><span class="meta">{{ run.result?.sheet_len ?? '—' }} m</span></li>
        <li><span>标称卷长</span><span class="meta">{{ run.result?.stock_len ?? '—' }} m</span></li>
        <li><span>订货米</span><span class="meta">{{ run.result?.order_m ?? '—' }} m</span></li>
        <li><span>折边系数</span><span class="meta">{{ run.overlap }}</span></li>
        <li><span>写入时间</span><span class="meta">{{ run.created_at }}</span></li>
      </ul>
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>
