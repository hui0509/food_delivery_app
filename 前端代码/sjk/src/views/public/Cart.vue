<template>
  <div class="cart-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1><i class="el-icon-shopping-cart-2"></i> 我的购物车</h1>
      <p>确认您的订单信息</p>
    </div>

    <div class="cart-content">
      <!-- 购物车为空状态 -->
      <div v-if="cartItems.length === 0 && !loading" class="empty-cart">
        <div class="empty-icon">
          <i class="el-icon-shopping-cart-1"></i>
        </div>
        <h3>购物车空空如也</h3>
        <p>快去挑选心仪的美食吧～</p>
        <el-button type="primary" size="medium" @click="goToShopList">
          <i class="el-icon-shopping-bag-1"></i> 去逛逛
        </el-button>
      </div>

      <!-- 购物车内容 -->
      <div v-else class="cart-body">
        <!-- 购物车列表 -->
        <div class="cart-list">
          <div class="cart-header">
            <h3>购物车商品</h3>
            <el-button
              type="text"
              @click="clearCart"
              :disabled="cartItems.length === 0"
              class="clear-btn">
              <i class="el-icon-delete"></i> 清空购物车
            </el-button>
          </div>

          <div class="cart-items">
            <div
              v-for="(item, index) in cartItems"
              :key="item.cart_id"
              class="cart-item"
              :class="{ 'last-item': index === cartItems.length - 1 }">

              <!-- 菜品图片和基本信息 -->
              <div class="item-info">
                <el-avatar
                  :src="item.image_url"
                  :size="60"
                  shape="square"
                  class="dish-image">
                </el-avatar>
                <div class="dish-details">
                  <h4 class="dish-name">{{ item.dish_name }}</h4>
                  <p class="shop-name">{{ item.shop_name }}</p>
                  <p class="dish-price">¥{{ item.price }}</p>
                </div>
              </div>

              <!-- 数量控制 -->
              <div class="quantity-control">
                <el-button
                  size="mini"
                  :disabled="item.quantity <= 1"
                  @click="updateQuantity(item.cart_id, item.quantity - 1)"
                  class="quantity-btn">
                  <i class="el-icon-minus"></i>
                </el-button>

                <el-input-number
                  v-model="item.quantity"
                  :min="1"
                  :max="99"
                  size="mini"
                  controls-position="right"
                  @change="(val) => updateQuantity(item.cart_id, val)"
                  class="quantity-input">
                </el-input-number>

                <el-button
                  size="mini"
                  @click="updateQuantity(item.cart_id, item.quantity + 1)"
                  class="quantity-btn">
                  <i class="el-icon-plus"></i>
                </el-button>
              </div>

              <!-- 小计和删除 -->
              <div class="item-actions">
                <div class="subtotal">
                  ¥{{ (item.price * item.quantity).toFixed(2) }}
                </div>
                <el-button
                  type="text"
                  size="mini"
                  @click="removeItem(item.cart_id)"
                  class="delete-btn">
                  <i class="el-icon-delete"></i>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 订单汇总 -->
        <div class="order-summary">
          <div class="summary-card">
            <h3>订单汇总</h3>

            <div class="summary-details">
              <div class="summary-row">
                <span>商品总价</span>
                <span>¥{{ totalAmount.toFixed(2) }}</span>
              </div>
              <div class="summary-row">
                <span>配送费</span>
                <span>¥{{ deliveryFee.toFixed(2) }}</span>
              </div>
              <div class="summary-row discount">
                <span>优惠</span>
                <span>-¥{{ discount.toFixed(2) }}</span>
              </div>
              <el-divider></el-divider>
              <div class="summary-row total">
                <span>实付金额</span>
                <span class="final-amount">¥{{ finalAmount.toFixed(2) }}</span>
              </div>
            </div>

            <!-- 下单按钮 -->
            <div class="checkout-actions">
              <el-button
                type="primary"
                size="large"
                @click="showOrderDialog = true"
                :loading="checkoutLoading"
                class="checkout-btn">
                <i class="el-icon-shopping-cart-2"></i>
                立即下单 (¥{{ finalAmount.toFixed(2) }})
              </el-button>

              <p class="checkout-tips">
                <i class="el-icon-info"></i>
                请确认商品信息无误后再下单
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 下单对话框 -->
    <el-dialog
      title="确认订单"
      :visible.sync="showOrderDialog"
      width="600px"
      :close-on-click-modal="false"
      class="custom-dialog">
      <div class="order-dialog">
        <!-- 订单金额 -->
        <div class="order-summary">
          <div class="amount-info">
            <span class="label">订单金额：</span>
            <span class="price">¥{{ finalAmount.toFixed(2) }}</span>
          </div>
        </div>

        <!-- 地址选择 -->
        <div class="address-section">
          <h4 class="section-title">选择收货地址</h4>
          <el-tabs v-model="addressTab" @tab-click="(tab) => handleAddressTabChange(tab.paneName)" class="address-tabs">
            <el-tab-pane label="选择现有地址" name="select">
              <div v-if="userAddresses.length === 0" class="address-selector no-address">
                <el-empty description="暂无收货地址">
                  <el-button type="primary" size="small" @click="addressTab = 'new'">添加地址</el-button>
                </el-empty>
              </div>
              <div v-else class="address-selector">
                <div class="address-list">
                  <div
                    v-for="address in userAddresses"
                    :key="address.address_id"
                    class="address-item"
                    :class="{ selected: address.address_id === selectedAddressId }"
                    @click="selectAddress(address.address_id)">
                    <div class="address-header">
                      <div class="address-tags">
                        <el-tag
                          v-if="address.is_default"
                          type="primary"
                          size="small"
                          effect="plain"
                          class="default-tag">默认</el-tag>
                        <el-tag
                          :type="getAddressLabelColor(address.address_label)"
                          size="small"
                          effect="plain">
                          {{ getAddressLabelText(address.address_label) }}
                        </el-tag>
                      </div>
                      <div class="address-actions">
                        <el-button
                          v-if="!address.is_default"
                          type="text"
                          size="small"
                          @click.stop="setDefaultAddress(address.address_id)">
                          设为默认
                        </el-button>
                      </div>
                    </div>
                    <div class="consignee-info">
                      <span class="name">{{ address.cons_name }}</span>
                      <span class="phone">{{ address.cons_phone }}</span>
                    </div>
                    <div class="address-detail">
                      <i class="el-icon-location-outline"></i>
                      {{ address.province }}{{ address.city }}{{ address.district }}{{ address.street }}
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="新建收货地址" name="new">
              <el-form
                ref="newAddressForm"
                :model="newAddressForm"
                :rules="addressRules"
                label-width="100px" class="address-form-container">
                <el-form-item label="收货人" prop="cons_name">
                  <el-input v-model="newAddressForm.cons_name" placeholder="请输入收货人姓名" maxlength="10" show-word-limit></el-input>
                </el-form-item>
                <el-form-item label="联系电话" prop="cons_phone">
                  <el-input v-model="newAddressForm.cons_phone" placeholder="请输入联系电话" maxlength="11" show-word-limit></el-input>
                </el-form-item>
                <el-form-item label="所在地区">
                  <div class="region-selector">
                    <el-select
                      v-model="newAddressForm.province"
                      placeholder="省份"
                      @change="handleProvinceChange"
                      style="width: 31%; margin-right: 1%;">
                      <el-option
                        v-for="province in provinceOptions"
                        :key="province.value"
                        :label="province.label"
                        :value="province.value">
                      </el-option>
                    </el-select>
                    <el-select
                      v-model="newAddressForm.city"
                      placeholder="城市"
                      @change="handleCityChange"
                      style="width: 31%; margin-right: 1%;">
                      <el-option
                        v-for="city in cityOptions"
                        :key="city.value"
                        :label="city.label"
                        :value="city.value">
                      </el-option>
                    </el-select>
                    <el-select
                      v-model="newAddressForm.district"
                      placeholder="区县"
                      style="width: 35%;">
                      <el-option
                        v-for="district in districtOptions"
                        :key="district.value"
                        :label="district.label"
                        :value="district.value">
                      </el-option>
                    </el-select>
                  </div>
                </el-form-item>
                <el-form-item label="详细地址" prop="street">
                  <el-input
                    v-model="newAddressForm.street"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入详细地址"
                    maxlength="100"
                    show-word-limit>
                  </el-input>
                </el-form-item>
                <el-form-item label="地址标签">
                  <el-radio-group v-model="newAddressForm.address_label">
                    <el-radio-button label="home">家</el-radio-button>
                    <el-radio-button label="company">公司</el-radio-button>
                    <el-radio-button label="school">学校</el-radio-button>
                    <el-radio-button label="other">其他</el-radio-button>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-checkbox v-model="newAddressForm.is_default">设为默认地址</el-checkbox>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveNewAddress">保存地址</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 配送方式 -->
        <div class="delivery-section">
          <h4 class="section-title">配送方式</h4>
          <el-radio-group v-model="orderForm.order_way">
            <el-radio label="自提">自提</el-radio>
            <el-radio label="网上订餐">外卖配送</el-radio>
          </el-radio-group>
        </div>

        <!-- 备注 -->
        <div class="remark-section">
          <h4 class="section-title">备注</h4>
          <el-input
            v-model="orderForm.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
            maxlength="100"
            show-word-limit>
          </el-input>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="showOrderDialog = false" class="cancel-btn">取消</el-button>
        <el-button
          type="primary"
          @click="submitOrder"
          :loading="submitting"
          class="submit-btn">
          提交订单
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ShoppingCart',
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
      cartItems: [],
      loading: false,
      checkoutLoading: false,
      submitting: false,
      showOrderDialog: false,
      deliveryFee: 3.00, // 配送费
      discount: 0.00, // 优惠金额
      orderForm: {
        order_way: '网上订餐',
        remark: ''
      },
      orderRules: {
        cons_name: [
          { required: true, message: '请输入客户姓名', trigger: 'blur' },
          { min: 2, max: 10, message: '姓名长度在 2 到 10 个字符', trigger: 'blur' }
        ],
        cons_addre: [
          { required: true, message: '请输入送餐地址', trigger: 'blur' },
          { min: 5, max: 50, message: '地址长度在 5 到 50 个字符', trigger: 'blur' }
        ],
        order_way: [
          { required: true, message: '请选择订餐方式', trigger: 'change' }
        ]
      },
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
      // 地址验证规则
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
      }
    }
  },
  computed: {
    // 计算商品总价
    totalAmount() {
      return this.cartItems.reduce((total, item) => {
        return total + (item.price * item.quantity)
      }, 0)
    },
    // 计算最终金额
    finalAmount() {
      return Math.max(0, this.totalAmount + this.deliveryFee - this.discount)
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
        this.addressTab = 'select'
        this.loadUserAddresses()
      }
    }
  },
  created() {
    this.getCartItems()
  },
  methods: {
    
    // 获取购物车数据
    async getCartItems() {
      this.loading = true
      try {
        const res = await this.$axios.get("/api/cart")
        if (res.data.status === 200) {
          this.cartItems = res.data.data.items || []
          console.log("购物车数据:", this.cartItems)
        } else {
          this.$message.error('获取购物车失败')
        }
      } catch (error) {
        console.error('获取购物车失败:', error)
        this.$message.error('网络错误，请稍后重试')
      } finally {
        this.loading = false
      }
    },

    // 更新商品数量
    async updateQuantity(cartId, newQuantity) {
      if (newQuantity < 1) return

      try {
        const res = await this.$axios.post("/api/cart/update", {
          cart_id: cartId,
          quantity: newQuantity
        })

        if (res.data.status === 200) {
          // 更新本地数据
          const item = this.cartItems.find(item => item.cart_id === cartId)
          if (item) {
            item.quantity = newQuantity
          }
          this.$message.success('数量更新成功')
        } else {
          this.$message.error('更新失败')
          // 重新获取数据
          this.getCartItems()
        }
      } catch (error) {
        console.error('更新数量失败:', error)
        this.$message.error('更新失败')
        this.getCartItems()
      }
    },

    // 删除商品
    async removeItem(cartId) {
      try {
        const result = await this.$confirm('确定要删除这个商品吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        if (result) {
          const res = await this.$axios.post("/api/cart/remove", {
            cart_id: cartId
          })

          if (res.data.status === 200) {
            this.$message.success('删除成功')
            // 从本地数据中移除
            this.cartItems = this.cartItems.filter(item => item.cart_id !== cartId)
          } else {
            this.$message.error('删除失败')
          }
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除商品失败:', error)
          this.$message.error('删除失败')
        }
      }
    },

    // 清空购物车（带确认对话框）
    async clearCart() {
      try {
        const result = await this.$confirm('确定要清空购物车吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        if (result) {
          await this.clearCartSilently()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('清空购物车失败:', error)
          this.$message.error('清空失败')
        }
      }
    },

    // 静默清空购物车（无确认对话框）
    async clearCartSilently() {
      try {
        const res = await this.$axios.post("/api/cart/clear")

        if (res.data.status === 200) {
          this.cartItems = []
        } else {
          this.$message.error('清空失败')
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
        this.resetNewAddressForm()
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

          this.resetNewAddressForm()
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
          this.clearCartSilently()
          this.resetOrderForm()
          // 提示用户
          this.$confirm('订单创建成功！是否查看订单详情？', '提示', {
            confirmButtonText: '查看订单',
            cancelButtonText: '继续购物',
            type: 'success'
          }).then(() => {
            this.$router.push('/orders')
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
      this.resetNewAddressForm()
    },

    // 重置地址表单
    resetNewAddressForm() {
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

    // 去店铺列表
    goToShopList() {
      this.$router.push('/shops')
    }
  }
}
</script>

<style scoped>
.cart-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

/* 页面标题 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 40px;
  border-radius: 16px;
  text-align: center;
  margin-bottom: 30px;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 16px;
}

/* 购物车内容布局 */
.cart-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* 空购物车状态 */
.empty-cart {
  background: white;
  border-radius: 16px;
  padding: 80px 40px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 80px;
  color: #dcdfe6;
  margin-bottom: 20px;
}

.empty-cart h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
}

.empty-cart p {
  margin: 0 0 30px 0;
  color: #909399;
  font-size: 16px;
}

/* 购物车主体布局 */
.cart-body {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
  align-items: start;
}

/* 购物车列表 */
.cart-list {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f2f5;
}

.cart-header h3 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.clear-btn {
  color: #f56c6c !important;
  font-size: 14px;
}

.clear-btn:hover {
  color: #e64545 !important;
}

/* 购物车商品项 */
.cart-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 20px;
  align-items: center;
  padding: 25px 0;
  border-bottom: 1px solid #f0f2f5;
}

.cart-item.last-item {
  border-bottom: none;
}

/* 商品信息 */
.item-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.dish-image {
  border-radius: 8px;
}

.dish-details {
  flex: 1;
}

.dish-name {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.shop-name {
  margin: 0 0 5px 0;
  color: #909399;
  font-size: 14px;
}

.dish-price {
  margin: 0;
  color: #ff6b35;
  font-size: 16px;
  font-weight: 600;
}

/* 数量控制 */
.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
}

.quantity-input {
  width: 80px;
}

::v-deep .quantity-input .el-input__inner {
  text-align: center;
}

/* 商品操作 */
.item-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.subtotal {
  color: #ff6b35;
  font-size: 18px;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
}

.delete-btn {
  color: #909399 !important;
  font-size: 18px;
}

.delete-btn:hover {
  color: #f56c6c !important;
}

/* 订单汇总 */
.order-summary {
  position: sticky;
  top: 20px;
}

.summary-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.summary-card h3 {
  margin: 0 0 25px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f2f5;
}

.summary-details {
  margin-bottom: 25px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  color: #606266;
  font-size: 15px;
}

.summary-row.discount {
  color: #67c23a;
}

.summary-row.total {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.final-amount {
  color: #ff6b35;
  font-size: 24px;
}

::v-deep .el-divider {
  margin: 15px 0;
}

/* 下单按钮 */
.checkout-actions {
  text-align: center;
}

.checkout-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.checkout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.checkout-tips {
  margin: 0;
  color: #909399;
  font-size: 13px;
  text-align: center;
}

.checkout-tips i {
  margin-right: 5px;
}

/* 表单样式 */
.form-display-text {
  font-weight: 600;
  color: #333;
}

.form-display-text.price {
  color: #ff6b35;
  font-size: 20px;
  font-weight: 700;
}

/* 加载状态 */
.loading-container {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

/* 对话框底部按钮优化 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  color: #606266;
  background: white;
  transition: all 0.3s ease;
  font-weight: 500;
}

.cancel-btn:hover {
  border-color: #c0c4cc;
  background-color: #f5f7fa;
  color: #606266;
  transform: translateY(-1px);
}

.submit-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 订单对话框样式 */
.order-dialog {
  padding: 10px 0;
}

.order-summary {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.order-summary .amount-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-summary .amount-info .label {
  font-size: 16px;
  color: #606266;
}

.order-summary .amount-info .price {
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
  gap: 10px;
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

/* 自定义对话框样式 */
::v-deep .custom-dialog .el-dialog {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

::v-deep .custom-dialog .el-dialog__header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 30px;
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
  font-size: 18px;
}

::v-deep .custom-dialog .el-dialog__body {
  padding: 30px;
}

::v-deep .custom-dialog .el-form-item__label {
  color: #606266;
  font-weight: 600;
}

::v-deep .custom-dialog .el-input__inner,
::v-deep .custom-dialog .el-textarea__inner {
  border-radius: 8px;
  border: 1px solid #e1e8ed;
  transition: all 0.3s ease;
}

::v-deep .custom-dialog .el-input__inner:focus,
::v-deep .custom-dialog .el-textarea__inner:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

::v-deep .custom-dialog .el-select .el-input__inner:focus {
  border-color: #667eea;
}

/* 响应式调整 */
@media (max-width: 768px) {
  /* 响应式地址选择器 */
  .region-selector {
    flex-direction: column;
    gap: 10px;
  }

  .region-selector .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }

  /* 移动端对话框优化 */
  ::v-deep .custom-dialog .el-dialog {
    width: 90% !important;
    margin-top: 5vh !important;
  }

  ::v-deep .custom-dialog .el-dialog__body {
    padding: 20px;
  }

  ::v-deep .custom-dialog .el-form-item__label {
    padding-bottom: 8px;
  }

  /* 移动端按钮布局优化 */
  .dialog-footer {
    flex-direction: column;
    gap: 10px;
  }

  .cancel-btn,
  .submit-btn {
    width: 100%;
    margin: 0;
  }
}

@media (max-width: 480px) {
  /* 小屏幕对话框优化 */
  ::v-deep .custom-dialog .el-dialog__header {
    padding: 15px 20px;
  }

  ::v-deep .custom-dialog .el-dialog__body {
    padding: 15px;
  }

  ::v-deep .custom-dialog .el-form-item__label {
    width: 80px !important;
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .cart-body {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .order-summary {
    position: static;
  }
}

@media (max-width: 768px) {
  .cart-container {
    padding: 10px;
  }

  .page-header {
    padding: 20px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .cart-list,
  .summary-card {
    padding: 20px;
  }

  .cart-item {
    grid-template-columns: 1fr;
    gap: 15px;
    text-align: center;
  }

  .item-info {
    justify-content: center;
  }

  .item-actions {
    justify-content: center;
  }

  .quantity-control {
    justify-content: center;
  }

  /* 移动端对话框优化 */
  ::v-deep .custom-dialog .el-dialog {
    width: 90% !important;
    margin-top: 5vh !important;
  }

  ::v-deep .custom-dialog .el-dialog__body {
    padding: 20px;
  }

  ::v-deep .custom-dialog .el-form-item__label {
    padding-bottom: 8px;
  }

  /* 移动端按钮布局优化 */
  .dialog-footer {
    flex-direction: column;
    gap: 10px;
  }

  .cancel-btn,
  .submit-btn {
    width: 100%;
    margin: 0;
  }
}

@media (max-width: 480px) {
  .empty-cart {
    padding: 40px 20px;
  }

  .empty-icon {
    font-size: 60px;
  }

  .cart-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
    text-align: center;
  }

  /* 小屏幕对话框优化 */
  ::v-deep .custom-dialog .el-dialog__header {
    padding: 15px 20px;
  }

  ::v-deep .custom-dialog .el-dialog__body {
    padding: 15px;
  }

  ::v-deep .custom-dialog .el-form-item__label {
    width: 80px !important;
  }
}
</style>