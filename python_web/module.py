import re
# 翻页保持url相对不变
def static_url(current_url, page_num, all_page_num, index_num):
    result = re.search(r'page=[0-9]+', current_url)
    if result != None:
        first_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(1), current_url)
        end_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(all_page_num), current_url)
        prev_page_url = current_url
        if page_num > 1:
            prev_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(page_num-1), current_url)
        next_page_url = current_url
        if page_num < all_page_num:
            next_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(page_num+1), current_url)
    else: # 现在已经在第一页中
        if index_num == 0:
            first_page_url = current_url + 'page=1'
            end_page_url = current_url + 'page={}'.format(all_page_num)
            prev_page_url = first_page_url
            if all_page_num == 1:
                next_page_url = first_page_url
            else:
                next_page_url = current_url + 'page=2'
        else:
            first_page_url = current_url + '&page=1'
            end_page_url = current_url + '&page={}'.format(all_page_num)
            prev_page_url = first_page_url
            if all_page_num == 1:
                next_page_url = first_page_url
            else:
                next_page_url = current_url + '&page=2'

    page_info = {
        'first_page_url': first_page_url,
        'prev_page_url': prev_page_url,
        'next_page_url': next_page_url,
        'end_page_url': end_page_url,
        'cur_page_num': page_num,
        'max_page_num': all_page_num
    }
    return page_info

if __name__ == "__main__":
    pass