<script setup>
import { ref, onMounted } from "vue";
import api from "../api";

const hot = ref([]);
const newest = ref([]);
const leaders = ref([]);
const q = ref("");
const searchResults = ref(null);
const loading = ref(false);

async function loadWidgets() {
  const [h, n, l] = await Promise.all([
    api.get("/topics/hot/"),
    api.get("/topics/new/"),
    api.get("/accounts/leaderboard/"),
  ]);
  hot.value = h.data.results || h.data;
  newest.value = n.data.results || n.data;
  leaders.value = l.data;
}

async function doSearch() {
  loading.value = true;
  try {
    const r = await api.get("/topics/", { params: { q: q.value, ordering: "-posts_count" } });
    searchResults.value = r.data.results || r.data;
  } finally {
    loading.value = false;
  }
}

onMounted(loadWidgets);
</script>

<template>
  <div>
    <div class="card">
      <h2>Поиск по темам</h2>
      <input v-model="q" placeholder="что ищем?" @keyup.enter="doSearch" />
      <button @click="doSearch">Поиск</button>
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
    </div>

    <div class="grid">
      <div class="card">
        <h2>🔥 Горячее (7 дней)</h2>
        <ul>
          <li v-for="t in hot" :key="t.id">
            <router-link :to="`/topic/${t.id}`">{{ t.title }}</router-link>
            <small> · постов: {{ t.posts_count ?? 0 }} · посл. активность: {{ t.last_activity }}</small>
          </li>
        </ul>
      </div>

      <div class="card">
        <h2>🆕 Новое</h2>
        <ul>
          <li v-for="t in newest" :key="t.id">
            <router-link :to="`/topic/${t.id}`">{{ t.title }}</router-link>
            <small> · {{ t.created_at }}</small>
          </li>
        </ul>
      </div>
    </div>

    <div class="card">
      <h2>👑 Топ пользователи</h2>
      <ol>
        <li v-for="u in leaders" :key="u.username">
          {{ u.display_name }} ({{ u.username }}) — рейтинг: {{ u.total_rating }},
          тем: {{ u.topics }}, постов: {{ u.posts }}
        </li>
      </ol>
    </div>
  </div>
</template>
