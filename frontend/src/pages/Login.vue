<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { login } from "../api";
import api from "../api";

const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const error = ref("");

async function doLogin() {
  error.value = "";
  try {
    await login(username.value, password.value);
    try { await api.get("/accounts/me/"); } catch {}
    router.push(route.query.next || "/");
  } catch (e) {
    error.value = "Неверный логин или пароль";
  }
}
</script>

<template>
  <div class="card" style="max-width:380px;margin:40px auto;">
    <h2>Вход</h2>
    <input v-model="username" placeholder="Логин" @keyup.enter="doLogin" />
    <input v-model="password" type="password" placeholder="Пароль" @keyup.enter="doLogin" />
    <button @click="doLogin">Войти</button>
    <p v-if="error" style="color:#b00">{{ error }}</p>
  </div>
</template>

<style>
.card { border:1px solid #ddd; border-radius:8px; padding:12px; }
input { display:block; width:100%; padding:8px; margin:8px 0; }
button { padding:8px 12px; }
</style>
