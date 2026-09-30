<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const items = ref([])
const err = ref('')
const editId = ref(null)
const form = ref({ roll_width: 0, stock_len: 0 })

async function load() {
  items.value = (await getJSON('/api/papers')).items
}

onMounted(async () => {
  try {
    await load()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function startEdit(p) {
  err.value = ''
  editId.value = p.id
  form.value = { roll_width: p.roll_width, stock_len: p.stock_len }
}

async function save(p) {
  err.value = ''
  try {
    await putJSON(`/api/papers/${p.id}`, {
      roll_width: Number(form.value.roll_width),
      stock_len: Number(form.value.stock_len),
    })
    editId.value = null
    await load()
  } catch (e) {
    err.value = String(e.message || e)
  }
}
</script>

<template>
  <div class="page">
    <h1>包装纸</h1>
    <p class="lede">此处只改标称卷宽与标称卷长；已写入的用纸档钉住旧值，新单按新标称托底。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div class="paper-grid">
      <div v-for="p in items" :key="p.id" class="paper-tile">
        <strong>{{ p.name }}</strong>
        <template v-if="editId === p.id">
          <label class="field">
            卷宽 (m)
            <input v-model.number="form.roll_width" type="number" min="0" step="0.01" />
          </label>
          <label class="field">
            标称卷长 (m)
            <input v-model.number="form.stock_len" type="number" min="0" step="0.1" />
          </label>
          <div class="row">
            <button @click="save(p)">保存</button>
            <button class="ghost" @click="editId = null">取消</button>
          </div>
        </template>
        <template v-else>
          <span class="meta">卷宽 {{ p.roll_width }} m</span>
          <span class="meta">标称卷长 {{ p.stock_len ?? '—' }} m</span>
          <div class="row" style="margin-top: 0.6rem; margin-bottom: 0">
            <button class="ghost" @click="startEdit(p)">改标称</button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paper-tile .meta {
  display: block;
}
.field {
  display: block;
  margin: 0.4rem 0;
  font-size: 0.88rem;
  color: var(--ink-soft);
}
.field input {
  display: block;
  width: 100%;
  margin-top: 0.2rem;
  padding: 0.4rem 0.5rem;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.72);
  font: inherit;
  color: var(--ink);
}
</style>
