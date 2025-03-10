import { createRouter, createWebHistory } from 'vue-router'
import { useFileStore } from '@/stores/fileStore'
// 改为动态导入
const HomeView = () => import('@/views/HomeView.vue')
const EditorView = () => import('@/views/EditorView.vue')
const TrashView = () => import('@/views/TrashView.vue')
const HotwordsView = () => import('@/views/HotwordsView.vue')  // 添加热词管理页面

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: '文件列表'
      }
    },
    {
      path: '/editor/:id',
      name: 'editor',
      component: EditorView,
      meta: {
        title: '编辑文件'
      },
      // 添加路由守卫，确保文件存在
      beforeEnter: async (to) => {
        const fileStore = useFileStore()
        const fileId = to.params.id
        
        // 如果 store 中没有当前文件，尝试获取
        if (!fileStore.currentFile || fileStore.currentFile.file_id !== fileId) {
          try {
            await fileStore.fetchFileList()
            const file = fileStore.fileList.find(f => f.file_id === fileId)
            if (!file) {
              return {
                path: '/',
                query: { error: 'file_not_found' }
              }
            }
            fileStore.currentFile = file
          } catch (error) {
            console.error('Failed to fetch file:', error)
            return {
              path: '/',
              query: { error: 'load_failed' }
            }
          }
        }
      }
    },
    {
      path: '/trash',
      name: 'trash',
      component: TrashView,
      meta: {
        title: '回收站'
      }
    },
    {
      path: '/hotwords',
      name: 'hotwords',
      component: HotwordsView,
      meta: {
        title: '热词管理'
      }
    }
  ]
})

// 全局路由守卫
router.beforeEach((to, from) => {
  const fileStore = useFileStore()
  
  // 如果不是编辑页面，清空当前文件
  if (to.name !== 'editor') {
    fileStore.currentFile = null
  }
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 潜催语音转文字系统` : '潜催语音转文字系统'
})

export default router 