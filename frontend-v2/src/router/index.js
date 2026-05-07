import { createRouter, createWebHashHistory } from "vue-router"
import DashboardLayout from "@/layouts/DashboardLayout.vue"
import HomeView from "@/views/HomeView.vue"
import HotView from "@/views/HotView.vue"
import DataView from "@/views/DataView.vue"
import SettingsView from "@/views/SettingsView.vue"

const routes = [
    {
        path: "/",
        component: DashboardLayout,
        redirect: "/home",
        children: [
            { path: "home", name: "home", component: HomeView, meta: { title: "舆情推演" } },
            { path: "hot", name: "hot", component: HotView, meta: { title: "热榜选题" } },
            { path: "data", name: "data", component: DataView, meta: { title: "数据洞察" } },
            { path: "settings", name: "settings", component: SettingsView, meta: { title: "设置" } },
        ],
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router
