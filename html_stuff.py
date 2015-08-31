
html_template = """<html>
<head>
<meta charset="utf-8">
<title>Welcome!</title>
</head>
<body>
<h1>Total: {total_value:.0f} </h1>

<h1>Selected expenses weekly ({weekly_categories})</h1>
{selected_expenses_weekly}

<h1>Expenses monthly by categories</h1>
{monthly_by_categories}

</body>
</html>"""


def represent_html(model):
    # copy model?
    model["selected_expenses_weekly"] = make_table(model["selected_expenses_weekly"])
    model["monthly_by_categories"] = make_table(model["monthly_by_categories"])
    result = html_template.format(**model)
    return result


def make_table(tt):
    result = ""
    result += '<table border="1">\n'
    for row in tt:
        result += '<tr>'
        for cell in row:
            if type(cell) == dict:
                if type(cell["value"]) in [float, int]:
                    cell["value"] = "{:.0f}".format(cell["value"])
                if "note" in cell:
                    cell["note"] = "\n".join(cell["note"])
                    result += '<td align="center" title="{note}">{value}</td>'.format(**cell)
                else:
                    result += '<td align="center" title="{value}">{value}</td>'.format(**cell)
            elif type(cell) == str:
                result += '<td align="center">{}</td>'.format(cell)
            elif type(cell) in [float, int]:
                result += '<td align="center">{:.0f}</td>'.format(cell)
        result += '</tr>\n'
    result += '</table>'
    return result
