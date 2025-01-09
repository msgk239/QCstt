import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: {
        title: '文件列表'
      }
    },
    {
      path: '/trash',
      name: 'trash',
      component: () => import('@/views/TrashView.vue'),
      meta: {
        title: '回收站'
      }
    },
    {
      path: '/editor/:id',
      name: 'editor',
      component: () => import('@/views/EditorView.vue'),
      meta: {
        title: '编辑器'
      },
      beforeEnter: (to, from, next) => {
        console.log('Editor route guard:', to.params)
        next()
      }
    }
  ]
})

// 路由标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title + ' - 潜催语音转文字系统'
  next()
})

export default router 