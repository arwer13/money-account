
html_template = """<html>
<head><title>{title}</title></head>
<body>
<h1>Total: {total_value:.0f} </h1> </br>

<h1>Selected expenses weekly*</h1>
{selected_expenses_weekly}

<h1>Expenses by categories</h1>
{expenses_by_categories}
</body>
</html>"""

def make_table(tt):
    result = ""
    result += '<table border="1">\n'
    for row in tt:
        result += '<tr>'
        result += (len(row)*'<td align="center">{}</td>').format(*row)
        result += '</tr>\n'
    result += '</table>'
    return result
