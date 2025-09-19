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
const err = ref("");

async function loadMe() {
  try { const r = await api.get("/accounts/me/"); me.value = r.data; }
  catch { me.value = null; }
}

async function load() {
  loading.value = true;
  err.value = "";
  try {
    const t = await api.get(`/topics/${id}/`);
    topic.value = t.data;
    const p = await api.get("/posts/", { params: { topic: id }});
    posts.value = p.data.results || p.data;
  } catch (e) {
    err.value = "Не удалось загрузить тему или ответы";
  } finally { loading.value = false; }
}

function ensureAuth() {
  if (!me.value) {
    alert("Нужно войти, чтобы выполнить действие");
    router.push({ name: "login", query: { next: `/topic/${id}` } });
    return false;
  }
  return true;
}

async function voteTopic(val) {
  if (!ensureAuth()) return;
  await api.post(`/topics/${id}/vote/`, { value: val }).catch(()=>{});
  await load();
}

async function addPost() {
  if (!ensureAuth()) return;
  if (!newPost.value.trim()) return;
  await api.post("/posts/", { topic: id, body: newPost.value }).catch(()=>{});
  newPost.value = "";
  await load();
}

async function votePost(pid, val) {
  if (!ensureAuth()) return;
  await api.post(`/posts/${pid}/vote/`, { value: val }).catch(()=>{});
  await load();
}

async function addComment(pid) {
  if (!ensureAuth()) return;
  const body = (newComment.value[pid] || "").trim();
  if (!body) return;
  await api.post("/comments/", { post: pid, body }).catch(()=>{});
  newComment.value[pid] = "";
  await load();
}

async function editPost(p) {
  if (!ensureAuth()) return;
  const text = window.prompt("Новый текст ответа:", p.body);
  if (!text || text.trim() === p.body) return;
  await api.patch(`/posts/${p.id}/`, { body: text.trim() }).catch(()=>{});
  await load();
}

async function deletePost(p) {
  if (!ensureAuth()) return;
  if (!window.confirm("Точно удалить ответ?")) return;
  await api.delete(`/posts/${p.id}/`).catch(()=>{});
  await load();
}

async function editTopic() {
  if (!ensureAuth()) return;
  const title = window.prompt("Новый заголовок:", topic.value.title);
  if (!title || title.trim() === topic.value.title) return;
  const body = window.prompt("Новый текст темы:", topic.value.body || "");
  await api.patch(`/topics/${id}/`, { title: title.trim(), body: (body || "").trim() }).catch(()=>{});
  await load();
}

async function deleteTopic() {
  if (!ensureAuth()) return;
  if (!window.confirm("Точно удалить тему?")) return;
  await api.delete(`/topics/${id}/`).catch(()=>{});
  router.push(`/`);
}

onMounted(async () => {
  await loadMe();
  await load();
});
</script>

<template>
  <div v-if="loading" class="card">Загрузка...</div>
  <div v-else-if="err" class="card" style="color:#b00">{{ err }}</div>
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

        <div v-if="p.is_editable" style="margin-top:6px">
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
