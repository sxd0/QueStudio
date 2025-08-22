<template>
  <div class="container">
    <header>
      <h1>QueStudio</h1>
      <nav>
        <router-link to="/">Главная</router-link>
      </nav>
    </header>
    <router-view />
  </div>
</template>

<style>
.container { max-width: 960px; margin: 0 auto; padding: 1rem; }
header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; }
nav a { margin-right: 1rem; }
.card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
.grid { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
input, textarea, select, button { padding: 8px; margin: 4px 0; }
</style>
