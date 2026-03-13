# Contributing Guide / 贡献指南

## 单人项目的 PR 流程说明 / PR Workflow for Solo Developers

**一句话回答：不强制，但推荐。**  
**Short answer: not mandatory, but recommended.**

---

### 为什么单人开发仍值得使用 PR？

| 场景 | 好处 |
|------|------|
| 触发 CI/CD | 每次 push 或 PR 都会自动跑 lint / type-check，不依赖人工审查 |
| 自我 code review | 打开 PR diff 强迫自己以"旁观者视角"重看一遍变更 |
| 变更记录 | PR 标题和描述形成可检索的决策记录，比提交历史更易读 |
| 大功能保护 | 对重要分支（`main` / `v*`）开启 Branch Protection，防止误推送 |

**什么时候可以直接推送（不开 PR）？**

- 文档小改动（typo、注释）
- hotfix（例如修复 404 下载地址）
- 只有你一个人维护且确定不需要 CI 结果再合并

**什么时候建议开 PR？**

- 功能开发（新增模块、新增接口）
- 安全相关变更（认证、密钥、RCON 绑定）
- 涉及多文件重构
- 你想记录"为什么这样做"的场合

---

### 推荐的单人工作流 / Recommended Solo Workflow

```
main (protected)
  └─ feat/xxx     ← 开发新功能，完成后开 PR → CI 通过后 squash merge
  └─ fix/yyy      ← bug 修复，小改可直接 push
  └─ docs/zzz     ← 文档变更，直接 push 即可
```

1. 功能开发时从 `main`（或最新版本分支）切出一个短生命周期分支
2. 完成后推送分支，等待 CI 通过
3. Squash merge 回目标分支，删除功能分支
4. 清理不再需要的临时分支（`demo*`、`test-*` 等）

---

### Commit Message 规范 / Commit Convention

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
type(scope): short description

feat      新功能
fix       Bug 修复
docs      仅文档变更
chore     构建/依赖/工具变更
security  安全相关变更
perf      性能优化
refactor  重构（不改变功能）
test      测试相关
```

示例：
```
feat(wizard): add advanced params modal
fix(bluemap): replace broken v5.15 download URL with v5.16
security(rcon): bind to localhost by default
```

---

### 分支清理建议 / Branch Cleanup

完成合并后请删除功能分支：

```bash
git branch -d feat/xxx          # 删除本地分支
git push origin --delete feat/xxx  # 删除远程分支
```

临时演示分支（`demo*`、`demon*`、`test-*`）在确认不再需要后应及时清理。

---

### 本地开发环境 / Local Dev Setup

```bash
# 后端
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload

# 前端
cd frontend
npm install
npm run dev

# 部署 CLI
python -m deploy.cli --help
```
