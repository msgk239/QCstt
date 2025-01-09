import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import EditorView from '@/views/EditorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      // 编辑页面使用独立路由，不继承主布局
      path: '/editor/:id',
      name: 'editor',
      component: EditorView
    }
  ]
})

export default router 