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
        print("모드 2는 3단계에서 구현 예정입니다.")
    else:
        print("잘못된 선택입니다. 1 또는 2를 입력하세요.")