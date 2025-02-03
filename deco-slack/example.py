from deco_slack import deco_slack


@deco_slack(
    # These parameters are all optional
    start={"text": "start text", "title": "start", "color": "good"},
    success={"text": "success text", "title": "success", "color": "good"},
    error={
        "title": "error",
        "color": "danger",
        "stacktrace": True,  # Set True if you need stacktrace in a notification
    },
)
def test1():
    print("test1")


@deco_slack(
    success={"text": "success text", "title": "success", "color": "good"},
    error={"title": "error", "color": "danger", "stacktrace": True},
)
def error1():
    raise ValueError("error occured.")


# 動的メッセージのサンプル
@deco_slack(
    start={"text": "データ処理を開始します", "title": "処理開始", "color": "good"},
    success={
        "text_formatter": lambda result: f"処理が完了しました。結果: {result}",
        "title": "処理完了",
        "color": "good",
    },
    error={
        "text_formatter": lambda e: f"エラーが発生しました: {str(e)}",
        "title": "エラー",
        "color": "danger",
        "stacktrace": True,
    },
)
def process_with_result(data):
    # データ処理のサンプル
    result = data * 2
    return result


if __name__ == "__main__":
    test1()
    try:
        error1()
    except ValueError:
        pass

    # 動的メッセージのテスト
    process_with_result(10)
