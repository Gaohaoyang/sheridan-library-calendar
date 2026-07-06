# Sheridan Library 家庭活动日历

**在线访问：<https://gaohaoyang.github.io/sheridan-library-calendar/>**

一个自包含的静态页面，把 [ActiveMississauga 活动搜索](https://anc.ca.apm.activecommunities.com/activemississauga/activity/search?onlineSiteId=0&activity_select_param=2&center_ids=46&min_age=0&activity_department_ids=5&max_age=6&viewMode=list)（Sheridan Library / 0–6 岁 / Library 部门）里的全部活动整理成日历。长期使用：数据每天自动同步，换季后新活动会自然进入日历。

## 功能

- **桌面**：月份 tab + 月历网格，每场活动显示起止时间、名称和一行中文简介
- **手机**（≤720px）：整季活动一条按天排列的长列表，月份标题吸顶，打开自动定位到今天
- 点击活动块 / 图例弹出详情面板：中英文简介、时间、地点、名额、全部场次日期（图书馆盖章样式：灰 = 已过、蓝实心 = 今天、红划掉 = 闭馆跳过）
- 详情面板有独立 URL（`?activity=<活动ID>`），可分享收藏，浏览器返回键关闭面板
- 面板内一键**分享链接**、**加入 Google 日历**（周期活动带 RRULE）、**加入 Apple 日历**（.ics 文件，含时区、每周重复和闭馆 EXDATE）
- 弹窗打开时背景锁定不可滚动；支持键盘 Esc 关闭、reduced-motion
- **实时核对**：页面加载后通过公共 CORS 代理（corsproxy.io → allorigins.win）转发官方 GET 接口，后台刷新名额与日期；代理不可用时静默退回内嵌快照

## 数据更新

- **自动**：GitHub Actions（[.github/workflows/update-data.yml](.github/workflows/update-data.yml)）每天多伦多时间早上 6 点左右跑一次 `update.py`，数据有变化才提交；也可在 Actions 页手动触发
- **手动**：`python3 update.py`（只用 Python 标准库）

脚本依次调用官方接口：`POST /rest/activities/list`（按条件搜索）→ `GET /rest/activity/detail/{id}`（详情）→ `GET /rest/activity/detail/meetingandregistrationdates/{id}`（场次与闭馆例外），然后把数据回写到 `index.html` 的 `/*__DATA_START__*/ ... /*__DATA_END__*/` 标记之间。中文简介（`ZH_BRIEF`）和配色（`COLORS`）是手写的，位于标记外不会被覆盖；出现新活动时脚本会提示补写。

> 为什么页面不直接实时拉官方接口？接口不返回 CORS 头（GET 无 `Access-Control-Allow-Origin`，POST 预检 403），也不支持 JSONP，浏览器同源策略挡住了静态页面的直接请求，所以用 CI 定时抓取 + 公共代理实时核对的组合。

## 起源

最初开发于 [weekRecord](https://github.com/zhuyingying/joe-s-note) 仓库的 `activities/sheridan-library/` 目录，为发布 GitHub Pages 迁移至独立仓库。
