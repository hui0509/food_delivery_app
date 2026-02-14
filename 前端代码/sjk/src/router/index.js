import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '@/views/auth/Login'
import UserProfile from '@/views/user/Profile'
import AdminDashboard from '@/views/admin/Dashboard'

Vue.use(VueRouter)

export default new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            redirect: '/login'
        },
        {
            path: '/login',
            component: Login,
            meta: {
                title: "登录"
            },
        },
        {
            path: '/user',
            component: UserProfile,
            meta: {
                title: "用户界面"
            }
        },
        {
            path: '/manage',
            component: AdminDashboard,
            meta: {
                title: "后台管理界面"
            }
        },
        // 商家管理界面
        {
            path: '/store',
            component: () => import('@/views/store/StoreManage.vue'),
            meta: {
                title: "商家管理"
            }
        },
        // 测试路由（可以保留）
        {
            path: '/test-completed-orders',
            component: () => import('@/views/admin/orders/BeSended.vue'),
            meta: {
                title: "测试-已完成订单"
            }
        },
        // 店铺列表页面
        {
            path: '/shops',
            component: () => import('@/views/public/ShopList.vue'),
            meta: {
                title: "店铺列表"
            }
        },
        // 店铺详情页面
        {
            path: '/shop/:shopId',
            component: () => import('@/views/public/ShopDetail.vue'),
            meta: {
                title: "店铺详情"
            }
        },
        // 用户未发货订单
        {
            path: '/user/unsend',
            component: () => import('@/views/user/orders/UserUnsend.vue'),
            meta: {
                title: '未发货订单'
            }
        },
        // 购物车页面
        {
            path: '/cart',
            name: 'Cart',
            component: () => import('@/views/public/Cart.vue'),
            meta: {
                title: '购物车',
                requiresAuth: true
            }
        },
        // 404 页面处理
        {
            path: '*',
            redirect: '/login'
        }
    ]
})