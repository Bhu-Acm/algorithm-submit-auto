import requests
import time


def get_all_question_ids():
    base_url = "https://ac.nowcoder.com/acm/problem/list/json"
    page = 1
    page_size = 50
    all_question_ids = []

    while True:
        print(f"当前页面为:{page}")
        # 构造请求参数
        params = {
            "page": page,
            "pageSize": page_size
        }
        try:
            # 发送请求（模拟浏览器）
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(base_url, params=params, headers=headers)
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
                question_id = problem.get("questionId")
                if question_id:
                    current_page_ids.append(question_id)
                    all_question_ids.append(question_id)

            # 执行你自定义的其他逻辑（示例：打印当前页ID）
            print(f"===== 第 {page} 页爬取完成，共 {len(current_page_ids)} 条 =====")
            print(f"当前页questionId: {current_page_ids}")
            # 这里可以添加你的其他逻辑，比如写入文件、数据清洗等
            # --------------------------
            # 你的自定义逻辑写在这里
            # --------------------------

            print(f"已累计获取 {len(all_question_ids)} 个questionId")

            # 每爬取1页（50条）后暂停5秒
            print(f"暂停5秒后继续爬取下一页...")
            time.sleep(5)

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            break

        page += 1  # 下一页

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