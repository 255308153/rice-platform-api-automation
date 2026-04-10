# test_rice_platform_api

轻量级接口自动化测试骨架，基于 `pytest + requests`，用于助农大米平台 API 回归。
最近一次本地执行统计见：`EXECUTION_RESULT.md`。
当前持续维护核心接口自动化用例，支持本地回归与 CI 冒烟执行。

## 目录结构

```text
test_rice_platform_api/
├── clients/
│   ├── api_client.py
│   └── db_client.py
├── schemas/
│   ├── auth_login_success.json
│   ├── products_list_success.json
│   └── user_info_success.json
├── testcase/
│   ├── test_addresses.py
│   ├── test_ai_health.py
│   ├── test_ai_extended.py
│   ├── test_admin_content.py
│   ├── test_admin_extended.py
│   ├── test_admin_write_ops.py
│   ├── test_auth_login.py
│   ├── test_admin_permissions.py
│   ├── test_merchant_access.py
│   ├── test_messages.py
│   ├── test_order_guards.py
│   ├── test_orders.py
│   ├── test_posts.py
│   ├── test_posts_interaction.py
│   ├── test_products.py
│   ├── test_shops.py
│   └── test_user_info.py
├── testdata/
│   └── auth_login_cases.yaml
├── utils/
│   ├── data_loader.py
│   └── schema.py
├── config.py
├── conftest.py
├── pytest.ini
├── requirements.txt
└── .env.example
```

## 快速开始

1. 安装依赖

```bash
cd /Users/lqc/Downloads/deploy_web_bundle_20260318_副本/test_rice_platform_api
python3 -m pip install -r requirements.txt
```

2. 准备环境变量

```bash
cp .env.example .env
```

3. 启动后端服务（默认 `http://localhost:8080`）

4. 运行用例

```bash
python3 -m pytest
```

## 当前覆盖

- `POST /api/auth/login`：登录成功/异常登录（JSON Schema 契约校验）
- 登录异常场景使用 `YAML` 数据驱动
- `GET /api/user/info`：未登录拦截、登录后用户信息查询（JSON Schema 契约校验）
- `GET /api/products`：商品列表查询与分页字段校验（JSON Schema 契约校验）
- `GET /api/orders`：订单列表查询基础校验
- `GET /api/orders/page`、`GET /api/orders/refunds`：分页与退款记录查询
- `PUT /api/orders/{id}/pay`、`POST /api/orders/{id}/refund`：异常路径守卫校验（不存在订单）
- `GET /api/addresses`、`POST /api/addresses`、`DELETE /api/addresses/{id}`：地址列表与增删回归
- `GET /api/posts`、`GET /api/posts/categories`：论坛列表与分类查询
- `GET /api/shops`：店铺列表与详情（已恢复强断言）
- `GET /api/ai/chat/health`、`GET /api/ai/recognition/health`：AI 服务健康检查
- `POST /api/ai/chat`、`GET /api/ai/chat/history`、`GET /api/ai/recognition/history`：AI 会话与历史查询
- `GET /api/admin/users`：多角色权限校验（USER 拒绝、ADMIN 允许）
- `GET /api/admin/content/posts`、`GET /api/admin/content/comments`：管理员内容审核
- `GET /api/admin/forum/categories`、`GET /api/admin/notices`、`GET /api/admin/monitor/overview`：管理员配置与总览
- `PUT /api/admin/config`、`GET /api/admin/config/{key}`：管理员配置写入与回读验证
- `POST /api/admin/notices`、`DELETE /api/admin/notices/{id}`：公告创建与删除回归
- `GET /api/merchant/orders`、`GET /api/merchant/refunds`：商户角色接口访问校验（含 USER/ADMIN 拒绝）
- `GET /api/messages/contacts`、`GET /api/conversations`、`GET/PUT /api/conversations/preferences`：消息中心查询与偏好配置
- `POST /api/messages`：消息参数校验
- `GET /api/posts/favorites`、`POST /api/posts/{id}/like`、`POST /api/posts/{id}/favorite`：帖子互动链路回归
- `GET /api/user/info` + MySQL：接口返回与数据库一致性校验

## 常用命令

```bash
# 全量执行
python3 -m pytest

# 仅跑冒烟用例
python3 -m pytest -m smoke

# 生成 Allure 原始结果
python3 -m pytest --alluredir=allure-results

# 指定本地环境变量执行（示例）
RICE_API_BASE_URL=http://localhost:8088 \
RICE_API_USER_USERNAME=xxx \
RICE_API_USER_PASSWORD=xxx \
RICE_API_ADMIN_USERNAME=xxx \
RICE_API_ADMIN_PASSWORD=xxx \
RICE_API_MERCHANT_USERNAME=xxx \
RICE_API_MERCHANT_PASSWORD=xxx \
python3 -m pytest -m smoke
```

## CI（GitHub Actions）

项目内置工作流：`.github/workflows/api-smoke.yml`，用于自动执行 smoke 用例并上传 `allure-results` 产物。  
在仓库 `Settings -> Secrets and variables -> Actions` 中配置以下密钥：

- `RICE_API_BASE_URL`
- `RICE_API_USER_USERNAME`
- `RICE_API_USER_PASSWORD`
- `RICE_API_ADMIN_USERNAME`
- `RICE_API_ADMIN_PASSWORD`
- `RICE_API_MERCHANT_USERNAME`（可选）
- `RICE_API_MERCHANT_PASSWORD`（可选）

### self-hosted Runner 使用说明

当前工作流已切换为 `runs-on: self-hosted`，适合在本机或内网机器直接访问 `http://localhost:8080` 的测试环境。

1. 在 GitHub 仓库进入 `Settings -> Actions -> Runners -> New self-hosted runner`。  
2. 按页面命令在你的机器上安装并启动 Runner（建议常驻运行）。  
3. 确保 Runner 所在机器可访问 `RICE_API_BASE_URL`，并且后端服务、数据库等依赖已启动。  
4. 推送代码到 `main/master`，或在 Actions 页面手动执行 `API Smoke Tests`。  
5. 运行完成后在 Workflow 的 `Artifacts` 下载 `allure-results`，本地执行 `allure serve` 查看报告。

## 近期修复

- 修复后端 `GET /api/products` 分页查询缓存 key 空值场景问题，恢复列表强断言。
- 修复后端 `GET /api/shops` Redis 反序列化类型丢失问题，恢复列表与详情强断言。
- 新增 `shops` 列表 JSON Schema：`schemas/shops_list_success.json`。
- 定向验证通过：`python3 -m pytest -q testcase/test_products.py testcase/test_shops.py`。

## 下一步扩展建议

- 增加下单创建、退款申请、审核处理等“写操作”链路用例
- 补充 CI 环境数据库校验策略（测试库隔离 + 数据回滚）
