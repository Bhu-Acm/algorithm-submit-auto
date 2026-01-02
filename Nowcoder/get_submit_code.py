import re
import requests
import time
from bs4 import BeautifulSoup
import json

# 通用请求头（复用你的登录态）
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "__snaker__id=jZzBVCzBLY5hDFBJ; NOWCODERUID=A7D93B40B14C28DF0B6BFCCF2268001E; NOWCODERCLINETID=2C8F1F657F1475346F7AC1FE7996DD70; gr_user_id=60fe1e72-d713-4e1e-adec-198223b2105b; isAgreementChecked=true; uid=619886673; uid.sig=58pmEbSRocBD0dmIGMwQMux5AWgoIlFHCYOYfb9RIn4; from=acm_calendar; gdxidpyhxdE=AsLCV2%5CMw58ZTPdMKt62zTv6%5CBdr6Y2%2BlXI%5Chd2YBRZ7TyKJ69bvD%2BzAWgm0Nrz%2BOrxlKX0%2FbwS21%5CUBdHILrcEYlZghzAjjy2S61OCGmmpJH2iH7n6MSrZ1nMxnHzks%2Bp%5CqKvtWjpdawKhdhpMKnhBLzfk%2BaG1JeO2h%5CThoYWDdepPk%3A1765697777541; Hm_lvt_a808a1326b6c06c437de769d1b85b870=1766235566,1766312465,1766315070,1766366281; HMACCOUNT=B443188E4D3EE3E9; _clck=mdiw18%5E2%5Eg23%5E0%5E2139; _clsk=; NOWCODER_SASS_SESSION_ID=d9f4d6de-e5ff-4109-8bca-bf991b66114f; _uetvid=ef412520e00511f080b10f798ddeec69; ls_sess_id=07BF7C38E20228ECEA41E510E199097E; c196c3667d214851b11233f5c17f99d5_gr_last_sent_cs1=619886673; t=F50BC6E95CC1CF21EDF17C2106F83706; username=%E6%9C%B1%E9%81%93%E9%98%B3; username.sig=5ek_mVVk4bMh0_9e28NpEYjt20niO0IRWod9O30zND0; aliyungf_tc=b93521b7f3a66bd1daf1ef9f3620e3d369e31f3592f963dea882909e4e5dfbd5; c196c3667d214851b11233f5c17f99d5_gr_session_id=7724fdc3-31d9-4111-87f7-e8cc867d94ae; c196c3667d214851b11233f5c17f99d5_gr_last_sent_sid_with_cs1=7724fdc3-31d9-4111-87f7-e8cc867d94ae; c196c3667d214851b11233f5c17f99d5_gr_session_id_sent_vst=7724fdc3-31d9-4111-87f7-e8cc867d94ae; acw_tc=0a18ab6d17672650377491682e51977cd5837769730201dd0d9b121c8e8643; c196c3667d214851b11233f5c17f99d5_gr_cs1=619886673; Hm_lpvt_a808a1326b6c06c437de769d1b85b870=1767265613",
    "Host": "ac.nowcoder.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}

# 语言映射表（根据牛客网实际值调整）
LANGUAGE_MAP = {
    "C++(g++ 13)": {"id": 38, "name": "C++(g++ 13)"},
    "C++（clang++18）": {"id": 2, "name": "C++（clang++18）"},
    "C++": {"id": 2, "name": "C++"},
    "C(gcc 10)": {"id": 39, "name": "C(gcc 10)"},
    "Java": {"id": 4, "name": "Java"},
    "C": {"id": 1, "name": "C"},
    "Python2": {"id": 5, "name": "Python2"},
    "Python3": {"id": 11, "name": "Python3"},
    "pypy2": {"id": 24, "name": "pypy2"},
    "pypy3": {"id": 25, "name": "pypy3"},
    "C#": {"id": 9, "name": "C#"}
}

def get_problem_page_info(problem_id):
    f"""
    从https://ac.nowcoder.com/acm/problem/{problem_id}页面提取window.pageInfo数据
    :param problem_id: 题目ID
    :return: pageInfo字典或None
    """
    url = f"https://ac.nowcoder.com/acm/problem/{problem_id}"
    try:
        print(f"\n🔍 正在获取题目{problem_id}的pageInfo数据...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"

        # 提取JS中的window.pageInfo
        page_info = extract_page_info_from_html(response.text)
        return page_info

    except Exception as e:
        print(f"❌ 获取题目{problem_id}的pageInfo失败：{str(e)}")
        return None


def extract_page_info_from_html(html_content):
    """从HTML的JS代码中提取window.pageInfo的数据"""
    try:
        # 增强正则匹配，适配更多格式的window.pageInfo
        pattern = r'window\.pageInfo\s*=\s*({[\s\S]*?});\s*(//|$|\n)'
        match = re.search(pattern, html_content)
        if not match:
            print("❌ 未找到window.pageInfo数据")
            return None

        # 提取JSON字符串并处理格式问题
        page_info_str = match.group(1)
        # 移除单行注释
        page_info_str = re.sub(r'//.*?$', '', page_info_str, flags=re.MULTILINE)
        # 移除多行注释
        page_info_str = re.sub(r'/\*[\s\S]*?\*/', '', page_info_str)
        # 单引号转双引号
        page_info_str = page_info_str.replace("'", '"')
        # 修复末尾多余逗号
        page_info_str = re.sub(r',\s*}', '}', page_info_str)
        page_info_str = re.sub(r',\s*]', ']', page_info_str)
        # 处理未加引号的key
        page_info_str = re.sub(r'(\w+):', r'"\1":', page_info_str)

        # 解析为字典
        page_info = json.loads(page_info_str)
        print("✅ 成功提取window.pageInfo数据：")
        print(json.dumps(page_info, ensure_ascii=False, indent=2))
        return page_info

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败：{str(e)}")
        print(f"待解析字符串：{page_info_str[:500]}...")
        return None
    except Exception as e:
        print(f"❌ 提取window.pageInfo失败：{str(e)}")
        return None


def get_submission_ids(problem_ids):
    """
    批量处理题目ID，获取提交记录ID
    :param problem_ids: 题目ID列表
    """
    if not isinstance(problem_ids, list):
        problem_ids = [problem_ids]

    for problem_id in problem_ids:
        get_submission(problem_id)


def get_submission(problem_id):
    """获取指定题目ID的提交记录ID列表"""
    print(f"\n========== 开始处理题目 {problem_id} ==========")
    url = f"https://ac.nowcoder.com/acm/problem/{problem_id}/submit-list"
    submission_ids = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取tr标签的data-href中的submissionId
        tr_list = soup.find_all('tr', class_='js-nc-wrap-link')
        for tr in tr_list:
            data_href = tr.get('data-href', '')
            if 'submissionId=' in data_href:
                sid = data_href.split('submissionId=')[-1]
                if sid.isdigit():
                    submission_ids.append(sid)

        # 去重
        submission_ids = list(set(submission_ids))
        print(f"✅ 题目{problem_id}提取到 {len(submission_ids)} 个submissionId")

        # 解析第一个submissionId的代码详情
        if submission_ids:
            # 先获取该题的pageInfo（用于后续提交）
            page_info = get_problem_page_info(problem_id)
            if page_info:
                parse_code_detail(problem_id, submission_ids[0], page_info)
            else:
                print("⚠️ 缺少pageInfo，跳过代码提交")
        else:
            print("⚠️ 未找到任何submissionId")

        time.sleep(2)

    except Exception as e:
        print(f"❌ 提取{submission_ids}失败：{str(e)}")

    return submission_ids


def parse_code_detail(problem_id, submission_id, page_info):
    """
    解析指定提交ID的代码详情，并触发提交
    :param problem_id: 题目ID
    :param submission_id: 提交记录ID
    :param page_info: 题目页面的pageInfo数据
    """
    print(f"\n🔍 正在解析submissionId {submission_id}...")
    url = f"https://ac.nowcoder.com/acm/contest/view-submission?submissionId={submission_id}"

    try:
        time.sleep(2)  # 延迟避免封禁
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 提取提交语言
        language = ""
        lang_span = soup.find('span', string=lambda x: x and '语言：' in x)
        if lang_span:
            language = lang_span.text.split('语言：')[-1].split('（')[0].strip()
            # 适配语言名称（如"Java 1.8"转为"Java"）
            language = language.split()[0]

        # 2. 提取代码
        code = ""
        code_pre = soup.find('pre', class_=lambda x: x and 'lang-' in x)
        if code_pre:
            code = code_pre.text.strip()

        code_info = {
            "submission_id": submission_id,
            "problem_id": problem_id,
            "language": language,
            "code": code
        }

        print(f"✅ 解析完成：{json.dumps(code_info, ensure_ascii=False, indent=2)}")

        # 提交代码
        if code and page_info:
            submit_code(code_info, page_info)
        else:
            print("⚠️ 代码为空或缺少pageInfo，跳过提交")

    except Exception as e:
        print(f"❌ 解析submissionId {submission_id} 失败：{str(e)}")
        return {
            "submission_id": submission_id,
            "language": "",
            "problem_id": problem_id,
            "code": ""
        }


def submit_code(code_info, page_info):
    """
    提交代码到牛客网（使用从页面提取的pageInfo参数）
    :param code_info: 代码信息字典
    :param page_info: 页面的pageInfo字典
    :return: 提交结果字典
    """
    # 构建提交URL
    submit_url = "https://ac.nowcoder.com/nccommon/submit_cd?"

    print(f"code_info: {code_info.get('language')}")

    # 从pageInfo提取必要参数（优先级：pageInfo > 默认值）
    question_id = page_info.get("questionId", code_info["problem_id"])
    tag_id = page_info.get("tagId", 4)
    sub_tag_id = page_info.get("subTagId", 1)
    done_question_id = page_info.get("doneQuestionId", 18839)

    # 获取语言信息
    language = code_info.get("language", "Java")
    lang_info = LANGUAGE_MAP.get(language, ["Java"])

    # 获取代码
    code = code_info.get("code", "")

    # 构建表单数据
    form_data = {
        "questionId": str(question_id),
        "tagId": str(tag_id),
        "subTagId": str(sub_tag_id),
        "content": code,
        "language": str(lang_info["id"]),
        "languageName": lang_info["name"],
        "doneQuestionId": str(done_question_id)
    }

    print("提交表单数据:", form_data)

    # 调整请求头（POST请求需要的头部）
    post_headers = HEADERS.copy()
    post_headers.update({
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Origin": "https://ac.nowcoder.com",
        "Referer": f"https://ac.nowcoder.com/acm/problem/{question_id}"
    })

    try:
        print(f"\n📤 开始提交代码到题目 {question_id}...")
        print(f"🔤 使用语言: {lang_info['name']} (ID: {lang_info['id']})")

        # 发送POST请求提交代码
        response = requests.post(
            submit_url,
            data=form_data,
            headers=post_headers,
            timeout=30
        )
        response.raise_for_status()

        # 解析响应
        result = response.json() if response.text else {}
        print(f"✅ 提交成功！响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

        return {
            "success": True,
            "data": result,
            "status_code": response.status_code
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ 提交失败：{str(e)}")
        error_info = {
            "success": False,
            "error": str(e),
            "status_code": None,
            "response_text": ""
        }
        if hasattr(e, 'response') and e.response is not None:
            error_info["status_code"] = e.response.status_code
            error_info["response_text"] = e.response.text
            print(f"响应状态码: {error_info['status_code']}")
            print(f"响应内容: {error_info['response_text']}")
        return error_info
    except Exception as e:
        print(f"❌ 提交过程中发生未知错误：{str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# 主函数
if __name__ == "__main__":
    # 要处理的题目ID列表
    TARGET_PROBLEM_IDS = [209794]  # 可添加多个题目ID

    # 执行完整流程：获取提交ID → 解析代码 → 提交代码
    get_submission_ids(TARGET_PROBLEM_IDS)
