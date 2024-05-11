class Probihited_words:
    probihited_words = [
        "sb",
        "傻逼",
        "有病",
        "你妈",
        "渣渣",
        "木琴"
    ]
    wordsToReplace = {
        "弟弟": "dd",
        "趋势": "**",
        "去世": "无了",
        "口我": "嘿嘿",
        "LL": "66",
        "垃圾": "有点菜",
        "垃姬": "有点菜",
        "辣鸡": "有点菜",
        "坟": "*"

    }
    def __ListStrInIter__(__str: str, __iter: list) -> bool:
        for i in __iter:
            if i in __str:
                return True
        return False
    
    def checkProbihited(words: str):
        words = words.replace("64个", "一组").replace("64", "一组")
        pre_check = words.replace(" ", "")
        if Probihited_words.__ListStrInIter__(pre_check, Probihited_words.probihited_words) or Probihited_words.__ListStrInIter__(pre_check, Probihited_words.wordsToReplace):
            for i in Probihited_words.probihited_words:
                pre_check = pre_check.replace(i, "?")
            for i in Probihited_words.wordsToReplace:
                pre_check = pre_check.replace(i, Probihited_words.wordsToReplace[i])
            return pre_check
        else:
            return words
