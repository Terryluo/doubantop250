import xlwt as xl


def createworkbook():
    workbook = xl.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('multiplicationForm')

    for row in range(1, 10):
        for col in range(1, row + 1):
            worksheet.write(row - 1, col - 1, '%d x %d = %d' % (row, col, row * col))

    workbook.save('multiplicationForm.xls')


createworkbook()
