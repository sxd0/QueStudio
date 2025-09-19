<script setup>
import { ref } from "vue";
import api, { setTokens } from "../api";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const err = ref("");

async function login() {
  err.value = "";
  try {
    const r = await api.post("/accounts/login/", { username: username.value, password: password.value });
    const access = r.data.access || r.data.access_token;
    const refresh = r.data.refresh || r.data.refresh_token;
    setTokens({ access, refresh });
    router.push("/");
  } catch (e) {
    err.value = "Неверные учётные данные или сервер недоступен";
  }
}
</script>

<template>
  <div class="card" style="max-width:400px;margin:40px auto;">
    <h2>Вход</h2>
    <input v-model="username" placeholder="Логин" />
    <input v-model="password" type="password" placeholder="Пароль" />
    <button @click="login">Войти</button>
    <p v-if="err" style="color:#b00">{{ err }}</p>
  </div>
</template>

<style>
.card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
input { display:block; width:100%; margin:8px 0; padding:8px; }
button { padding:8px 12px; }
</style>
