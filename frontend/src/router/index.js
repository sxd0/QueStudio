import { createRouter, createWebHistory } from "vue-router";
import Home from "../pages/Home.vue";
import TopicDetail from "../pages/TopicDetail.vue";
import Login from "../pages/Login.vue";

const routes = [
  { path: "/", name: "home", component: Home },
  { path: "/topic/:id", name: "topic", component: TopicDetail, props: true },
  { path: "/login", name: "login", component: Login },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
