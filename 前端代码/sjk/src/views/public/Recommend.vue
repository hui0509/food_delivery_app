<template>
    <div class="recommend-container">
        <!-- 顶部切换标签 -->
        <div class="tab-switcher">
            <el-tabs v-model="activeTab" @tab-click="handleTabClick">
                <el-tab-pane label="推荐店铺" name="recommend">
                    <i class="el-icon-star-on" slot="label"></i>
                </el-tab-pane>
                <el-tab-pane label="热门评价" name="reviews">
                    <i class="el-icon-chat-dot-round" slot="label"></i>
                </el-tab-pane>
                <el-tab-pane label="我要评价" name="rate">
                    <i class="el-icon-edit" slot="label"></i>
                    <el-badge v-if="pendingOrders.length > 0" :value="pendingOrders.length"
                             type="danger" class="pending-badge"></el-badge>
                </el-tab-pane>
            </el-tabs>
        </div>

        <!-- 推荐店铺内容 -->
        <div v-show="activeTab === 'recommend'" class="recommend-content">
            <!-- 筛选排序 -->
            <div class="filter-bar">
                <el-select v-model="sortBy" placeholder="排序方式" @change="loadRecommendedShops">
                    <el-option label="综合推荐" value="recommend"></el-option>
                    <el-option label="评分最高" value="rating"></el-option>
                    <el-option label="人气最旺" value="popular"></el-option>
                    <el-option label="销量最高" value="sales"></el-option>
                </el-select>

                <div class="filter-tags">
                    <el-tag
                        v-for="tag in filterTags"
                        :key="tag.value"
                        :type="activeFilter === tag.value ? 'primary' : 'info'"
                        @click="toggleFilter(tag.value)"
                        class="filter-tag">
                        {{ tag.label }}
                    </el-tag>
                </div>
            </div>

            <!-- 推荐店铺列表 -->
            <div class="recommend-shops" v-loading="loading.shops">
                <div v-if="recommendedShops.length === 0" class="empty-state">
                    <i class="el-icon-star-off"></i>
                    <p>暂无推荐店铺</p>
                    <p class="hint">先去逛逛店铺，我们会根据您的喜好进行推荐</p>
                </div>

                <div class="shop-grid">
                    <div v-for="shop in recommendedShops" :key="shop.shop_id" class="shop-card">
                        <div class="shop-image" @click="goToShop(shop.shop_id)">
                            <img :src="shop.image_url" :alt="shop.shop_name"
                                 @error="handleImageError(shop, $event)">
                            <div class="shop-tag">
                                <el-tag v-if="shop.avg_rating >= 4.5" type="danger" size="mini">推荐</el-tag>
                                <el-tag v-else-if="shop.avg_rating >= 4.0" type="warning" size="mini">热门</el-tag>
                                <el-tag v-else type="success" size="mini">优选</el-tag>
                            </div>
                        </div>

                        <div class="shop-info">
                            <div class="shop-header" @click="goToShop(shop.shop_id)">
                                <h3 class="shop-name">{{ shop.shop_name }}</h3>
                                <div class="shop-rating">
                                    <el-rate
                                        v-model="shop.avg_rating"
                                        disabled
                                        show-score
                                        text-color="#ff9900"
                                        score-template="{value}">
                                    </el-rate>
                                    <span class="review-count">({{ shop.review_count }}评价)</span>
                                </div>
                            </div>

                            <p class="shop-desc">{{ shop.description || '暂无描述' }}</p>

                            <div class="shop-stats">
                                <div class="stat-item">
                                    <i class="el-icon-shopping-bag-1"></i>
                                    <span>月售 {{ shop.total_sales || 0 }}</span>
                                </div>
                                <div class="stat-item">
                                    <i class="el-icon-thumb"></i>
                                    <span>{{ shop.recommend_reason }}</span>
                                </div>
                            </div>

                            <div class="shop-actions">
                                <el-button
                                    type="primary"
                                    size="small"
                                    icon="el-icon-shopping-cart-2"
                                    @click="viewShopMenu(shop.shop_id)">
                                    查看菜单
                                </el-button>
                                <el-button
                                    type="info"
                                    size="small"
                                    icon="el-icon-chat-line-square"
                                    @click="viewShopReviews(shop.shop_id, shop.shop_name)">
                                    查看评价({{ shop.review_count }})
                                </el-button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 热门评价内容 -->
        <div v-show="activeTab === 'reviews'" class="reviews-content">
            <div class="reviews-list" v-loading="loading.reviews">
                <div v-if="hotReviews.length === 0" class="empty-state">
                    <i class="el-icon-chat-line-round"></i>
                    <p>暂无评价</p>
                    <p class="hint">成为第一个发表评价的人吧！</p>
                </div>

                <div v-for="review in hotReviews" :key="review.review_id" class="review-card">
                    <div class="review-header">
                        <div class="reviewer-info">
                            <!-- 修改：使用getAvatarUrl方法获取正确头像 -->
                            <el-avatar
                                :size="40"
                                :src="getAvatarUrl(review.avatar_url)"
                                :key="review.review_id"
                                class="reviewer-avatar">
                                <span v-if="!review.avatar_url">
                                    {{ (review.username || '用户').charAt(0).toUpperCase() }}
                                </span>
                            </el-avatar>
                            <div class="reviewer-details">
                                <span class="reviewer-name">{{ review.username || '匿名用户' }}</span>
                                <span class="review-time">{{ review.created_time }}</span>
                            </div>
                        </div>
                        <div class="review-rating">
                            <el-rate v-model="review.rating" disabled></el-rate>
                            <el-tag size="mini" type="info">{{ review.type }}</el-tag>
                        </div>
                    </div>

                    <div class="review-content">
                        <p class="review-text">{{ review.comment || '用户很懒，没有留下评价~' }}</p>
                        <div class="review-target">
                            <span v-if="review.dish_name">
                                <i class="el-icon-fork-spoon"></i>
                                评价菜品：{{ review.dish_name }}
                            </span>
                            <span>
                                <i class="el-icon-s-shop"></i>
                                店铺：{{ review.shop_name }}
                            </span>
                        </div>
                    </div>

                    <div class="review-actions">
                        <el-button
                            type="text"
                            :icon="review.liked ? 'el-icon-thumb' : 'el-icon-thumb'"
                            :class="{ 'liked-button': review.liked }"
                            @click="likeReview(review.review_id)">
                            有用({{ review.likes || 0 }})
                        </el-button>
                        <el-button
                            type="text"
                            icon="el-icon-s-shop"
                            @click="goToShop(review.shop_id)">
                            去店铺看看
                        </el-button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 我要评价内容 -->
        <div v-show="activeTab === 'rate'" class="rate-content">
            <div class="rate-panel" v-loading="loading.pending">
                <div v-if="pendingOrders.length === 0" class="empty-state">
                    <i class="el-icon-circle-check"></i>
                    <p>没有待评价的订单</p>
                    <p class="hint">完成订单后即可进行评价</p>
                    <el-button type="primary" @click="goToShopList">
                        去下单
                    </el-button>
                </div>

                <div v-for="order in pendingOrders" :key="order.order_id" class="pending-order">
                    <div class="order-header">
                        <span class="shop-name">{{ order.shop_name }}</span>
                        <div class="order-info">
                            <h3>订单：{{ order.order_id }}</h3>
                            <p class="order-time">{{ order.create_time }}</p>
                        </div>
                    </div>

                    <div class="order-dishes">
                        <div class="dishes-list">
                            <span v-for="dish in order.dishes" :key="dish.dish_id" class="dish-tag">
                                {{ dish.dish_name }}
                            </span>
                        </div>
                    </div>

                    <div class="rate-actions">
                        <div class="rate-form">
                            <div class="rate-input">
                                <span class="rate-label">整体评分：</span>
                                <el-rate
                                    v-model="order.rating"
                                    :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                                    @change="updateRating(order)">
                                </el-rate>
                            </div>

                            <div class="comment-input">
                                <el-input
                                    type="textarea"
                                    :rows="2"
                                    placeholder="写下您的用餐体验和建议吧~"
                                    v-model="order.comment"
                                    maxlength="200"
                                    show-word-limit>
                                </el-input>
                            </div>

                            <div class="dish-ratings" v-if="order.dishes && order.dishes.length > 0">
                                <p class="section-title">菜品评分（选填）：</p>
                                <div v-for="dish in order.dishes" :key="dish.dish_id" class="dish-rate-item">
                                     <img
                                        class="dish-image"
                                        :src="dish.image_url || defaultDishImage"
                                        @error="handleImageError(dish, $event, 'dish')"
                                      />
                                    <span class="dish-name">{{ dish.dish_name }}</span>
                                    <el-rate
                                        v-model="dish.rating"
                                        size="small"
                                        @change="updateDishRating(order, dish)">
                                    </el-rate>
                                </div>
                            </div>

                            <div class="submit-buttons">
                                <el-button
                                    type="primary"
                                    :loading="submitting[order.order_id]"
                                    @click="submitReview(order)">
                                    提交评价
                                </el-button>
                                <el-button
                                    type="info"
                                    @click="skipReview(order.order_id)">
                                    暂时跳过
                                </el-button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 店铺评价弹窗 -->
        <el-dialog
            :title="currentShopName + ' - 评价详情'"
            :visible.sync="reviewDialogVisible"
            width="800px"
            @close="handleReviewDialogClose">

            <div v-loading="loadingShopReviews">
                <!-- 评价统计 -->
                <div v-if="shopReviewStats" class="review-stats">
                    <div class="overall-rating">
                        <span class="rating-number">{{ (shopReviewStats.avg_rating || 0).toFixed(1) }}</span>
                        <div class="rating-info">
                            <el-rate v-model="shopReviewStats.avg_rating" disabled></el-rate>
                            <span class="total-count">{{ shopReviewStats.total_reviews || 0 }}条评价</span>
                        </div>
                    </div>

                    <div class="rating-distribution">
                        <div v-for="(count, rating) in (shopReviewStats.rating_distribution || {})"
                             :key="rating" class="distribution-item">
                            <span class="rating-label">{{ rating }}星</span>
                            <el-progress
                                :percentage="Number((shopReviewStats.total_reviews > 0 ? (count / shopReviewStats.total_reviews * 100).toFixed(1) : 0))"
                                :show-text="false"
                                :stroke-width="10"
                                :color="getProgressColor(rating)">
                            </el-progress>
                            <span class="rating-count">{{ count }}</span>
                        </div>
                    </div>
                </div>

                <!-- 评价列表 -->
                <div class="review-list-dialog">
                    <div v-if="currentShopReviews.length === 0" class="empty-state">
                        <el-empty description="暂无评价"></el-empty>
                    </div>

                    <div v-for="review in currentShopReviews" :key="review.review_id" class="review-item">
                        <div class="reviewer-info">
                            <!-- 修改：使用getAvatarUrl方法获取正确头像 -->
                       <el-avatar
                        :size="32"
                        :src="getAvatarUrl(review.avatar_url)"
                        :key="review.review_id"
                        class="reviewer-avatar">
                        <span v-if="!review.avatar_url">
                            {{ (review.username || '用户').charAt(0).toUpperCase() }}
                        </span>
                    </el-avatar>
                            <div class="reviewer-details">
                                <span class="reviewer-name">{{ review.username || '匿名用户' }}</span>
                                <div class="review-rating-time">
                                    <el-rate v-model="review.rating" disabled size="mini"></el-rate>
                                    <span class="review-time">{{ formatTime(review.created_time) }}</span>
                                </div>
                            </div>
                        </div>

                        <div class="review-content">
                            <p>{{ review.comment || '用户很懒，没有留下评价~' }}</p>
                            <div v-if="review.dishes && review.dishes.length > 0" class="review-dishes">
                                <span class="dish-label">包含菜品：</span>
                                <el-tag
                                    v-for="dish in review.dishes"
                                    :key="dish"
                                    size="mini"
                                    type="info">
                                    {{ dish }}
                                </el-tag>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <span slot="footer" class="dialog-footer">
                <el-button @click="reviewDialogVisible = false">关 闭</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'RecommendComponent',
   data() {
        return {
            activeTab: 'recommend',
            loading: {
                shops: false,
                reviews: false,
                pending: false,
                dishes: false,
                // 移除这里的 shopReviews: false
            },
            recommendedShops: [],
            hotReviews: [],
            pendingOrders: [],
            recommendedDishes: [],
            sortBy: 'recommend',
            activeFilter: 'all',
            filterTags: [
                { label: '全部', value: 'all' },
                { label: '高评分', value: 'high_rating' },
                { label: '人气店', value: 'popular' },
                { label: '新店', value: 'new' }
            ],
            submitting: {},
            defaultShopImage: '/images/shop/default-shop.jpg',
            defaultDishImage: '/images/dish/default-dish.jpg',

            // 点赞相关状态
            likeLoading: {}, // 记录每个评价的点赞加载状态
            userLikeStatus: {}, // 用户点赞状态缓存

            // 店铺评价相关
            reviewDialogVisible: false,
            currentShopReviews: [],
            shopReviewStats: null,
            loadingShopReviews: false, // 添加独立的加载状态属性
            currentShopId: null,
            currentShopName: '',

            // 用户信息缓存
            userAvatarCache: {},
            apiBaseUrl: 'http://127.0.0.1:5000'
        }
    },

    mounted() {
        this.loadData()
    },

    watch: {
        activeTab(newTab) {
            if (newTab === 'recommend') {
                this.loadRecommendedShops()
            } else if (newTab === 'reviews') {
                this.loadHotReviews()
            } else if (newTab === 'rate') {
                this.loadPendingOrders()
            }
        }
    },

    methods: {
        createAxiosInstance() {
            const token = localStorage.getItem('token')
            return axios.create({
                baseURL: this.apiBaseUrl,
                headers: token ? { token } : {},
                timeout: 10000
            })
        },

       getAvatarUrl(url) {
                // 如果为空，直接返回默认头像
                if (!url || url === 'null' || url === 'undefined') {
                    return '/images/user/default-avatar.jpg'
                }

                // 如果已经是完整URL，直接返回
                if (url.startsWith('http://') || url.startsWith('https://')) {
                    return url
                }

                // 确保路径以斜杠开头
                let path = url
                if (!path.startsWith('/')) {
                    path = '/' + path
                }

                return path
           },

        async loadData() {
            await this.loadRecommendedShops()
            await this.loadHotReviews()
            await this.loadRecommendedDishes()
            if (localStorage.getItem('token')) {
                await this.loadPendingOrders()
            }
        },

        /* ================== 关键修改：推荐店铺 ================== */
        async loadRecommendedShops() {
            try {
                this.loading.shops = true
                const http = this.createAxiosInstance()

                const response = await http.get('/api/recommend/shops', {
                    params: {
                        sort_by: this.sortBy,
                        filter: this.activeFilter
                    }
                })

                if (response.data.status === 200) {
                    this.recommendedShops = response.data.data.map(shop => ({
                        ...shop,
                        avg_rating: shop.avg_rating || 0,
                        review_count: shop.review_count || 0,
                        total_sales: shop.total_sales || 0,
                        order_count: shop.order_count || 0,
                        image_url: this.getAvatarUrl(shop.image_url) || this.defaultShopImage
                    }))
                } else {
                    this.$message.error(response.data.msg || '加载推荐店铺失败')
                }
            } catch (error) {
                console.error('加载推荐店铺失败:', error)
                this.$message.error('加载推荐店铺失败')
            } finally {
                this.loading.shops = false
            }
        },

        toggleFilter(filter) {
            this.activeFilter = filter
            this.loadRecommendedShops()
        },

        // 修改热评加载函数，获取点赞状态
        async loadHotReviews() {
            try {
                this.loading.reviews = true
                const http = this.createAxiosInstance()

                const response = await http.get('/api/recommend/hot-reviews')
                console.log('热门评价响应:', response.data)

                // 详细打印每个评价的数据
                if (response.data.status === 200 && response.data.data) {
                    console.log('第一个评价的完整数据:', response.data.data[0])
                    console.log('第一个评价的头像URL:', response.data.data[0]?.avatar_url)

                    this.hotReviews = response.data.data.map(review => ({
                        ...review,
                        created_time: this.formatTime(review.created_time),
                        likes: review.likes || 0,
                        liked: review.liked || false,
                        avatar_url: review.avatar_url || null // 确保有avatar_url字段
                    }))

                    // 再次检查处理后的数据
                    console.log('处理后第一个评价的头像URL:', this.hotReviews[0]?.avatar_url)
                }
            } catch (error) {
                console.error('加载热门评价失败:', error)
            } finally {
                this.loading.reviews = false
            }
        },

        // 获取用户头像URL
        async getUserAvatarUrl(userId) {
            if (!userId) return null;

            // 先检查缓存
            const cacheKey = `user_avatar_${userId}`;
            if (this.userAvatarCache[cacheKey]) {
                return this.userAvatarCache[cacheKey];
            }

            try {
                const http = this.createAxiosInstance();
                const response = await http.get(`/api/user/${userId}/info`);

                if (response.data.status === 200 && response.data.data && response.data.data.avatar_url) {
                    const avatarUrl = response.data.data.avatar_url;
                    // 缓存结果
                    this.userAvatarCache[cacheKey] = avatarUrl;
                    return avatarUrl;
                }
            } catch (error) {
                console.warn(`获取用户 ${userId} 头像失败:`, error);
            }

            return null; // 返回null，前端会显示默认头像
        },

        // 加载推荐菜品
        async loadRecommendedDishes() {
            try {
                this.loading.dishes = true
                const http = this.createAxiosInstance()

                const response = await http.get('/api/recommend/dishes')
                console.log('推荐菜品响应:', response.data)

                if (response.data.status === 200) {
                    this.recommendedDishes = response.data.data.map(dish => ({
                        ...dish,
                        avg_rating: dish.avg_rating || 0,
                        review_count: dish.review_count || 0,
                        // 处理图片URL
                        image_url: this.getAvatarUrl(dish.image_url) || this.defaultDishImage
                    }))
                }
            } catch (error) {
                console.error('加载推荐菜品失败:', error)
                this.$message.error('加载推荐菜品失败: ' + (error.response?.data?.msg || error.message))
            } finally {
                this.loading.dishes = false
            }
        },

        // 加载待评价订单
        async loadPendingOrders() {
            try {
                this.loading.pending = true
                const token = localStorage.getItem('token')
                if (!token) {
                    this.pendingOrders = []
                    return
                }

                const http = this.createAxiosInstance()
                const response = await http.get('/api/review/pending')

                if (response.data.status === 200) {
                    this.pendingOrders = response.data.data.map(order => ({
                        ...order,
                        rating: 5,
                        comment: '',
                        dishes: order.dishes ? order.dishes.map(dish => ({
                            ...dish,
                            rating: 5,
                            comment: ''
                        })) : []
                    }))

                    // 通知父组件更新待评价数量
                    this.$emit('update-pending-count', this.pendingOrders.length)
                } else if (response.data.status === 401) {
                    this.pendingOrders = []
                    this.$message.warning('请先登录查看待评价订单')
                } else {
                    this.$message.error(response.data.msg || '加载待评价订单失败')
                }
            } catch (error) {
                console.error('加载待评价订单失败:', error)
                this.pendingOrders = []
                if (error.response?.status !== 401) {
                    this.$message.error('加载待评价订单失败: ' + (error.response?.data?.msg || error.message))
                }
            } finally {
                this.loading.pending = false
            }
        },

        // 格式化时间
        formatTime(timeStr) {
            if (!timeStr) return ''

            try {
                // 尝试解析各种时间格式
                let date
                if (typeof timeStr === 'string') {
                    // 移除可能的额外空格
                    timeStr = timeStr.trim()

                    // 尝试常见的时间格式
                    if (timeStr.includes('T')) {
                        // ISO格式
                        date = new Date(timeStr)
                    } else if (timeStr.includes('-')) {
                        // MySQL datetime格式
                        date = new Date(timeStr.replace(' ', 'T') + 'Z')
                    } else {
                        return timeStr
                    }
                } else if (timeStr instanceof Date) {
                    date = timeStr
                } else {
                    return String(timeStr)
                }

                // 格式化日期
                const now = new Date()
                const diffMs = now - date
                const diffMins = Math.floor(diffMs / 60000)
                const diffHours = Math.floor(diffMins / 60)
                const diffDays = Math.floor(diffHours / 24)

                if (diffMins < 1) {
                    return '刚刚'
                } else if (diffMins < 60) {
                    return `${diffMins}分钟前`
                } else if (diffHours < 24) {
                    return `${diffHours}小时前`
                } else if (diffDays < 7) {
                    return `${diffDays}天前`
                } else {
                    // 显示具体日期
                    const year = date.getFullYear()
                    const month = (date.getMonth() + 1).toString().padStart(2, '0')
                    const day = date.getDate().toString().padStart(2, '0')
                    return `${year}-${month}-${day}`
                }
            } catch (error) {
                console.warn('时间格式化失败:', error, '原始时间:', timeStr)
                return timeStr
            }
        },

        // 标签切换
        handleTabClick(tab) {
            this.activeTab = tab.name
        },


        // 带筛选条件的加载推荐店铺
        async loadRecommendedShopsWithFilter() {
            // 这里可以根据筛选条件添加查询参数
            await this.loadRecommendedShops()
        },

        // 跳转到店铺
        goToShop(shopId) {
            this.$router.push(`/shop/${shopId}`)
        },

        // 跳转到菜品
        goToDish(dishId) {
            this.$router.push(`/dish/${dishId}`)
        },

        // 查看店铺详情
        viewShopMenu(shopId) {
            this.goToShop(shopId)
        },

        // 查看店铺评价（弹窗方式）
        async viewShopReviews(shopId, shopName = '') {
            this.currentShopId = shopId
            this.currentShopName = shopName || '店铺'
            await this.loadShopReviews()
            this.reviewDialogVisible = true
        },

        // 加载店铺评价数
        async loadShopReviews() {
            try {
                this.loadingShopReviews = true
                const http = this.createAxiosInstance()

                const response = await http.get(`/api/review/shop/${this.currentShopId}`)
                console.log('店铺评价响应:', response.data)

                if (response.data.status === 200) {
                    const reviews = response.data.data.reviews || []

                    // 检查第一个评价的数据
                    if (reviews.length > 0) {
                        console.log('店铺评价第一个数据:', reviews[0])
                        console.log('店铺评价头像URL:', reviews[0]?.avatar_url)
                    }

                    this.currentShopReviews = reviews.map(review => ({
                        ...review,
                        likes: review.likes || 0,
                        liked: review.liked || false,
                        avatar_url: review.avatar_url || null
                    }))

                    this.shopReviewStats = response.data.data.stats || {}
                }
            } catch (error) {
                console.error('加载店铺评价失败:', error)
            } finally {
                this.loadingShopReviews = false
            }
        },

        // 获取进度条颜色
        getProgressColor(rating) {
            const colors = {
                '1': '#F56C6C',
                '2': '#E6A23C',
                '3': '#409EFF',
                '4': '#67C23A',
                '5': '#67C23A'
            }
            return colors[rating] || '#409EFF'
        },

        // 关闭评价弹窗
        handleReviewDialogClose() {
            this.reviewDialogVisible = false
            this.currentShopReviews = []
            this.shopReviewStats = null
            this.currentShopId = null
            this.currentShopName = ''
        },

        // 图片加载失败处理
        handleImageError(item, event, type = 'shop') {
            if (type === 'shop') {
                event.target.src = this.defaultShopImage
            } else {
                event.target.src = this.defaultDishImage
            }
        },

            // 点赞评价
            async likeReview(reviewId) {
                try {
                    const token = localStorage.getItem('token')
                    if (!token) {
                        this.$message.warning('请先登录')
                        return
                    }

                    const http = this.createAxiosInstance()
                    const response = await http.post(`/api/review/${reviewId}/like`)

                    if (response.data.status === 200) {
                        // 更新本地点赞数和点赞状态
                        const review = this.hotReviews.find(r => r.review_id === reviewId)
                        if (review) {
                            review.likes = response.data.likes || 0
                            review.liked = response.data.liked || false
                        }
                        this.$message.success(response.data.msg || '操作成功')
                    } else {
                        this.$message.info(response.data.msg || '操作失败')
                    }
                } catch (error) {
                    console.error('点赞失败:', error)
                    if (error.response?.status === 401) {
                        this.$message.warning('请先登录')
                    } else {
                        this.$message.error('操作失败')
                    }
                }
            },

        // 跳转到店铺列表
        goToShopList() {
            this.$router.push('/shops')
        },

        // 更新整体评分
        updateRating(order) {
            console.log(`订单 ${order.order_id} 评分更新为: ${order.rating}`)
        },

        // 更新菜品评分
        updateDishRating(order, dish) {
            console.log(`菜品 ${dish.dish_name} 评分更新为: ${dish.rating}`)
        },

        // 提交评价
        async submitReview(order) {
            try {
                const token = localStorage.getItem('token')
                if (!token) {
                    this.$message.error('请先登录')
                    return
                }

                this.$set(this.submitting, order.order_id, true)

                const http = this.createAxiosInstance()
                let hasError = false

                // 1. 提交店铺整体评价
                if (order.rating && order.rating > 0) {
                    const shopReviewData = {
                        order_id: order.order_id,
                        shop_id: order.shop_id,
                        rating: order.rating,
                        comment: order.comment || '整体体验良好',
                        review_type: 'shop'
                    }

                    try {
                        const shopResponse = await http.post('/api/review/submit', shopReviewData)
                        if (shopResponse.data.status !== 200) {
                            this.$message.error(shopResponse.data.msg || '店铺评价提交失败')
                            hasError = true
                        }
                    } catch (error) {
                        console.error('店铺评价提交失败:', error)
                        this.$message.error('店铺评价提交失败')
                        hasError = true
                    }
                }

                // 2. 提交菜品评价（如果有）
                if (!hasError && order.dishes && order.dishes.length > 0) {
                    const dishPromises = order.dishes
                        .filter(dish => dish.rating && dish.rating > 0)
                        .map(dish => http.post('/api/review/submit', {
                            order_id: order.order_id,
                            shop_id: order.shop_id,
                            dish_id: dish.dish_id,
                            rating: dish.rating,
                            comment: dish.comment || `${dish.dish_name}：${order.comment || '味道不错'}`,
                            review_type: 'dish'
                        }))

                    if (dishPromises.length > 0) {
                        try {
                            const dishResults = await Promise.allSettled(dishPromises)
                            const failedDishes = dishResults.filter(result =>
                                result.status === 'rejected' ||
                                (result.status === 'fulfilled' && result.value.data.status !== 200)
                            )

                            if (failedDishes.length > 0) {
                                console.warn(`${failedDishes.length}个菜品评价提交失败`)
                            }
                        } catch (error) {
                            console.error('菜品评价提交失败:', error)
                        }
                    }
                }

                if (!hasError) {
                    this.$message.success('评价提交成功！')

                    // 从待评价列表中移除
                    this.pendingOrders = this.pendingOrders.filter(o => o.order_id !== order.order_id)

                    // 通知父组件更新数量
                    this.$emit('update-pending-count', this.pendingOrders.length)

                    // 重新加载数据
                    await Promise.all([
                        this.loadHotReviews(),
                        this.loadRecommendedShops(),
                        this.loadRecommendedDishes()
                    ])
                }

            } catch (error) {
                console.error('提交评价失败:', error)
                if (error.response && error.response.data) {
                    this.$message.error(error.response.data.msg || '提交评价失败')
                } else {
                    this.$message.error('提交评价失败: ' + error.message)
                }
            } finally {
                this.$set(this.submitting, order.order_id, false)
            }
        },

        // 跳过评价
        skipReview(orderId) {
            this.$confirm('确定跳过评价吗？跳过后将无法再次评价此订单', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                this.pendingOrders = this.pendingOrders.filter(order => order.order_id !== orderId)
                this.$emit('update-pending-count', this.pendingOrders.length)
                this.$message.info('已跳过该订单评价')
            })
        }
    }
}
</script>

<style scoped>
.recommend-container {
    padding: 20px;
}

/* 标签切换样式 */
.tab-switcher {
    background: white;
    border-radius: 8px;
    padding: 0 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.tab-switcher .el-tabs__nav-wrap::after {
    height: 1px;
}

.pending-badge {
    margin-left: 5px;
}

/* 筛选栏样式 */
.filter-bar {
    background: white;
    border-radius: 8px;
    padding: 15px 20px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
}

.filter-tags {
    display: flex;
    gap: 10px;
}

.filter-tag {
    cursor: pointer;
    transition: all 0.3s;
}

.filter-tag:hover {
    transform: translateY(-2px);
}

/* 推荐店铺样式 */
.shop-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.shop-card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    border: 1px solid #ebeef5;
}

.shop-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-color: #409EFF;
}

.shop-image {
    position: relative;
    height: 180px;
    overflow: hidden;
    cursor: pointer;
}

.shop-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}

.shop-card:hover .shop-image img {
    transform: scale(1.05);
}

.shop-tag {
    position: absolute;
    top: 10px;
    right: 10px;
}

.shop-info {
    padding: 15px;
}

.shop-header {
    cursor: pointer;
    margin-bottom: 10px;
}

.shop-name {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.shop-rating {
    display: flex;
    align-items: center;
    gap: 10px;
}

.review-count {
    font-size: 12px;
    color: #909399;
}

.shop-desc {
    font-size: 14px;
    color: #606266;
    margin: 10px 0;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.shop-stats {
    display: flex;
    justify-content: space-between;
    margin: 15px 0;
    padding: 10px 0;
    border-top: 1px solid #ebeef5;
    border-bottom: 1px solid #ebeef5;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    color: #909399;
}

.stat-item i {
    font-size: 14px;
}

.shop-actions {
    display: flex;
    justify-content: space-between;
    gap: 10px;
}

/* 评价卡片样式 */
.reviews-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.review-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.reviewer-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.reviewer-avatar {
    flex-shrink: 0;
}

.reviewer-details {
    display: flex;
    flex-direction: column;
}

.reviewer-name {
    font-weight: 600;
    color: #303133;
}

.review-time {
    font-size: 12px;
    color: #909399;
}

.review-rating {
    display: flex;
    align-items: center;
    gap: 10px;
}

.review-content {
    margin-bottom: 15px;
}

.review-text {
    font-size: 14px;
    line-height: 1.6;
    color: #606266;
    margin-bottom: 10px;
}

.review-target {
    display: flex;
    gap: 20px;
    font-size: 13px;
    color: #909399;
}

.review-target i {
    margin-right: 5px;
}

.review-actions {
    display: flex;
    gap: 20px;
    padding-top: 15px;
    border-top: 1px solid #ebeef5;
}

/* 评价表单样式 */
.rate-panel {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.pending-order {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;
}

.order-info h3 {
    margin: 0;
    font-size: 16px;
    color: #303133;
}

.order-time {
    margin: 5px 0 0 0;
    font-size: 12px;
    color: #909399;
}

.shop-name {
    font-weight: 600;
    color: #409EFF;
    font-size: 16px;
}

.order-dishes {
    margin-bottom: 20px;
}

.dishes-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.dish-tag {
    padding: 4px 12px;
    background: #f0f9ff;
    border: 1px solid #d9ecff;
    border-radius: 20px;
    font-size: 13px;
    color: #409EFF;
}

.rate-form {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.rate-input {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.rate-label {
    font-weight: 600;
    color: #303133;
}

.comment-input {
    margin-bottom: 20px;
}

.dish-ratings {
    margin-top: 20px;
}

.section-title {
    font-weight: 600;
    color: #303133;
    margin-bottom: 10px;
}

.dish-rate-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px dashed #dcdfe6;
}

.dish-rate-item:last-child {
    border-bottom: none;
}

.dish-name {
    font-size: 14px;
    color: #606266;
}

.submit-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 20px;
}

/* 空状态样式 */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #909399;
}

.empty-state i {
    font-size: 48px;
    margin-bottom: 15px;
    color: #c0c4cc;
}

.empty-state p {
    margin: 10px 0;
    font-size: 16px;
}

.empty-state .hint {
    font-size: 14px;
    color: #c0c4cc;
    margin-bottom: 20px;
}

/* 店铺评价弹窗样式 */
.review-stats {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #ebeef5;
}

.overall-rating {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

.rating-number {
    font-size: 36px;
    font-weight: bold;
    color: #ff9900;
    min-width: 60px;
}

.rating-info {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.total-count {
    font-size: 14px;
    color: #909399;
}

.rating-distribution {
    margin-top: 15px;
}

.distribution-item {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.rating-label {
    width: 40px;
    font-size: 14px;
    color: #606266;
    text-align: right;
}

.distribution-item .el-progress {
    flex: 1;
}

.rating-count {
    width: 40px;
    font-size: 14px;
    color: #909399;
    text-align: right;
}

.review-list-dialog {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 10px;
}

.review-list-dialog::-webkit-scrollbar {
    width: 6px;
}

.review-list-dialog::-webkit-scrollbar-thumb {
    background-color: #dcdfe6;
    border-radius: 3px;
}

.review-item {
    padding: 15px 0;
    border-bottom: 1px solid #f0f0f0;
}

.review-item:last-child {
    border-bottom: none;
}

.reviewer-info {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.reviewer-details {
    display: flex;
    flex-direction: column;
}

.reviewer-name {
    font-weight: 600;
    font-size: 14px;
    color: #303133;
}

.review-rating-time {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 2px;
}

.review-time {
    font-size: 12px;
    color: #909399;
}

.review-content p {
    margin: 0 0 8px 0;
    font-size: 14px;
    line-height: 1.5;
    color: #606266;
}

.review-dishes {
    display: flex;
    align-items: center;
    gap: 5px;
    flex-wrap: wrap;
}

.dish-label {
    font-size: 12px;
    color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .shop-grid {
        grid-template-columns: 1fr;
    }

    .filter-bar {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }

    .filter-tags {
        flex-wrap: wrap;
    }

    .shop-actions {
        flex-direction: column;
    }

    .order-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .dish-rate-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }

    /* 弹窗响应式 */
    .overall-rating {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .distribution-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }

    .distribution-item .el-progress {
        width: 100%;
    }
}

.dish-review-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.dish-image {
  width: 56px;
  height: 56px;
  border-radius: 6px;
  object-fit: cover;
  margin-right: 12px;
}

.dish-info {
  flex: 1;
}

.dish-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

</style>