# main.py
"""
Mini NPU Simulator
1단계: 데이터 구조 + MAC 연산 코어
"""

import json
import time


# ----------------------------------------
# 1. 데이터 구조 관련 함수
# ----------------------------------------

def create_grid(size, fill=0.0):
    """size x size 2차원 배열(리스트의 리스트) 생성"""
    return [[fill for _ in range(size)] for _ in range(size)]


def set_cell(grid, row, col, value):
    """특정 위치 값 저장"""
    grid[row][col] = value


def get_cell(grid, row, col):
    """특정 위치 값 읽기"""
    return grid[row][col]


def get_size(grid):
    """grid의 크기(N) 반환 (N x N 기준)"""
    return len(grid)


# ----------------------------------------
# 2. MAC 연산 코어 (반복문 구현, 외부 라이브러리 금지)
# ----------------------------------------

def mac_operation(pattern, filter_):
    """
    입력 패턴과 필터를 위치별로 곱하고 모두 더함
    반환: float 점수
    """
    size_p = len(pattern)
    size_f = len(filter_)

    if size_p != size_f:
        raise ValueError(
            f"크기 불일치: pattern={size_p}x{size_p}, filter={size_f}x{size_f}"
        )

    score = 0.0
    for i in range(size_p):
        row_p = pattern[i]
        row_f = filter_[i]
        if len(row_p) != size_p or len(row_f) != size_f:
            raise ValueError("행 길이가 정사각형 크기와 일치하지 않습니다.")
        for j in range(size_p):
            score += row_p[j] * row_f[j]

    return score


def measure_mac_time(pattern, filter_, repeat=10):
    """
    MAC 연산 시간 측정 (I/O 제외, 순수 연산 구간만)
    반환: (평균 시간(ms), 마지막 점수)
    """
    total_time = 0.0
    score = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        score = mac_operation(pattern, filter_)
        end = time.perf_counter()
        total_time += (end - start)

    avg_ms = (total_time / repeat) * 1000
    return avg_ms, score


# ----------------------------------------
# 3. 모드 1: 사용자 입력 (3x3) 처리
# ----------------------------------------
 
MODE1_SIZE = 3
 
 
def parse_row(line, size):
    """
    한 줄(공백 구분)을 파싱해 float 리스트로 반환.
    실패 시 None 반환 (호출부에서 재입력 유도).
    """
    tokens = line.strip().split()
    if len(tokens) != size:
        return None
    try:
        return [float(t) for t in tokens]
    except ValueError:
        return None
 
 
def input_grid(label, size):
    """
    size줄을 공백 구분으로 입력받아 size x size 그리드 생성.
    행/열 개수 불일치, 숫자 파싱 실패 시 안내 후 해당 줄 재입력.
    """
    print(f"\n{label} ({size}줄 입력, 공백 구분)")
    grid = []
    row_idx = 0
    while row_idx < size:
        line = input()
        row = parse_row(line, size)
        if row is None:
            print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
            continue
        grid.append(row)
        row_idx += 1
    return grid
 
 
def run_mode1():
    """모드 1: 사용자 입력(3x3) → MAC 연산 → 판정 → 성능 분석"""
    print("\n" + "-" * 40)
    print("# [1] 필터 입력")
    print("-" * 40)
    filter_a = input_grid("필터 A", MODE1_SIZE)
    filter_b = input_grid("필터 B", MODE1_SIZE)
 
    print("\n" + "-" * 40)
    print("# [2] 패턴 입력")
    print("-" * 40)
    pattern = input_grid("패턴", MODE1_SIZE)
 
    print("\n" + "-" * 40)
    print("# [3] MAC 결과")
    print("-" * 40)
    avg_ms_a, score_a = measure_mac_time(pattern, filter_a, repeat=10)
    avg_ms_b, score_b = measure_mac_time(pattern, filter_b, repeat=10)
    avg_ms = (avg_ms_a + avg_ms_b) / 2
 
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_ms:.4f} ms")
 
    if abs(score_a - score_b) < 1e-9:
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")


# ----------------------------------------
# 3. 모드 2: data.json 로드 및 스키마 검증
# ----------------------------------------

DATA_JSON_PATH = "data.json"


def normalize_label(raw):
    """
    원본 값을 표준 라벨(Cross/X)로 정규화.
    expected: '+' -> Cross, 'x' -> X
    filter 키: 'cross' -> Cross, 'x' -> X
    매칭 실패 시 None 반환.
    """
    if raw is None:
        return None
    key = str(raw).strip().lower()
    if key in ("+", "cross"):
        return "Cross"
    if key == "x":
        return "X"
    return None


def load_data_json(path=DATA_JSON_PATH):
    """
    data.json을 로드.
    실패 시 (None, 에러메시지) 반환. 프로그램은 종료시키지 않음.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except FileNotFoundError:
        return None, f"파일을 찾을 수 없습니다: {path}"
    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 오류: {e}"


def extract_size_from_key(pattern_key):
    """
    'size_5_1' -> 5, 'size_13_2' -> 13 형태로 N 추출.
    형식이 맞지 않으면 None 반환.
    """
    parts = pattern_key.split("_")
    if len(parts) < 2 or parts[0] != "size":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def get_filters_for_size(filters, size):
    """
    filters에서 size_N 항목을 찾아 (cross_filter, x_filter, 에러메시지) 반환.
    없으면 (None, None, 에러메시지).
    """
    size_key = f"size_{size}"
    if size_key not in filters:
        return None, None, f"{size_key} 필터가 data.json에 존재하지 않습니다."

    size_filters = filters[size_key]
    cross_f = None
    x_f = None
    for raw_key, grid in size_filters.items():
        label = normalize_label(raw_key)
        if label == "Cross":
            cross_f = grid
        elif label == "X":
            x_f = grid

    if cross_f is None or x_f is None:
        return None, None, f"{size_key}에서 Cross/X 필터를 모두 찾지 못했습니다 (키: {list(size_filters.keys())})."

    return cross_f, x_f, None


def validate_size_match(pattern_input, cross_f, x_f, expected_size):
    """
    패턴/필터 크기가 expected_size(N)와 일치하는지 검증.
    불일치 시 에러메시지 반환, 일치하면 None.
    """
    p_size = len(pattern_input)
    if p_size != expected_size:
        return f"패턴 크기 불일치: 실제 {p_size}, 기대 {expected_size}"
    for row in pattern_input:
        if len(row) != expected_size:
            return f"패턴 행 길이 불일치: 실제 {len(row)}, 기대 {expected_size}"

    for label, f in (("Cross", cross_f), ("X", x_f)):
        if len(f) != expected_size:
            return f"{label} 필터 크기 불일치: 실제 {len(f)}, 기대 {expected_size}"
        for row in f:
            if len(row) != expected_size:
                return f"{label} 필터 행 길이 불일치: 실제 {len(row)}, 기대 {expected_size}"

    return None


def load_and_validate_cases(data):
    """
    data.json 구조(filters/patterns)를 순회하며 케이스 목록 생성.
    각 케이스: {key, size, pattern, cross_f, x_f, expected_label, error}
    error가 있으면 이후 단계(MAC 연산)는 건너뛰고 FAIL 처리 대상.
    """
    cases = []

    filters = data.get("filters")
    patterns = data.get("patterns")

    if filters is None or patterns is None:
        return cases, "data.json에 'filters' 또는 'patterns' 키가 없습니다."

    for pattern_key, pattern_obj in patterns.items():
        size = extract_size_from_key(pattern_key)
        case = {
            "key": pattern_key,
            "size": size,
            "pattern": None,
            "cross_f": None,
            "x_f": None,
            "expected_label": None,
            "error": None,
        }

        if size is None:
            case["error"] = f"패턴 키 형식 오류: '{pattern_key}'에서 크기(N)를 추출할 수 없습니다."
            cases.append(case)
            continue

        pattern_input = pattern_obj.get("input")
        expected_raw = pattern_obj.get("expected")

        if pattern_input is None:
            case["error"] = "패턴 데이터(input)가 없습니다."
            cases.append(case)
            continue

        expected_label = normalize_label(expected_raw)
        if expected_label is None:
            case["error"] = f"expected 값 '{expected_raw}'을(를) 표준 라벨로 정규화할 수 없습니다."
            cases.append(case)
            continue

        cross_f, x_f, err = get_filters_for_size(filters, size)
        if err:
            case["error"] = err
            cases.append(case)
            continue

        size_err = validate_size_match(pattern_input, cross_f, x_f, size)
        if size_err:
            case["error"] = size_err
            cases.append(case)
            continue

        case["pattern"] = pattern_input
        case["cross_f"] = cross_f
        case["x_f"] = x_f
        case["expected_label"] = expected_label
        cases.append(case)

    return cases, None


def run_mode2_load_only():
    """3단계 자체 확인용: 로드 + 검증까지만 수행하고 결과 출력 (판정/성능은 4~5단계)"""
    print("\n" + "-" * 40)
    print("# [1] 필터 로드")
    print("-" * 40)

    data, err = load_data_json()
    if err:
        print(f"✗ data.json 로드 실패: {err}")
        return

    for size in (5, 13, 25):
        _, _, ferr = get_filters_for_size(data.get("filters", {}), size)
        if ferr:
            print(f"✗ size_{size} 필터 로드 실패: {ferr}")
        else:
            print(f"✓ size_{size} 필터 로드 완료 (Cross, X)")

    print("\n" + "-" * 40)
    print("# [2] 패턴 로드 및 검증")
    print("-" * 40)

    cases, load_err = load_and_validate_cases(data)
    if load_err:
        print(f"✗ {load_err}")
        return

    for case in cases:
        if case["error"]:
            print(f"--- {case['key']} ---")
            print(f"✗ FAIL (검증 오류): {case['error']}")
        else:
            print(f"--- {case['key']} ---")
            print(f"✓ 검증 통과 (size={case['size']}, expected={case['expected_label']})")


# ----------------------------------------
# 간단 동작 확인 (1단계 자체 테스트용)
# ----------------------------------------

if __name__ == "__main__":
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    choice = input("선택: ").strip()
 
    if choice == "1":
        run_mode1()
    elif choice == "2":
        run_mode2_load_only()
    else:
        print("잘못된 선택입니다. 1 또는 2를 입력하세요.")