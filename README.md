# 👾 Alien Invasion Plus

基于 Pygame 的《外星人入侵》增强版。在《Python 编程：从入门到实践》原版游戏的基础上，大幅扩展了 Boss 战、外星人子弹、护盾、道具掉落、长按自动射击、关卡系统和最高分记录等功能，玩法更接近街机射击游戏。

## ✨ 功能特性

- 🎯 **Boss 战**：关卡中会出现 Boss（`boss.py`），击败后推进关卡
- 🔫 **外星人子弹**：敌人会主动射击，不再是单向躲避（`alien_bullet.py`）
- 🛡️ **护盾系统**：抵挡子弹伤害（`shield.py`）
- 🎁 **道具掉落**：加血等增益道具（`powerup.py`）
- 🔥 **长按自动射击**：按住开火键持续射击
- 📈 **关卡与难度递增**：速度、分值随关卡动态提升（`settings.py`）
- 🏆 **最高分记录**：持久化保存到 `high_score.txt`
- 🔊 **音效系统**：支持音效加载，缺失时自动降级不报错
- 🖥️ **自适应窗口**：窗口可缩放，且自动限制不超过当前屏幕尺寸
- ❤️ **飞船生命值**：飞船带血量（health）设定

## 🚀 快速开始

需要 **Python 3.8+** 和 **Pygame**。

```bash
# 安装依赖
pip install pygame

# 启动游戏
python alien_invasion.py
```

> 仓库暂未提供 `requirements.txt`，建议补充一行：`pygame>=2.0`。

## 🎮 操作说明

| 按键 | 功能 |
|---|---|
| 方向键 | 移动飞船 |
| 空格 | 开火（支持长按连射） |
| SPACE | 游戏结束界面：重新开始 |
| Q | 游戏结束界面：退出 |

> 具体移动/开火键位以实际运行手感为准，欢迎在验证后补充完整键位表。

## 📁 项目结构

```
Alien-Invasion-Plus/
├── alien_invasion.py   # 主程序：游戏循环、事件、碰撞与状态管理
├── settings.py         # 全部游戏参数（速度、分值、窗口等）
├── game_stats.py       # 游戏统计（分数、生命、关卡）
├── scoreboard.py       # 计分板 UI
├── ship.py             # 飞船（移动、开火、生命值）
├── bullet.py           # 玩家子弹
├── alien.py            # 普通外星人
├── alien_bullet.py     # 外星人子弹
├── boss.py             # Boss 逻辑
├── shield.py           # 护盾
├── powerup.py          # 道具掉落
├── button.py           # 开始按钮
├── game_over_screen.py # 游戏结束界面
└── high_score.txt      # 最高分持久化文件
```

## 📌 建议下一步

- [ ] 补充 `requirements.txt`
- [ ] 在 `docs/screenshots/` 放几张游戏截图，README 顶部配图更吸引人
- [ ] 写一份完整的键位说明

## 📄 许可

未指定开源许可（默认保留所有权利）。如需开源，建议选择 MIT License。
