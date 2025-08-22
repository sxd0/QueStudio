import { createRouter, createWebHistory } from "vue-router";
import Home from "../pages/Home.vue";
import TopicDetail from "../pages/TopicDetail.vue";

const routes = [
  { path: "/", name: "home", component: Home },
  { path: "/topic/:id", name: "topic", component: TopicDetail, props: true },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
