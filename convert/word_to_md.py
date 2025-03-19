import time
import mammoth
import markdownify

def convert_imgs(img):
    with img.open() as img_bytes:
        file_suffix = img.content_type.split("/")[1]
        path_file = f"./img/{str(time.time())}.{file_suffix}"
        with open(path_file, "wb") as f:
            f.write(img_bytes.read())
    return {"src": path_file}


with open(r"./data/教育技术学导论.docx", "rb") as docx_file:
    ret = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.img_element(convert_imgs))
    html = ret.value

    md = markdownify.markdownify(html, heading_style="ATX")
    print(md)
    with open("./output/docx_to_html.html", "w", encoding="utf-8") as html_file, open("./output/docx_to_md.md", "w", encoding="utf-8") as md_file:
        html_file.write(html)
        md_file.write(md)
    messages = ret.messages
    print(messages)