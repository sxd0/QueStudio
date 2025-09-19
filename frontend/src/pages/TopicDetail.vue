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
const me = ref(null);
const loading = ref(false);
const error = ref("");

async function loadMe() {
  try { const r = await api.get("/accounts/me/"); me.value = r.data; }
  catch { me.value = null; }
}

async function load() {
  loading.value = true; error.value = "";
  try {
    const t = await api.get(`/topics/${id}/`);
    topic.value = t.data;
    const p = await api.get("/posts/", { params: { topic: id }});
    posts.value = p.data.results || p.data || [];
  } catch { error.value = "Не удалось загрузить тему или ответы"; }
  finally { loading.value = false; }
}

function requireAuth(nextPath) {
  if (!me.value) {
    router.push({ name: "login", query: { next: nextPath || route.fullPath } });
    return false;
  }
  return true;
}

async function voteTopic(val) {
  if (!requireAuth(`/topic/${id}`)) return;
  try { await api.post(`/topics/${id}/vote/`, { value: val }); await load(); } catch {}
}

async function addPost() {
  if (!requireAuth(`/topic/${id}`)) return;
  const body = newPost.value.trim();
  if (!body) return;
  try { await api.post("/posts/", { topic: id, body }); newPost.value = ""; await load(); } catch {}
}

async function votePost(pid, val) {
  if (!requireAuth(`/topic/${id}`)) return;
  try { await api.post(`/posts/${pid}/vote/`, { value: val }); await load(); } catch {}
}

async function addComment(pid) {
  if (!requireAuth(`/topic/${id}`)) return;
  const body = (newComment.value[pid] || "").trim();
  if (!body) return;
  try { await api.post("/comments/", { post: pid, body }); newComment.value[pid] = ""; await load(); } catch {}
}

async function editPost(p) {
  if (!requireAuth(`/topic/${id}`)) return;
  if (!(me.value?.username && me.value.username === p.author_name)) return;
  const text = window.prompt("Новый текст ответа:", p.body);
  if (!text || text.trim() === p.body) return;
  try { await api.patch(`/posts/${p.id}/`, { body: text.trim() }); await load(); } catch {}
}

async function deletePost(p) {
  if (!requireAuth(`/topic/${id}`)) return;
  if (!(me.value?.username && me.value.username === p.author_name)) return;
  if (!window.confirm("Точно удалить ответ?")) return;
  try { await api.delete(`/posts/${p.id}/`); await load(); } catch {}
}

async function editTopic() {
  if (!requireAuth(`/topic/${id}`)) return;
  if (!topic.value?.is_editable) return;
  const title = window.prompt("Новый заголовок:", topic.value.title);
  if (!title || title.trim() === topic.value.title) return;
  const body = window.prompt("Новый текст темы:", topic.value.body || "");
  try { await api.patch(`/topics/${id}/`, { title: title.trim(), body: (body||"").trim() }); await load(); } catch {}
}

async function deleteTopic() {
  if (!requireAuth(`/topic/${id}`)) return;
  if (!topic.value?.is_editable) return;
  if (!window.confirm("Точно удалить тему?")) return;
  try { await api.delete(`/topics/${id}/`); router.push("/"); } catch {}
}

onMounted(async () => {
  await loadMe();
  await load();
});
</script>

<template>
  <div v-if="loading" class="card">Загрузка...</div>
  <div v-else-if="error" class="card" style="color:#b00">{{ error }}</div>
  <div v-else-if="!topic" class="card">Тема не найдена</div>
  <div v-else>
    <div class="card">
      <h2>{{ topic.title }}</h2>
      <p><i>{{ topic.category_name }}</i> · рейтинг: {{ topic.rating }}</p>
      <p>{{ topic.body }}</p>
      <div>
        <button @click="voteTopic(1)">👍</button>
        <button @click="voteTopic(-1)">👎</button>
      </div>
      <div v-if="topic.is_editable" style="margin-top:6px">
        <button @click="editTopic">Редактировать тему</button>
        <button @click="deleteTopic">Удалить тему</button>
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

        <div v-if="me && me.username === p.author_name" style="margin-top:6px">
          <button @click="editPost(p)">Редактировать</button>
          <button @click="deletePost(p)">Удалить</button>
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

<style>
.card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
textarea, input, button { margin-top: 6px; }
</style>
