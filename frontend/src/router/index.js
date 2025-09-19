import { createRouter, createWebHistory } from "vue-router";
import Home from "../pages/Home.vue";
import TopicDetail from "../pages/TopicDetail.vue";
import Login from "../pages/Login.vue";

const routes = [
  { path: "/", name: "home", component: Home },
  { path: "/topic/:id", name: "topic", component: TopicDetail, props: true },
  { path: "/login", name: "login", component: Login },
  { path: "/:pathMatch(.*)*", component: { template: "<div class='card'>404</div>" } },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
