# -*- coding: utf-8 -*-
"""
中医世界模型 · 雏形 v0.1：六气能量状态 + 药物偏性向量 + 方剂配伍 + 动态推演
⚠️ 定位：可视化演示/雏形。参数来自四气五味→六气的定性映射规则（中医教材/本草通则），
   未经实测标定；发布/对外时须标注"定性映射、参数可调、未标定"。
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------- 中文字体 ----------
CAND = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"]
for p in CAND:
    if os.path.exists(p):
        font_manager.fontManager.addfont(p)
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=p).get_name()]
        break
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 13

AXES = ["风", "寒", "暑", "湿", "燥", "火"]
QI = {"寒": -2, "凉": -1, "平": 0, "温": 1, "热": 2}

# ---------- 药物库：四气 / 五味 / 归经 / 趋向 / 药力 ----------
D = {
    #  名       气    味           归经           趋向   力
    "麻黄": ("温", "辛",     "肺膀胱", "升浮", 1.3),
    "桂枝": ("温", "辛甘",   "心肺膀胱", "升浮", 1.1),
    "杏仁": ("温", "苦",     "肺大肠", "降",   0.8),
    "甘草": ("平", "甘",     "十二经", "平",   0.7),
    "白芍": ("凉", "酸苦",   "肝脾",  "降",   0.9),
    "生姜": ("温", "辛",     "肺脾胃", "升浮", 0.8),
    "大枣": ("温", "甘",     "脾胃",  "平",   0.6),
    "石膏": ("寒", "辛甘",   "肺胃",  "降",   1.5),
    "知母": ("寒", "苦甘",   "肺胃肾", "降",   1.1),
    "粳米": ("平", "甘",     "脾胃",  "平",   0.4),
    "黄连": ("寒", "苦",     "心肝胃", "降",   1.3),
    "黄芩": ("寒", "苦",     "肺胆",  "降",   1.2),
    "黄柏": ("寒", "苦",     "肾膀胱", "降",   1.1),
    "大黄": ("寒", "苦",     "脾胃大肠", "降", 1.4),
    "芒硝": ("寒", "咸苦",   "胃大肠", "降",   1.1),
    "附子": ("热", "辛甘",   "心肾脾", "升",   1.6),
    "干姜": ("热", "辛",     "脾胃",  "升",   1.3),
    "半夏": ("温", "辛",     "脾胃肺", "降",   1.0),
    "茯苓": ("平", "甘淡",   "心脾肾", "降",   0.8),
    "白术": ("温", "苦甘",   "脾胃",  "升",   0.9),
    "泽泻": ("寒", "甘淡",   "肾膀胱", "降",   0.9),
    "猪苓": ("平", "甘淡",   "肾膀胱", "降",   0.8),
    "滑石": ("寒", "甘淡",   "膀胱",  "降",   0.9),
    "藿香": ("温", "辛",     "脾胃肺", "升浮", 1.0),
    "紫苏": ("温", "辛",     "肺脾",  "升浮", 0.9),
    "白芷": ("温", "辛",     "肺胃",  "升浮", 0.9),
    "厚朴": ("温", "苦辛",   "脾胃肺", "降",   1.0),
    "苍术": ("温", "苦辛",   "脾胃",  "升",   1.0),
    "砂仁": ("温", "辛",     "脾胃肾", "升浮", 0.8),
    "柴胡": ("凉", "辛苦",   "肝胆",  "升浮", 1.1),
    "薄荷": ("凉", "辛",     "肺肝",  "升浮", 0.8),
    "连翘": ("寒", "苦",     "心肺胆", "降",   1.0),
    "人参": ("温", "甘",     "脾肺",  "升",   1.2),
    "黄芪": ("温", "甘",     "脾肺",  "升",   1.1),
    "熟地": ("温", "甘",     "肝肾",  "降",   1.2),
    "山茱萸": ("温", "酸",   "肝肾",  "降",   0.9),
    "山药": ("平", "甘",     "脾肺肾", "平",   0.7),
    "丹皮": ("凉", "苦辛",   "心肝肾", "降",   0.8),
    "麦冬": ("寒", "甘苦",   "心肺胃", "降",   0.9),
    "生地": ("寒", "甘苦",   "心肝肾", "降",   1.1),
    "五味子": ("温", "酸",   "肺肾心", "降",   0.8),
    "当归": ("温", "甘辛",   "肝心脾", "升",   1.0),
    "川芎": ("温", "辛",     "肝胆心包", "升浮", 1.0),
    "桔梗": ("平", "苦辛",   "肺",    "升浮", 0.7),
}


def drug_vector(name):
    """四气五味 → 六气(风 寒 暑 湿 燥 火)偏性向量（定性映射规则，可标定）"""
    qi, wei, gui, trend, pot = D[name]
    q = QI[qi]
    xin = 1.0 if "辛" in wei else 0.0
    ku = 1.0 if "苦" in wei else 0.0
    gan = 1.0 if "甘" in wei else 0.0
    suan = 1.0 if "酸" in wei else 0.0
    xian = 1.0 if "咸" in wei else 0.0
    dan = 1.0 if "淡" in wei else 0.0
    se = 1.0 if "涩" in wei else 0.0
    v = np.zeros(6)
    v[1] = -0.45 * max(q, 0)                       # 寒：温/热药祛寒
    fire = 0.45 * min(q, 0)                        # 火：寒/凉药清热（负=清热）
    v[5] = fire
    v[2] = 0.6 * fire                              # 暑：清火药兼清暑
    v[0] = -0.40 * xin                             # 风：辛散祛风
    AROMATIC = {"藿香", "紫苏", "白芷", "苍术", "砂仁", "厚朴", "陈皮", "佩兰"}
    v[3] = (-0.35 * ku - 0.55 * dan - 0.25 * (xin * ku)
            - 0.30 * (1.0 if name in AROMATIC else 0.0)   # 芳香化湿：仅芳香类药物（辛温≠芳香）
            + 0.15 * (suan + se))               # 湿
    v[4] = 0.20 * ku - 0.40 * xian - 0.25 * (gan * (q < 0))                   # 燥
    return v, pot, gan, trend


def net_formula(formula):
    """方剂净向量：君臣佐使加权 + 甘药增'扶正(自愈)'系数"""
    W = {"君": 1.0, "臣": 0.6, "佐": 0.4, "使": 0.25}
    v = np.zeros(6); tonic = 0.0; parts = []; warm = 0.0
    for nm, role in formula:
        dv, pot, gan, trend = drug_vector(nm)
        w = W[role] * pot
        v += w * dv
        _qi = QI[D[nm][0]]
        warm += w * max(_qi, 0) * (1.0 if "辛" in D[nm][1] else 0.0)   # 辛温之性（用于"暑火盛忌辛温"）
        tonic += W[role] * gan * 0.05
        parts.append((nm, role, w * dv))
    return v, min(tonic, 0.25), parts, warm


def _M():
    """病机传变矩阵（源→目标）：风火相煽 / 热盛伤津 / 湿从寒化 / 暑必兼湿"""
    M = np.zeros((6, 6))
    idx = {k: i for i, k in enumerate(AXES)}
    for s, t, c in [("风", "火", 0.10), ("火", "燥", 0.08), ("燥", "火", 0.04),
                    ("湿", "寒", 0.06), ("寒", "湿", 0.04), ("暑", "湿", 0.07),
                    ("火", "风", 0.03)]:
        M[idx[s], idx[t]] = c
    return M


# 剂型 = 动力学时间常数（古人已把"释放速度"编码在剂型里）
DOSE_TAU = {"汤": 1.0, "散": 1.5, "丸": 4.0, "膏": 6.0, "丹": 3.0}


def simulate(E0, Dnet, tonic, warm=0.0, form="汤", n_dose=10, T_dose=1.0, T=10.0, dt=0.02, alpha=1.1):
    """E' = -k0·E + M·E + α·Dnet
    规则：
      R1 药力线性叠加（α·Dnet）
      R2 误治助邪：若药力与病势同向（Dnet·E>0）→ 传变×1.8、自愈×0.5
      R3 寒凉抑遏：里有寒、湿未解而用大剂寒凉 → 反增寒湿
    """
    tau = DOSE_TAU.get(form, 1.0)
    M = _M() * (1.8 if float(np.dot(Dnet, E0)) > 0 else 1.0)
    k0 = (0.05 + tonic) * (0.5 if float(np.dot(Dnet, E0)) > 0 else 1.0)
    idx = {k: i for i, k in enumerate(AXES)}
    E = E0.astype(float).copy()
    D_eff = Dnet.copy()
    if E[idx["寒"]] > 0.3 and D_eff[idx["火"]] < -0.3:          # R3
        D_eff[idx["寒"]] += 0.35 * abs(D_eff[idx["火"]])
        D_eff[idx["湿"]] += 0.15 * abs(D_eff[idx["火"]])
    traj = [E.copy()]
    for i in range(int(T / dt)):
        tt = i * dt
        # 服药脉冲：每次一剂，药力按剂型时间常数衰减（汤速/丸缓/膏润）
        drug = 0.0
        k = 0
        while k < n_dose and k * T_dose <= tt:
            drug += np.exp(-(tt - k * T_dose) / tau)
            k += 1
        dE = -k0 * E + M @ E
        # R4 暑火已盛而用辛温 → 助热（"暑证忌辛温发汗"）
        if (E[idx["暑"]] + E[idx["火"]]) > 0.3:
            dE[idx["火"]] += 0.20 * warm * drug * min(1.0, max(0.0, E[idx["火"]] + E[idx["暑"]]) / 0.3)
        # 药力按"药势 vs 病势"门控：清该气时按剩余病势给力（病去药止，不过头）；
        # 助邪方向按已存在的病势给力且递增衰减（邪愈盛则增量愈小）
        for ax in range(6):
            f = alpha * D_eff[ax] * drug
            g = min(1.0, max(0.0, E[ax]) / 0.15)
            if f < 0:
                dE[ax] += f * g
            else:
                dE[ax] += f * g / (1.0 + max(0.0, E[ax]))
        E = E + dt * dE
        E = np.clip(E, -3, 3)
        traj.append(E.copy())
    return np.array(traj)


# ---------- 证候（人体能量失衡状态）与处方 ----------
CASES = {
    "风寒表实": dict(E=[0.8, 0.9, 0, 0, 0, 0],
                 good=[("麻黄", "君"), ("桂枝", "臣"), ("杏仁", "佐"), ("甘草", "使")],
                 bad=[("石膏", "君"), ("知母", "臣"), ("粳米", "佐")]),
    "暑湿困脾": dict(E=[0.2, 0.2, 0.6, 1.0, 0, 0.1],
                 good=[("藿香", "君"), ("紫苏", "臣"), ("厚朴", "臣"), ("滑石", "佐"),
                       ("茯苓", "佐"), ("白术", "佐"), ("甘草", "使")],
                 bad=[("附子", "君"), ("干姜", "臣"), ("甘草", "使")]),
    "阴虚火旺": dict(E=[0, 0, 0, 0, 0.5, 0.8],
                 good=[("生地", "君"), ("麦冬", "臣"), ("知母", "佐"), ("丹皮", "佐"),
                       ("茯苓", "使")],
                 bad=[("干姜", "君"), ("桂枝", "臣"), ("甘草", "使")]),
    "寒厥（少阴）": dict(E=[0, 1.3, 0, 0.2, 0, 0],
                    good=[("附子", "君"), ("干姜", "臣"), ("甘草", "使")],
                    bad=[("黄连", "君"), ("黄芩", "臣"), ("大黄", "佐")]),
}

def main():
    OUT = os.environ.get("TSIE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))
    os.makedirs(OUT, exist_ok=True)
    summary = {}

    # ================= 图1：雷达 —— 基线 / 证候 / 服药后 / 方剂向量 =================
    case = "风寒表实"
    c = CASES[case]
    E0 = np.array(c["E"])
    Dn, tonic, parts, warm_g = net_formula(c["good"])
    traj_good = simulate(E0, Dn, tonic, warm=warm_g)
    Dn_bad, tonic_bad, _, warm_b = net_formula(c["bad"])
    traj_bad = simulate(E0, Dn_bad, tonic_bad, warm=warm_b)

    ang = np.linspace(0, 2 * np.pi, 6, endpoint=False).tolist(); ang += ang[:1]
    fig, ax = plt.subplots(figsize=(7.2, 7.2), subplot_kw=dict(polar=True))
    for vec, lbl, col in [([0]*6, "阴平阳秘（基线）", "#7fb069"),
                          (list(E0), f"证候：{case}", "#d1495b"),
                          (list(traj_good[-1]), "服对证方后", "#00798c"),
                          (list(2.2 * Dn), "方剂净向量（药力方向）", "#edae49")]:
        vals = vec + vec[:1]
        ax.plot(ang, vals, label=lbl, color=col, lw=2.4)
        ax.fill(ang, vals, color=col, alpha=0.12)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(AXES, fontsize=17)
    ax.set_title(f"六气能量状态 · {case}（麻黄汤推演）", fontsize=16, pad=22)
    ax.legend(loc="upper right", bbox_to_anchor=(1.22, 1.12), fontsize=12)
    plt.tight_layout(); plt.savefig(f"{OUT}/1_六气雷达_风寒表实麻黄汤.png", dpi=130); plt.close()

    # ================= 图2：动态推演轨迹 =================
    t = np.arange(len(traj_good)) * 0.05
    fig, axs = plt.subplots(1, 2, figsize=(13.5, 5.6))
    ax = axs[0]
    ax.plot(t, np.linalg.norm(traj_good, axis=1), lw=3, color="#00798c", label="对证方（麻黄汤）")
    ax.plot(t, np.linalg.norm(traj_bad, axis=1), lw=3, color="#d1495b", label="反例：寒证误用白虎汤（寒凉抑遏）")
    ax.plot(t, np.linalg.norm(simulate(E0, np.zeros(6), 0.0, warm=0.0), axis=1), lw=2, ls="--",
            color="#8d99ae", label="不用药（自愈力 0.12）")
    ax.set_xlabel("推演时间（相对单位）"); ax.set_ylabel("总偏离 |E|（能量失衡度）")
    ax.set_title("干预后的状态轨迹（每日一剂·汤剂动力学）", fontsize=14)
    ax.legend(fontsize=12); ax.grid(alpha=0.3)
    ax = axs[1]
    for i, a in enumerate(AXES):
        ax.plot(t, traj_good[:, i], lw=2.4, label=a)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("推演时间"); ax.set_ylabel("各气偏离量")
    ax.set_title("对证方：六气逐项归零", fontsize=14)
    ax.legend(ncol=6, fontsize=11, loc="lower center"); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig(f"{OUT}/2_动态推演轨迹_收敛与发散.png", dpi=130); plt.close()

    # ================= 图3：药物偏性向量 + 方剂配伍 =================
    fig, axs = plt.subplots(1, 2, figsize=(14, 5.8))
    ax = axs[0]
    mat = np.array([p[2] for p in parts])
    names = [f"{p[0]}（{p[1]}）" for p in parts]
    bottom = np.zeros(6); colors = ["#d1495b", "#00798c", "#edae49", "#66a182", "#8d99ae", "#2e4057"]
    x = np.arange(6)
    for i, nm in enumerate(names):
        ax.bar(x, mat[i], bottom=bottom, label=nm)
        bottom += mat[i]
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(AXES, fontsize=15)
    ax.set_ylabel("对该气的修正量（负=祛/清）")
    ax.set_title("麻黄汤：各味药的能量偏性叠加", fontsize=14)
    ax.legend(fontsize=11); ax.grid(alpha=0.25, axis="y")
    ax = axs[1]
    labels = list(CASES.keys())
    good_ratio, bad_ratio, none_ratio = [], [], []
    for cs in labels:
        cc = CASES[cs]; e0 = np.array(cc["E"])
        d1, t1, _, w1 = net_formula(cc["good"]); tr1 = simulate(e0, d1, t1, warm=w1)
        d2, t2, _, w2 = net_formula(cc["bad"]); tr2 = simulate(e0, d2, t2, warm=w2)
        tr0 = simulate(e0, np.zeros(6), 0.0, warm=0.0)
        none_ratio.append(np.linalg.norm(tr0[-1]) / np.linalg.norm(e0))
        good_ratio.append(np.linalg.norm(tr1[-1]) / np.linalg.norm(e0))
        bad_ratio.append(np.linalg.norm(tr2[-1]) / np.linalg.norm(e0))
        summary[cs] = dict(对证方残余比=round(float(good_ratio[-1]), 3),
                           不用药残余比=round(float(none_ratio[-1]), 3),
                           误治残余比=round(float(bad_ratio[-1]), 3),
                           对证方=cc["good"][0][0] + "为主", 误治方=cc["bad"][0][0] + "为主")
    xx = np.arange(len(labels)); w = 0.26
    ax.bar(xx - w, good_ratio, w, label="对证方", color="#00798c")
    ax.bar(xx, none_ratio, w, label="不用药（仅自愈力）", color="#8d99ae")
    ax.bar(xx + w, bad_ratio, w, label="误治方", color="#d1495b")
    ax.axhline(1.0, color="k", ls="--", lw=1.2, label="1.0 = 与治疗前持平")
    ax.set_xticks(xx); ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel("治疗后 / 治疗前 的失衡比")
    ax.set_title("四证推演结局：对证 / 不用药 / 误治", fontsize=14)
    ax.legend(fontsize=12); ax.grid(alpha=0.25, axis="y")
    plt.tight_layout(); plt.savefig(f"{OUT}/3_药物偏性与四方结局.png", dpi=130); plt.close()

    json.dump(summary, open(f"{OUT}/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("图:", os.listdir(OUT))


if __name__ == "__main__":
    main()
