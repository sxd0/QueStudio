<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const hot = ref([]);
const newest = ref([]);
const leaders = ref([]);
const q = ref("");
const searchResults = ref(null);
const loading = ref(false);

const hotPage = ref({ next: null, prev: null });
const newPage = ref({ next: null, prev: null });
const searchPage = ref({ next: null, prev: null });

async function safeGet(url, config) {
  try { return await api.get(url, config); } catch { return { data: [] }; }
}

async function loadHot(url = "/topics/hot/") {
  const r = await safeGet(url);
  hot.value = r.data.results || r.data || [];
  hotPage.value = { next: r.data?.next ?? null, prev: r.data?.previous ?? null };
}

async function loadNew(url = "/topics/new/") {
  const r = await safeGet(url);
  newest.value = r.data.results || r.data || [];
  newPage.value = { next: r.data?.next ?? null, prev: r.data?.previous ?? null };
}

async function doSearch(url = null) {
  loading.value = true;
  try {
    const r = await safeGet(url || "/topics/", { params: { q: q.value, ordering: "-posts_count" } });
    searchResults.value = r.data.results || r.data || [];
    searchPage.value = { next: r.data?.next ?? null, prev: r.data?.previous ?? null };
  } finally {
    loading.value = false;
  }
}

async function loadWidgets() {
  const l = await safeGet("/accounts/leaderboard/");
  leaders.value = l.data || [];
  await loadHot();
  await loadNew();
}

onMounted(loadWidgets);
</script>

<template>
  <div>
    <div class="card">
      <h2>Поиск по темам</h2>
      <input v-model="q" placeholder="что ищем?" @keyup.enter="doSearch()" />
      <button @click="doSearch()">Поиск</button>
    </div>

    <div v-if="searchResults" class="card">
      <h3>Результаты поиска</h3>
      <div v-if="!searchResults.length">Ничего не найдено</div>
      <ul>
        <li v-for="t in searchResults" :key="t.id">
          <router-link :to="`/topic/${t.id}`">{{ t.title }}</router-link>
          <small> — {{ t.category_name }} · постов: {{ t.posts_count ?? 0 }} · рейтинг: {{ t.rating }}</small>
        </li>
      </ul>
      <div>
        <button :disabled="!searchPage.prev" @click="doSearch(searchPage.prev)">Назад</button>
        <button :disabled="!searchPage.next" @click="doSearch(searchPage.next)">Вперёд</button>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <h2>🔥 Горячее (7 дней)</h2>
        <ul>
          <li v-for="t in hot" :key="t.id">
            <router-link :to="`/topic/${t.id}`">{{ t.title }}</router-link>
            <small> · постов: {{ t.posts_count ?? 0 }} · посл. активность: {{ t.last_activity_at || t.last_activity }}</small>
          </li>
        </ul>
        <div>
          <button :disabled="!hotPage.prev" @click="loadHot(hotPage.prev)">Назад</button>
          <button :disabled="!hotPage.next" @click="loadHot(hotPage.next)">Вперёд</button>
        </div>
      </div>

      <div class="card">
        <h2>🆕 Новое</h2>
        <ul>
          <li v-for="t in newest" :key="t.id">
            <router-link :to="`/topic/${t.id}`">{{ t.title }}</router-link>
            <small> · {{ t.created_at }}</small>
          </li>
        </ul>
        <div>
          <button :disabled="!newPage.prev" @click="loadNew(newPage.prev)">Назад</button>
          <button :disabled="!newPage.next" @click="loadNew(newPage.next)">Вперёд</button>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>👑 Топ пользователи</h2>
      <div v-if="!leaders.length"><i>Войдите, чтобы увидеть лидеров или сделайте эндпоинт публичным</i></div>
      <ol v-else>
        <li v-for="u in leaders" :key="u.username">
          {{ u.display_name || u.username }} ({{ u.username }}) — рейтинг: {{ u.total_rating }},
          тем: {{ u.topics }}, постов: {{ u.posts }}
        </li>
      </ol>
    </div>
  </div>
</template>

<style>
.card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
.grid { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
</style>
