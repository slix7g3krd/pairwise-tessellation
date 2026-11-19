"""第 59 批：角色走近高模雕塑，轮廓边缘突然裂开，置换贴图把三角形拉出缝隙：曲..."""

# 阴影 pass 允许的最低细分比例：过低会导致投影轮廓与主 pass 对不上。
SHADOW_MIN_RATIO = 0.5
# 水密判定使用的容差。
WATERTIGHT_EPS = 1e-6
# 逐帧因子平滑系数（0.5 表示对上一帧与当前帧取平均）。
FRAME_BLEND = 0.5


def screen_factor(distance, edge_length):
    """屏幕误差细分因子。

    细分因子与边在屏幕上的投影大小成正比，与相机距离成反比。
    """
    if distance <= 0.0:
        return 0.0
    return float(edge_length) / float(distance)


def uv_seam(u, seam):
    """UV 接缝距离。

    UV 空间是周期性的，接缝两侧应按环绕后的最短距离比较，
    否则 u=0.9 与 seam=0.1 会被误判为相距 0.8。
    """
    d = abs(float(u) - float(seam))
    d = d % 1.0
    return min(d, 1.0 - d)


def uv_set_match(set_a, set_b):
    """判断 UV 集是否一致。

    法线贴图与置换贴图必须采样同一个 UV 集，否则凹凸方向会错。
    """
    return set_a == set_b


def winding_flip(indices, flipped):
    """修正细分绕序。

    细分生成的三角形必须继承父三角形绕序；需要翻转时交换首尾顶点。
    """
    idx = tuple(indices)
    return tuple(reversed(idx)) if flipped else idx


def shadow_factor(base, shadow):
    """阴影 pass 因子。

    阴影 pass 可以使用较低因子，但不得低于主 pass 的一半，
    以免投影轮廓与主体轮廓错开。
    """
    base = float(base)
    shadow = float(shadow)
    return max(base * SHADOW_MIN_RATIO, min(shadow, base))


def lod_factor(base, lod):
    """LOD 细分因子。

    每提升一级 LOD，因子按 2 的幂增长；相邻 LOD 使用同一公式，
    避免切换时因子跳变导致顶点弹跳。
    """
    return float(base) * (2.0 ** int(lod))


def scaled_displacement(value, scale):
    """按缩放调整置换。

    置换幅度是模型空间量，必须随模型缩放同比缩放，否则放大后表面过鼓。
    """
    return float(value) * float(scale)


def watertight_edge(left, right):
    """判断边界是否水密。

    两侧边界顶点重合（在容差内）才视为水密，可避免 T 形裂缝。
    """
    return abs(float(left) - float(right)) <= WATERTIGHT_EPS


def skin_before_tess(weight):
    """蒙皮与细分顺序权重。

    返回钳制到 [0, 1] 的蒙皮权重：细分应在蒙皮之后进行，
    该权重用于在两者之间过渡而不越界。
    """
    return min(1.0, max(0.0, float(weight)))


def platform_limit(factor, limit):
    """平台细分上限。

    移动端上限较低，必须把因子钳制到平台能力之内。
    """
    return min(factor, limit)


def frame_factor(last, current):
    """逐帧因子平滑。

    基于当前帧的相机状态即时计算，并与上一帧做加权平均，
    避免快速推拉镜头时因子滞后。
    """
    return FRAME_BLEND * float(last) + (1.0 - FRAME_BLEND) * float(current)


def bounds_expand(bounds, displacement):
    """扩展细分包围盒。

    置换会把顶点推出原包围盒，视锥剔除前必须按置换幅度外扩。
    """
    lo, hi = bounds
    d = abs(float(displacement))
    return (float(lo) - d, float(hi) + d)


def cache_key(mesh_id, material_version):
    """细分缓存版本。

    缓存键必须包含材质版本，换材质后不能继续复用旧置换结果。
    """
    return (mesh_id, material_version)
