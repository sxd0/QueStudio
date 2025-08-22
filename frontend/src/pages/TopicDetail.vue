<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();
const id = Number(route.params.id);

const topic = ref(null);
const posts = ref([]);
const newPost = ref("");
const newComment = ref({});
const loading = ref(false);
const me = ref(null);

async function loadMe() {
  try { const r = await api.get("/accounts/me/"); me.value = r.data; } catch { me.value = null; }
}

async function load() {
  loading.value = true;
  try {
    const t = await api.get(`/topics/${id}/`);
    topic.value = t.data;
    const p = await api.get("/posts/", { params: { topic: id }});
    posts.value = p.data.results || p.data;
  } finally { loading.value = false; }
}

async function voteTopic(val) {
  await api.post(`/topics/${id}/vote/`, { value: val });
  await load();
}

async function addPost() {
  if (!newPost.value.trim()) return;
  await api.post("/posts/", { topic: id, body: newPost.value });
  newPost.value = "";
  await load();
  router.push(`/topic/${id}`);
}

async function votePost(pid, val) {
  await api.post(`/posts/${pid}/vote/`, { value: val });
  await load();
}

async function addComment(pid) {
  const body = (newComment.value[pid] || "").trim();
  if (!body) return;
  await api.post("/comments/", { post: pid, body });
  newComment.value[pid] = "";
  await load();
}

onMounted(async () => {
  await loadMe();
  await load();
});
</script>

<template>
  <div v-if="!topic" class="card">Загрузка...</div>
  <div v-else>
    <div class="card">
      <h2>{{ topic.title }}</h2>
      <p><i>{{ topic.category_name }}</i> · рейтинг: {{ topic.rating }}</p>
      <p>{{ topic.body }}</p>
      <div>
        <button @click="voteTopic(1)">👍</button>
        <button @click="voteTopic(-1)">👎</button>
      </div>
    </div>

    <div class="card">
      <h3>Ответы</h3>
      <div v-for="p in posts" :key="p.id" class="card">
        <p>{{ p.body }}</p>
        <small>Автор: {{ p.author_name }} · рейтинг: {{ p.rating }}</small>
        <div>
          <button @click="votePost(p.id, 1)">👍</button>
          <button @click="votePost(p.id, -1)">👎</button>
        </div>

        <div class="card">
          <h4>Добавить комментарий</h4>
          <input v-model="newComment[p.id]" placeholder="Комментарий..." />
          <button @click="addComment(p.id)">Отправить</button>
        </div>
      </div>

      <div class="card">
        <h4>Добавить ответ</h4>
        <textarea v-model="newPost" placeholder="Текст ответа..."></textarea>
        <button @click="addPost">Ответить</button>
      </div>
    </div>
  </div>
</template>
