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
# 간단 동작 확인 (1단계 자체 테스트용)
# ----------------------------------------

if __name__ == "__main__":
    cross_filter = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    x_filter = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]
    cross_pattern = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]

    print("=== 1단계 동작 확인 ===")
    score_a = mac_operation(cross_pattern, cross_filter)
    score_b = mac_operation(cross_pattern, x_filter)
    print(f"Cross 필터 점수: {score_a}")
    print(f"X 필터 점수: {score_b}")

    avg_ms, _ = measure_mac_time(cross_pattern, cross_filter, repeat=10)
    print(f"연산 시간(평균/10회): {avg_ms:.4f} ms")