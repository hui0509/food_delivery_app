<template>
  <div class="shop-detail">
    <!-- 店铺头部信息 -->
    <div class="shop-header">
      <div class="shop-back" @click="$router.back()">
        <i class="el-icon-arrow-left"></i> 返回
      </div>
      <div class="shop-hero">
        <img :src="shop.image_url" :alt="shop.shop_name" class="shop-hero-image" />
        <div class="shop-hero-content">
          <h1>{{ shop.shop_name }}</h1>
          <p class="shop-description">{{ shop.description }}</p>
        </div>
      </div>
    </div>

    <!-- 菜品列表 -->
    <div class="dishes-section">
      <h2 class="section-title">菜品列表</h2>

      <div v-if="dishesLoading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else class="dishes-grid">
        <div
          v-for="dish in dishes"
          :key="dish.dish_id"
          class="dish-card"
        >
          <div class="dish-image-container">
            <img
              :src="dish.image_url"
              :alt="dish.dish_name"
              class="dish-image"
              @error="handleImageError"
            />
          </div>

          <div class="dish-content">
            <div class="dish-header">
              <h3 class="dish-name">{{ dish.dish_name }}</h3>
              <span class="dish-price">¥{{ dish.price }}</span>
            </div>

            <p class="dish-description">{{ dish.description || '美味菜品' }}</p>

            <div class="dish-footer">
              <span class="dish-sales">月售 {{ dish.monthly_sales }}份</span>
              <el-button
                type="primary"
                size="small"
                @click="addToCart(dish)"
                class="add-cart-btn"
              >
                <i class="el-icon-plus"></i>
                加入购物车
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="dishes.length === 0 && !dishesLoading" class="empty-state">
        <el-empty description="该店铺暂无菜品"></el-empty>
      </div>
    </div>

    <!-- 购物车悬浮按钮 -->
    <div class="cart-float" v-if="cartTotal > 0" @click="showCartDialog = true">
      <el-badge :value="cartTotal" class="cart-badge">
        <div class="cart-button">
          <i class="el-icon-shopping-cart-2"></i>
          <span class="cart-total">¥{{ cartAmount }}</span>
        </div>
      </el-badge>
    </div>

    <!-- 购物车对话框 -->
    <el-dialog
      title="购物车"
      :visible.sync="showCartDialog"
      width="500px"
      :close-on-click-modal="false"
      class="custom-dialog"
    >
      <div class="cart-dialog">
        <div v-if="cartItems.length === 0" class="empty-cart">
          <el-empty description="购物车为空"></el-empty>
        </div>

        <div v-else>
          <div class="cart-items">
            <div
              v-for="item in cartItems"
              :key="item.cart_id"
              class="cart-item"
            >
              <div class="item-info">
                <h4>{{ item.dish_name }}</h4>
                <p class="item-price">¥{{ item.price }} × {{ item.quantity }}</p>
              </div>
              <div class="item-actions">
                <span class="item-subtotal">¥{{ item.subtotal }}</span>
                <el-button
                  type="danger"
                  size="mini"
                  icon="el-icon-delete"
                  @click="removeFromCart(item.cart_id)"
                ></el-button>
              </div>
            </div>
          </div>

          <div class="cart-summary">
            <div class="total-amount">
              总计: <span class="amount">¥{{ cartAmount }}</span>
            </div>
          </div>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="clearCart" :disabled="cartItems.length === 0">
          清空购物车
        </el-button>
        <el-button
          type="primary"
          @click="showOrderDialog = true"
          :disabled="cartItems.length === 0"
          class="checkout-btn"
        >
          去下单
        </el-button>
      </div>
    </el-dialog>

    <!-- 下单对话框 -->
    <el-dialog
      title="确认订单"
      :visible.sync="showOrderDialog"
      width="600px"
      :close-on-click-modal="false"
      class="custom-dialog"
      @close="resetOrderForm"
    >
      <div class="order-dialog">
        <!-- 订单信息概览 -->
        <div class="order-summary">
          <div class="shop-info">
            <h3>{{ shop.shop_name }}</h3>
          </div>
          <div class="amount-info">
            <span class="label">订单金额：</span>
            <span class="price">¥{{ cartAmount }}</span>
          </div>
        </div>

        <!-- 地址选择 -->
        <div class="address-section">
          <h3 class="section-title">收货地址</h3>

          <div class="address-tabs">
            <el-radio-group v-model="addressTab" @change="handleAddressTabChange">
              <el-radio-button label="select">选择地址</el-radio-button>
              <el-radio-button label="new">新增地址</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 地址选择模式 -->
          <div v-if="addressTab === 'select'" class="address-selector">
            <div v-if="userAddresses.length === 0" class="no-address">
              <el-empty description="暂无地址，请新增地址"></el-empty>
            </div>

            <div v-else class="address-list">
              <div
                v-for="address in userAddresses"
                :key="address.address_id"
                class="address-item"
                :class="{ 'selected': selectedAddressId === address.address_id }"
                @click="selectAddress(address.address_id)"
              >
                <div class="address-header">
                  <div class="address-tags">
                    <el-tag
                      v-if="address.is_default"
                      type="success"
                      size="mini"
                      class="default-tag"
                    >
                      默认
                    </el-tag>
                    <el-tag
                      :type="getAddressLabelColor(address.address_label)"
                      size="mini"
                    >
                      {{ getAddressLabelText(address.address_label) }}
                    </el-tag>
                  </div>
                  <div class="address-actions">
                    <el-button
                      v-if="!address.is_default"
                      type="text"
                      size="mini"
                      @click.stop="setDefaultAddress(address.address_id)"
                    >
                      设为默认
                    </el-button>
                  </div>
                </div>
                <div class="address-content">
                  <div class="consignee-info">
                    <span class="name">{{ address.cons_name }}</span>
                    <span class="phone">{{ address.cons_phone }}</span>
                  </div>
                  <div class="address-detail">
                    <i class="el-icon-location"></i>
                    {{ address.province }}{{ address.city }}{{ address.district }}{{ address.street }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 新增地址模式 -->
          <div v-else class="address-form-container">
            <el-form
              ref="newAddressForm"
              :model="newAddressForm"
              :rules="addressRules"
              label-width="80px"
              size="small"
            >
              <el-form-item label="收货人" prop="cons_name">
                <el-input
                  v-model="newAddressForm.cons_name"
                  placeholder="请输入收货人姓名"
                  maxlength="10"
                ></el-input>
              </el-form-item>

              <el-form-item label="手机号" prop="cons_phone">
                <el-input
                  v-model="newAddressForm.cons_phone"
                  placeholder="请输入手机号"
                  maxlength="11"
                ></el-input>
              </el-form-item>

              <el-form-item label="所在地区" required>
                <div class="region-selector">
                  <el-select
                    v-model="newAddressForm.province"
                    placeholder="省份"
                    @change="handleProvinceChange"
                    style="width: 32%; margin-right: 2%;"
                  >
                    <el-option
                      v-for="province in provinceOptions"
                      :key="province.value"
                      :label="province.label"
                      :value="province.value"
                    ></el-option>
                  </el-select>

                  <el-select
                    v-model="newAddressForm.city"
                    placeholder="城市"
                    @change="handleCityChange"
                    style="width: 32%; margin-right: 2%;"
                    :disabled="!newAddressForm.province"
                  >
                    <el-option
                      v-for="city in cityOptions"
                      :key="city.value"
                      :label="city.label"
                      :value="city.value"
                    ></el-option>
                  </el-select>

                  <el-select
                    v-model="newAddressForm.district"
                    placeholder="区县"
                    style="width: 32%;"
                    :disabled="!newAddressForm.city"
                  >
                    <el-option
                      v-for="district in districtOptions"
                      :key="district.value"
                      :label="district.label"
                      :value="district.value"
                    ></el-option>
                  </el-select>
                </div>
              </el-form-item>

              <el-form-item label="详细地址" prop="street">
                <el-input
                  v-model="newAddressForm.street"
                  placeholder="街道、小区、门牌号等"
                  type="textarea"
                  :rows="2"
                  maxlength="100"
                ></el-input>
              </el-form-item>

              <el-form-item label="地址标签" prop="address_label">
                <el-select
                  v-model="newAddressForm.address_label"
                  placeholder="请选择"
                  style="width: 100%"
                >
                  <el-option label="家" value="home"></el-option>
                  <el-option label="公司" value="company"></el-option>
                  <el-option label="学校" value="school"></el-option>
                  <el-option label="其他" value="other"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="设为默认" prop="is_default">
                <el-switch v-model="newAddressForm.is_default"></el-switch>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 配送方式 -->
        <div class="delivery-section">
          <h3 class="section-title">配送方式</h3>
          <el-radio-group v-model="orderForm.order_way">
            <el-radio label="自提">自提</el-radio>
            <el-radio label="网上订餐">外卖配送</el-radio>
          </el-radio-group>
        </div>

        <!-- 备注 -->
        <div class="remark-section">
          <h3 class="section-title">备注</h3>
          <el-input
            v-model="orderForm.remark"
            placeholder="请输入备注信息（选填）"
            type="textarea"
            :rows="2"
            maxlength="100"
            show-word-limit
          ></el-input>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="showOrderDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitOrder"
          :loading="submitting"
          class="checkout-btn"
          :disabled="!isAddressValid"
        >
          提交订单
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ShopDetail',
  data() {
    // 手机号验证规则
    const validatePhone = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入手机号'));
      } else if (!/^1[3-9]\d{9}$/.test(value)) {
        callback(new Error('请输入正确的手机号'));
      } else {
        callback();
      }
    };

    return {
      // 店铺和菜品数据
      shop: {},
      dishes: [],
      dishesLoading: false,

      // 购物车相关
      cartItems: [],
      showCartDialog: false,
      showOrderDialog: false,

      // 地址管理相关
      userAddresses: [],
      addressTab: 'select', // 'select' or 'new'
      selectedAddressId: null,
      addressLoading: false,

      // 新增地址表单
      newAddressForm: {
        cons_name: '',
        cons_phone: '',
        province: '',
        city: '',
        district: '',
        street: '',
        address_label: 'home',
        is_default: false
      },

      // 地区数据
      provinceOptions: [
        { value: '河南省', label: '河南省' },
        { value: '北京市', label: '北京市' },
        { value: '上海市', label: '上海市' },
        { value: '广东省', label: '广东省' },
        { value: '浙江省', label: '浙江省' }
      ],
      cityOptions: [],
      districtOptions: [],

      // 订单表单
      orderForm: {
        order_way: '网上订餐',
        remark: ''
      },

      // 表单验证
      addressRules: {
        cons_name: [
          { required: true, message: '请输入收货人姓名', trigger: 'blur' },
          { min: 2, max: 10, message: '姓名长度在2到10个字符', trigger: 'blur' }
        ],
        cons_phone: [
          { required: true, validator: validatePhone, trigger: 'blur' }
        ],
        street: [
          { required: true, message: '请输入详细地址', trigger: 'blur' },
          { min: 5, max: 100, message: '地址长度在5到100个字符', trigger: 'blur' }
        ],
        address_label: [
          { required: true, message: '请选择地址标签', trigger: 'change' }
        ]
      },

      submitting: false
    }
  },
  computed: {
    // 购物车总数
    cartTotal() {
      return this.cartItems.reduce((sum, item) => sum + item.quantity, 0)
    },

    // 购物车总金额
    cartAmount() {
      return this.cartItems.reduce((sum, item) => sum + item.subtotal, 0)
    },

    // 地址是否有效
    isAddressValid() {
      if (this.addressTab === 'select') {
        return this.selectedAddressId !== null
      } else {
        // 检查新增地址表单是否有效
        return this.$refs.newAddressForm && this.$refs.newAddressForm.validate
      }
    }
  },
  watch: {
    // 监听下单对话框显示状态
    showOrderDialog(newVal) {
      if (newVal) {
        this.loadUserAddresses()
        this.addressTab = 'select'
        this.selectedAddressId = null
      }
    }
  },
  created() {
    this.getShopDetail()
    this.getDishes()
    this.getCart()
  },
  methods: {
    // 获取店铺详情
    async getShopDetail() {
      const shopId = this.$route.params.shopId
      try {
        const res = await this.$axios.get(`/api/shops/${shopId}`)
        if (res.data.status === 200) {
          this.shop = res.data.data
        } else {
          this.$message.error('获取店铺信息失败')
        }
      } catch (error) {
        console.error('请求失败:', error)
        this.$message.error('网络错误，请稍后重试')
      }
    },

    // 获取菜品列表
    async getDishes() {
      const shopId = this.$route.params.shopId
      this.dishesLoading = true
      try {
        const res = await this.$axios.get(`/api/shops/${shopId}/dishes`)
        if (res.data.status === 200) {
          this.dishes = res.data.data
        } else {
          this.$message.error('获取菜品信息失败')
        }
      } catch (error) {
        console.error('请求失败:', error)
        this.$message.error('网络错误，请稍后重试')
      } finally {
        this.dishesLoading = false
      }
    },

    // 获取购物车
    async getCart() {
      try {
        const res = await this.$axios.get('/api/cart')
        if (res.data.status === 200) {
          this.cartItems = res.data.data.items || []
        }
      } catch (error) {
        console.error('获取购物车失败:', error)
      }
    },

    // 添加到购物车
    async addToCart(dish) {
      try {
        const res = await this.$axios.post('/api/cart/add', {
          dish_id: dish.dish_id,
          quantity: 1
        })

        if (res.data.status === 200) {
          this.$message.success('添加成功')
          this.getCart()
        } else {
          this.$message.error(res.data.msg || '添加失败')
        }
      } catch (error) {
        console.error('添加到购物车失败:', error)
        this.$message.error('添加失败，请稍后重试')
      }
    },

    // 从购物车删除
    async removeFromCart(cartId) {
      try {
        const res = await this.$axios.post('/api/cart/remove', {
          cart_id: cartId
        })

        if (res.data.status === 200) {
          this.$message.success('删除成功')
          this.getCart()
        }
      } catch (error) {
        console.error('删除购物车项失败:', error)
        this.$message.error('删除失败')
      }
    },

    // 清空购物车
    async clearCart() {
      try {
        const res = await this.$axios.post('/api/cart/clear')

        if (res.data.status === 200) {
          this.$message.success('清空成功')
          this.cartItems = []
          this.showCartDialog = false
        }
      } catch (error) {
        console.error('清空购物车失败:', error)
        this.$message.error('清空失败')
      }
    },

    // 加载用户地址
    async loadUserAddresses() {
      this.addressLoading = true
      try {
        const res = await this.$axios.get('/api/user/addresses')
        if (res.data.status === 200) {
          this.userAddresses = res.data.data || []

          // 如果有默认地址，自动选中
          const defaultAddress = this.userAddresses.find(addr => addr.is_default)
          if (defaultAddress) {
            this.selectedAddressId = defaultAddress.address_id
          }
        }
      } catch (error) {
        console.error('加载地址失败:', error)
      } finally {
        this.addressLoading = false
      }
    },

    // 选择地址
    selectAddress(addressId) {
      this.selectedAddressId = addressId
    },

    // 设置默认地址
    async setDefaultAddress(addressId) {
      try {
        const res = await this.$axios.patch(`/api/user/addresses/${addressId}/set-default`)
        if (res.data.status === 200) {
          this.$message.success('已设置为默认地址')
          this.loadUserAddresses()
        } else {
          this.$message.error(res.data.msg || '设置失败')
        }
      } catch (error) {
        console.error('设置默认地址失败:', error)
        this.$message.error('设置默认地址失败')
      }
    },

    // 地址标签颜色
    getAddressLabelColor(label) {
      const colors = {
        'home': 'success',
        'company': 'warning',
        'school': 'primary',
        'other': 'info'
      }
      return colors[label] || 'info'
    },

    // 地址标签文本
    getAddressLabelText(label) {
      const texts = {
        'home': '家',
        'company': '公司',
        'school': '学校',
        'other': '其他'
      }
      return texts[label] || label
    },

    // 地址标签页切换
    handleAddressTabChange(tab) {
      if (tab === 'new') {
        this.selectedAddressId = null
        this.resetAddressForm()
      }
    },

    // 省份变化
    handleProvinceChange(province) {
      this.newAddressForm.city = ''
      this.newAddressForm.district = ''
      this.cityOptions = []
      this.districtOptions = []

      if (province) {
        if (province === '河南省') {
          this.cityOptions = [
            { value: '郑州市', label: '郑州市' },
            { value: '洛阳市', label: '洛阳市' }
          ]
        } else if (province === '北京市') {
          this.cityOptions = [
            { value: '北京市', label: '北京市' }
          ]
        } else if (province === '广东省') {
          this.cityOptions = [
            { value: '广州市', label: '广州市' },
            { value: '深圳市', label: '深圳市' }
          ]
        }
      }
    },

    // 城市变化
    handleCityChange(city) {
      this.newAddressForm.district = ''
      this.districtOptions = []

      if (city === '郑州市') {
        this.districtOptions = [
          { value: '金水区', label: '金水区' },
          { value: '二七区', label: '二七区' }
        ]
      } else if (city === '广州市') {
        this.districtOptions = [
          { value: '天河区', label: '天河区' },
          { value: '越秀区', label: '越秀区' }
        ]
      }
    },

    // 保存新增地址
    async saveNewAddress() {
      try {
        // 验证表单
        const valid = await this.$refs.newAddressForm.validate()
        if (!valid) return

        const res = await this.$axios.post('/api/user/addresses', this.newAddressForm)

        if (res.data.status === 200) {
          this.$message.success('地址保存成功')
          await this.loadUserAddresses()

          // 切换到选择地址标签页并选中新地址
          this.addressTab = 'select'
          const latestRes = await this.$axios.get('/api/user/addresses')
          if (latestRes.data.status === 200) {
            this.userAddresses = latestRes.data.data
            // 如果是默认地址，选中它
            if (this.newAddressForm.is_default) {
              const defaultAddr = this.userAddresses.find(addr => addr.is_default)
              if (defaultAddr) {
                this.selectedAddressId = defaultAddr.address_id
              }
            }
          }

          this.resetAddressForm()
        } else {
          this.$message.error(res.data.msg || '地址保存失败')
        }
      } catch (error) {
        console.error('保存地址失败:', error)
        this.$message.error('地址保存失败')
      }
    },

    // 提交订单
    async submitOrder() {
      try {
        // 验证地址
        if (this.addressTab === 'select' && !this.selectedAddressId) {
          this.$message.warning('请选择收货地址')
          return
        }

        // 如果是新增地址模式，先保存地址
        if (this.addressTab === 'new') {
          await this.saveNewAddress()
        }

        // 获取选中的地址信息
        const selectedAddress = this.userAddresses.find(
          addr => addr.address_id === this.selectedAddressId
        )

        if (!selectedAddress) {
          this.$message.error('请选择有效的收货地址')
          return
        }

        // 构建订单数据
        const orderData = {
          order_way: this.orderForm.order_way,
          cons_name: selectedAddress.cons_name,
          cons_phone: selectedAddress.cons_phone,
          cons_addre: `${selectedAddress.province}${selectedAddress.city}${selectedAddress.district}${selectedAddress.street}`,
          remark: this.orderForm.remark || '',
          address_id: this.selectedAddressId
        }

        this.submitting = true

        const res = await this.$axios.post('/api/order/cart', orderData)

        if (res.data.status === 200) {
          this.$message.success('下单成功！')
          this.showOrderDialog = false
          this.showCartDialog = false

          // 清空购物车
          await this.clearCart()

          // 提示用户
          this.$confirm('订单创建成功！是否查看订单详情？', '提示', {
            confirmButtonText: '查看订单',
            cancelButtonText: '继续购物',
            type: 'success'
          }).then(() => {
            this.$router.push('/user/unsend')
          }).catch(() => {
            // 继续留在当前页面
          })
        } else {
          this.$message.error(res.data.msg || '下单失败')
        }
      } catch (error) {
        console.error('下单失败:', error)
        this.$message.error('下单失败，请稍后重试')
      } finally {
        this.submitting = false
      }
    },

    // 重置地址表单
    resetAddressForm() {
      if (this.$refs.newAddressForm) {
        this.$refs.newAddressForm.resetFields()
      }
      this.newAddressForm = {
        cons_name: '',
        cons_phone: '',
        province: '',
        city: '',
        district: '',
        street: '',
        address_label: 'home',
        is_default: false
      }
      this.cityOptions = []
      this.districtOptions = []
    },

    // 重置订单表单
    resetOrderForm() {
      this.orderForm = {
        order_way: '网上订餐',
        remark: ''
      }
      this.addressTab = 'select'
      this.selectedAddressId = null
      if (this.$refs.newAddressForm) {
        this.$refs.newAddressForm.resetFields()
      }
    },

    // 图片加载失败处理
    handleImageError(event) {
      event.target.src = '/images/food/default-food.jpg'
    }
  }
}
</script>

<style scoped>
.shop-detail {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.shop-header {
  background: white;
  margin-bottom: 30px;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.shop-back {
  padding: 20px 30px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  color: #666;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.shop-back:hover {
  color: #409eff;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
}

.shop-hero {
  display: flex;
  padding: 40px;
  gap: 30px;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.shop-hero-image {
  width: 200px;
  height: 150px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.2);
}

.shop-hero-content h1 {
  margin: 0 0 15px 0;
  color: white;
  font-size: 32px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.shop-description {
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin: 0;
  font-size: 16px;
  max-width: 600px;
}

.dishes-section {
  background: white;
  margin: 0 auto 30px auto;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  max-width: 1200px;
}

.section-title {
  margin: 0 0 30px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f2f5;
}

.dishes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.dish-card {
  border: 1px solid #f0f2f5;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.dish-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
  border-color: #e1e8ed;
}

.dish-image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  position: relative;
}

.dish-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.dish-card:hover .dish-image {
  transform: scale(1.05);
}

.dish-content {
  padding: 20px;
}

.dish-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.dish-name {
  margin: 0;
  color: #303133;
  font-size: 18px;
  line-height: 1.4;
  flex: 1;
  font-weight: 600;
}

.dish-price {
  color: #ff6b35;
  font-weight: 700;
  font-size: 20px;
  margin-left: 15px;
}

.dish-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dish-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dish-sales {
  color: #909399;
  font-size: 13px;
  font-weight: 500;
}

.add-cart-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.add-cart-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.cart-float {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 1000;
}

.cart-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 18px 25px;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 16px;
}

.cart-button:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
}

.cart-total {
  font-weight: 700;
}

.cart-dialog {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

.cart-items {
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.3s ease;
}

.cart-item:hover {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px 15px;
  margin: 0 -15px;
}

.item-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.item-price {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.item-subtotal {
  color: #ff6b35;
  font-weight: 600;
  font-size: 16px;
}

.cart-summary {
  border-top: 2px solid #f0f2f5;
  padding-top: 20px;
  margin-top: 10px;
}

.total-amount {
  text-align: right;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.total-amount .amount {
  color: #ff6b35;
  font-weight: 700;
  font-size: 28px;
}

.empty-cart {
  padding: 60px 0;
}

.form-display-text {
  font-weight: 600;
  color: #303133;
}

.form-display-text.price {
  color: #ff6b35;
  font-size: 20px;
  font-weight: 700;
}

.loading-container {
  padding: 60px 0;
}

.empty-state {
  padding: 80px 0;
}

.dialog-footer {
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
}

.checkout-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.checkout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* 下单对话框样式 */
.order-dialog {
  padding: 10px 0;
}

.order-summary {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.order-summary .shop-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
}

.amount-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-info .label {
  font-size: 16px;
  color: #606266;
}

.amount-info .price {
  color: #ff6b35;
  font-size: 24px;
  font-weight: 700;
}

.address-section {
  margin-bottom: 25px;
}

.address-section .section-title {
  text-align: left;
  font-size: 18px;
  margin: 0 0 15px 0;
  padding: 0;
  border: none;
}

.address-tabs {
  margin-bottom: 20px;
}

.address-selector .no-address {
  padding: 40px 0;
}

.address-list {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 10px;
}

.address-item {
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.address-item:hover {
  border-color: #c3cfe2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.address-item.selected {
  border-color: #409eff;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(64, 158, 255, 0.1) 100%);
}

.address-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.address-tags {
  display: flex;
  gap: 8px;
}

.default-tag {
  font-size: 12px;
  padding: 2px 6px;
}

.address-actions .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

.consignee-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.consignee-info .name {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.consignee-info .phone {
  color: #666;
  font-size: 14px;
}

.address-detail {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.address-detail i {
  margin-right: 8px;
  color: #36d1dc;
}

.address-form-container {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.region-selector {
  display: flex;
  justify-content: space-between;
}

.delivery-section {
  margin-bottom: 25px;
}

.delivery-section .section-title {
  text-align: left;
  font-size: 18px;
  margin: 0 0 15px 0;
  padding: 0;
  border: none;
}

.remark-section {
  margin-bottom: 20px;
}

.remark-section .section-title {
  text-align: left;
  font-size: 18px;
  margin: 0 0 10px 0;
  padding: 0;
  border: none;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .dishes-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .shop-detail {
    padding: 10px;
  }

  .dishes-section {
    margin: 0 10px 20px 10px;
    padding: 25px;
  }

  .shop-hero {
    flex-direction: column;
    text-align: center;
    padding: 30px 20px;
  }

  .shop-hero-image {
    width: 100%;
    max-width: 250px;
    height: 180px;
  }

  .shop-hero-content h1 {
    font-size: 24px;
  }

  .dishes-grid {
    grid-template-columns: 1fr;
  }

  .cart-float {
    right: 15px;
    bottom: 15px;
  }

  .cart-button {
    padding: 15px 20px;
    font-size: 14px;
  }

  /* 响应式地址选择器 */
  .region-selector {
    flex-direction: column;
    gap: 10px;
  }

  .region-selector .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }
}

@media (max-width: 480px) {
  .shop-hero {
    padding: 20px 15px;
  }

  .shop-hero-image {
    max-width: 200px;
    height: 150px;
  }

  .dishes-section {
    padding: 20px;
  }

  .dish-content {
    padding: 15px;
  }

  .dish-name {
    font-size: 16px;
  }

  .dish-price {
    font-size: 18px;
  }
}

/* 对话框样式 */
::v-deep .custom-dialog .el-dialog {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

::v-deep .custom-dialog .el-dialog__header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

::v-deep .custom-dialog .el-dialog__title {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

::v-deep .custom-dialog .el-dialog__headerbtn {
  top: 20px;
}

::v-deep .custom-dialog .el-dialog__headerbtn .el-dialog__close {
  color: white;
}

::v-deep .custom-dialog .el-dialog__body {
  padding: 30px;
}
</style>