# WB-3DGS 上传 GitHub 操作指南（Windows 10）

## 0. 上传前先完成三件事

1. 打开 `RELEASE_AUDIT.md`，把 `REQUIRED_FROM_AUTHORS` 项从原始代码、训练
   log 和工作站环境中补齐。
2. 把至少一个真实 30,000-iteration checkpoint 放到发布位置，并填写
   `checkpoints/checkpoint_manifest.example.yaml` 的 SHA256、source commit、split
   manifest 和真实 training seed。
3. 确认 `DATA_AVAILABILITY.md` 中的数据限制原因经过作者/单位确认。不要为了
   写 Data Availability 自行假设“隐私/商业/合同限制”。

## 1. 建议的 GitHub 仓库名

`WB-3DGS`

Description 可写：

> Official implementation and reproducibility resources for WB-3DGS: wind-aware dynamic 3D Gaussian Splatting for banana reconstruction and phenotyping.

首次创建仓库时先不要在线勾选 `Add a README`、`.gitignore` 或 License，因为
本地文件已经准备好，避免第一次 push 产生不必要的历史冲突。

## 2. Windows 安装 Git / Git LFS

安装 Git for Windows 后，在 Git Bash 中：

```bash
git --version
git lfs install
git config --global user.name "YOUR NAME"
git config --global user.email "YOUR EMAIL"
```

## 3. 初始化本地仓库

将本项目文件夹重命名为 `WB-3DGS`，打开 Git Bash：

```bash
cd /c/你的路径/WB-3DGS
git init -b main
git status
git add .
git status
git commit -m "Initial reproducibility release"
```

在执行 `git add .` 前一定确认没有原始受限数据、个人信息、密码、API key、
实验站内部文件或不允许再分发的第三方权重。

## 4. 连接 GitHub 并第一次推送

在 GitHub 网页创建空仓库后复制 URL：

```bash
git remote add origin https://github.com/YOUR-ACCOUNT/WB-3DGS.git
git remote -v
git push -u origin main
```

如果你使用 SSH：

```bash
git remote set-url origin git@github.com:YOUR-ACCOUNT/WB-3DGS.git
git push -u origin main
```

## 5. checkpoint / 大文件怎么放

不要把几百 MB 的 `.pth/.pt/.ckpt` 当普通 Git 文件提交。本仓库的
`.gitattributes` 已为常见权重和 PCD 类型准备了 Git LFS 规则。

```bash
git lfs track "*.pth" "*.pt" "*.ckpt" "*.safetensors" "*.pcd"
git add .gitattributes
git add checkpoints/wb3dgs_seq14_plant18_iter30000.pth
git commit -m "Add minimal reproducibility checkpoint"
git push
```

也可以把 checkpoint 放到 GitHub **Releases**，仓库只提交
`checkpoint_manifest.yaml`、下载说明和 SHA256。对论文复现我更推荐这种方式，
因为代码历史会更轻。

计算 SHA256（Windows PowerShell）：

```powershell
Get-FileHash .\checkpoints\wb3dgs_seq14_plant18_iter30000.pth -Algorithm SHA256
```

## 6. 数据不能全部公开时怎么放

仓库中公开：

- 三个代表性 case：Seq-02/Plant-15、Seq-08/Plant-05、Seq-14/Plant-18；
- 对应 split manifest；
- 可公开的 RGB / LiDAR 子集；
- semantic reference mask / pseudo-label；
- 叶片实例审计记录（去标识）；
- 相机/雷达标定“格式”和允许公开的数值；
- manual measurement schema / 合法可公开的标注；
- 所有预处理和评价代码；
- 最小 checkpoint。

完整原始数据若受单位/合同/隐私/商业条件限制，可通过“reasonable request +
适用的数据使用条件”提供，但原因必须是真实且可证明的。GitHub 只负责代码和小型
代表子集；大规模数据更适合存入 Zenodo、Figshare、机构数据仓库等并在 README
给 DOI/永久链接。

## 7. 每次更新的标准流程

```bash
git status
git diff
git add 具体文件名
git commit -m "Describe the change"
git push
```

不要习惯性 `git add .` 后直接 push；论文复现仓库中最需要避免的是把受限原始数据
或密钥意外提交。

## 8. 投稿/返修时建议固定一个 release

当代码、配置、代表性数据和 checkpoint 都核对完后：

```bash
git tag -a v1.0-paper -m "Code and configs corresponding to the revised manuscript"
git push origin v1.0-paper
```

然后在 GitHub 创建 Release，并在 rebuttal/论文 Data & Code Availability 中引用
这个固定版本。若之后继续开发，不要改掉这个 tag 对应的历史。

## 9. README 首页最终应让审稿人一眼看到

- `Quick start`
- `Data structure`
- `Exact experiment configs`
- `Preprocessing`
- `Train / Evaluate / Phenotype commands`
- `Checkpoint`
- `Data availability`
- `Hardware & runtime`
- `License`
- `Citation`

## 10. 正式公开前最后检查

```bash
rg -n "REQUIRED_FROM_AUTHORS|TODO|PRIVATE|PASSWORD|TOKEN|SECRET" .
git status
```

并在一台“没有你的私人路径和环境变量”的干净机器上至少完成：安装、split
生成、预处理小样本、metric 单元测试和 checkpoint 推理。

