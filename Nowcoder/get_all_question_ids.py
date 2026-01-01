import requests
import time

from Nowcoder.get_submit_code import get_submission_ids


def get_all_question_ids():
    list_url = "https://ac.nowcoder.com/acm/problem/list/json"
    page = 1
    page_size = 50
    all_question_ids = []

    while True:
        # 构造请求参数
        params = {
            "token": "",
            "keyword": "",
            "tagId": "",
            "platformTagId": 0,
            "sourceTagId": 0,
            "difficulty": 0,
            "order": "id",
            "status": "all",
            "page": page,
            "pageSize": page_size,
        }
        try:
            # 发送请求（模拟浏览器）
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(list_url, headers=headers)
            response.raise_for_status()  # 捕获HTTP错误
            data = response.json()

            # 提取当前页的questionId
            problem_sets = data.get("data", {}).get("problemSets", [])
            if not problem_sets:
                print("无更多题目，停止爬取")
                break  # 没有更多题目，终止循环

            # 收集当前页的questionId
            current_page_ids = []
            for problem in problem_sets:
                question_id = problem.get("problemId")
                if question_id:
                    current_page_ids.append(question_id)
                    all_question_ids.append(question_id)

            print(f"===== 第 {page} 页爬取完成，共 {len(current_page_ids)} 条 =====")
            print(f"当前页questionId: {current_page_ids}")
            print(f"已累计获取 {len(all_question_ids)} 个questionId")

            # 现在对这50个题目分别获取答案并提交
            get_submission_ids(current_page_ids)

            # 每爬取1页（50条）后暂停5秒
            print(f"暂停10秒后继续爬取下一页...")
            time.sleep(10)

            page += 1  # 下一页

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            break

    return all_question_ids


# 执行爬取并输出结果
if __name__ == "__main__":
    # 记录开始时间
    start_time = time.time()
    # 爬取所有questionId
    question_ids = get_all_question_ids()
    # 输出最终结果
    print("\n==================== 爬取完成 ====================")
    print(f"共获取到 {len(question_ids)} 个questionId")
    print(f"总耗时: {round(time.time() - start_time, 2)} 秒")