import hashlib


def get_md5(url):
    """
    传入url生成相应的MD5字符串
    :param url: 页面url
    :return:    url相应MD5字符串
    """
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()
