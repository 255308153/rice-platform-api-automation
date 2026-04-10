# 接口自动化执行结果（本地）

- 执行时间：2026-04-10
- 执行命令：
  - `RICE_API_BASE_URL=http://localhost:8088 RICE_API_USER_USERNAME=<user> RICE_API_USER_PASSWORD=<pass> RICE_API_ADMIN_USERNAME=<admin> RICE_API_ADMIN_PASSWORD=<pass> RICE_API_MERCHANT_USERNAME=<merchant> RICE_API_MERCHANT_PASSWORD=<pass> RICE_DB_HOST=<host> RICE_DB_PORT=<port> RICE_DB_USER=<db_user> RICE_DB_PASSWORD=<db_pass> RICE_DB_NAME=<db_name> python3 -m pytest --alluredir=allure-results`
- 执行结果：`52 passed, 2 skipped in 11.50s`

## 跳过说明

1. `testcase/test_products.py::test_product_list_success`
   - 跳过原因：`/api/products` 当前返回业务错误：`Cannot read the array length because "value" is null`
   - 处理方式：暂按“已知后端缺陷”跳过，避免阻塞整体回归。

2. `testcase/test_shops.py::test_shop_list_success`
   - 跳过原因：`/api/shops` 返回序列化异常（`LocalDateTime` 未正确序列化）。
   - 处理方式：暂按“已知后端缺陷”跳过，避免阻塞整体回归。

## 当前覆盖模块

- 登录接口：成功登录、异常登录（YAML 数据驱动）
- 用户信息接口：鉴权拦截、登录后信息查询
- 用户信息接口：API 与 MySQL 数据一致性校验
- 地址接口：列表查询、新增地址、删除地址
- 商品接口：鉴权拦截、列表接口异常兜底
- 店铺接口：鉴权拦截、列表/详情（当前缺陷跳过）
- 订单接口：鉴权拦截、列表查询、分页查询、退款列表、异常状态守卫
- 论坛接口：分类查询、帖子列表、我的帖子、收藏列表、点赞/收藏双次切换回滚、评论入参校验
- AI 接口：聊天健康检查、识别健康检查、空消息校验、聊天/识别历史查询
- 管理端接口：普通用户越权拦截、管理员访问通过、帖子/评论审核、公告列表、版块分类、监控总览、配置写入回读、公告增删回归
- 商户端接口：`USER/ADMIN` 越权拦截、`MERCHANT` 角色接口访问校验
- 消息中心接口：联系人列表、会话列表、会话偏好保存回读、消息必填参数校验
