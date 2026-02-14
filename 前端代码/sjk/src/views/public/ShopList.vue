<template>
  <div class="shop-list">
    <div class="stats-bar">
      <div class="stat-item">
        <div class="stat-icon">🏪</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalStats.shops }}</div>
          <div class="stat-label">店铺数量</div>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索店铺名称..."
        prefix-icon="el-icon-search"
        class="search-input"
        clearable
      />
    </div>

    <!-- 店铺列表 -->
    <div class="main-content">
      <div class="header">
        <h1>选择店铺</h1>
        <p>选择您喜欢的店铺开始点餐</p>
      </div>

      <div class="body">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else class="shop-grid">
          <div
            v-for="shop in filteredShops"
            :key="shop.shop_id"
            class="shop-card"
            @click="enterShop(shop)"
          >
            <div class="shop-image-container">
              <img
                :src="shop.image_url"
                :alt="shop.shop_name"
                class="shop-image"
                @error="handleImageError"
              />
              <div class="image-overlay"></div>
            </div>

            <div class="shop-content">
              <div class="shop-header">
                <h3 class="shop-title">{{ shop.shop_name }}</h3>
              </div>
              <div class="shop-description">
                {{ shop.description || '欢迎光临本店' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredShops.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无店铺数据"></el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      shops: [],
      loading: false,
      searchText: '',
      totalStats: {
        shops: 0
      }
    }
  },
  computed: {
    filteredShops() {
      if (!this.searchText) {
        return this.shops
      }
      return this.shops.filter(shop =>
        shop.shop_name.toLowerCase().includes(this.searchText.toLowerCase())
      )
    }
  },
  created() {
    this.getShops()
  },
  methods: {
    async getShops() {
      this.loading = true
      try {
        const res = await this.$axios.get("/api/shops")
        console.log('获取店铺数据:', res.data)

        if (res.data.status === 200) {
          this.shops = res.data.data
          this.totalStats.shops = this.shops.length
        } else {
          this.$message.error('获取店铺信息失败')
        }
      } catch (error) {
        console.error('请求失败:', error)
        this.$message.error('网络错误，请稍后重试')
      } finally {
        this.loading = false
      }
    },

    enterShop(shop) {
      // 跳转到店铺详情页
      this.$router.push(`/shop/${shop.shop_id}`)
    },

    handleImageError(event) {
      event.target.src = '/images/food/default-food.jpg'
    }
  }
}
</script>

<style scoped>
.shop-list {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.stats-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #ff6b35;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.toolbar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-input {
  width: 300px;
}

.main-content {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  text-align: center;
}

.header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
}

.header p {
  margin: 10px 0 0 0;
  opacity: 0.9;
}

.body {
  padding: 30px;
}

.loading-container {
  padding: 40px;
}

.shop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.shop-card {
  background: white;
  border: 1px solid #eaeaea;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.shop-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.shop-image-container {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
}

.shop-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.shop-card:hover .shop-image {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 60%, rgba(0,0,0,0.1));
}

.shop-content {
  padding: 15px;
}

.shop-header {
  margin-bottom: 10px;
}

.shop-title {
  margin: 0;
  color: #333;
  font-size: 16px;
  line-height: 1.4;
}

.shop-description {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-state {
  padding: 60px 0;
}

@media (max-width: 768px) {
  .shop-list {
    padding: 10px;
  }

  .stats-bar {
    flex-direction: column;
  }

  .toolbar {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .body {
    padding: 15px;
  }

  .shop-grid {
    grid-template-columns: 1fr;
  }

  .shop-image-container {
    height: 140px;
  }
}
</style>