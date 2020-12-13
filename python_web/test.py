import re
current_url = "&/issue_center"
end_page_url = re.sub(r'page=[0-9]+', 'page={}'.format(24), current_url)
print(end_page_url)

print(current_url.split('&'))