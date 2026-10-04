with open("tools/build-index.mjs", "r", encoding="utf-8") as f:
    text = f.read()

# Replace all backticks and ${} in the newly added search and qr code sections
text = text.replace("`\\${normId} \\${numId} \\${normTitle} \\${normAlt} \\${normAuthor} \\${normBody}`", "[normId, numId, normTitle, normAlt, normAuthor, normBody].join(' ')")
text = text.replace("`${normId} ${numId} ${normTitle} ${normAlt} ${normAuthor} ${normBody}`", "[normId, numId, normTitle, normAlt, normAuthor, normBody].join(' ')")
text = text.replace("`FWP:${pl.title}|${songIds}`", "'FWP:' + pl.title + '|' + songIds")
text = text.replace("`FWP:\\${pl.title}|\\${songIds}`", "'FWP:' + pl.title + '|' + songIds")

# Qr code rect and svg replacements without backticks
old_rect = """rects += `<rect x="${(c * cellSize).toFixed(2)}" y="${(r * cellSize).toFixed(2)}" width="${cellSize}" height="${cellSize}" fill="#1c1917" />`;"""
new_rect = """rects += '<rect x=\"' + (c * cellSize).toFixed(2) + '\" y=\"' + (r * cellSize).toFixed(2) + '\" width=\"' + cellSize + '\" height=\"' + cellSize + '\" fill=\"#1c1917\" />';"""

old_svg = """return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" style="background:#ffffff; border-radius: 8px; padding: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">${rects}</svg>`;"""
new_svg = """return '<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 ' + size + ' ' + size + '\" width=\"' + size + '\" height=\"' + size + '\" style=\"background:#ffffff; border-radius: 8px; padding: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);\">' + rects + '</svg>';"""

text = text.replace(old_rect, new_rect)
text = text.replace(old_svg, new_svg)

with open("tools/build-index.mjs", "w", encoding="utf-8") as f:
    f.write(text)

print("Template literals cleaned in build-index.mjs")
