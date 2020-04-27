from pyppeteer import launch


class UnsupportedFileFormat(Exception):
    pass


async def convert_to_pdf(file_path, loop):
    browser = await launch(args=["--no-sandbox"], loop=loop)

    page = await browser.newPage()
    file_format = file_path.split(".")[-1]
    if file_format in ['doc', 'docx', 'odt', 'ott', 'stw', 'sdw', 'sxw']:
        path = "word_to_pdf"
    elif file_format in ['xls', 'xlsx', 'ods', 'ots', 'sdc', 'sxc']:
        path = "excel_to_pdf"
    elif file_format in ['ppt', 'pptx', 'odp', 'pps', 'ppsx', 'sxi']:
        path = "powerpoint_to_pdf"
    elif file_format in ['jpg', 'jpeg', 'png', 'tif', 'tiff']:
        path = "jpg_to_pdf"
    else:
        raise UnsupportedFileFormat

    await page.goto(f'https://www.ilovepdf.com/{path}')
    await page.waitForSelector("#pickfiles")
    await page.click("#pickfiles")

    #  Upload document
    input_field = await page.J('input[type="file"]')
    await input_field.uploadFile(file_path)
    await page.waitForSelector("#processTask")

    await page.click("#processTask")

    await page.waitForSelector("svg[data-icon=\"download\"]")
    result = await page.evaluate(
        '() => document.querySelector("a.downloader__btn").href'
    )
    await browser.close()

    return result

